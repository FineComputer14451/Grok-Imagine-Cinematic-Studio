"""xAI Files API CLI — list / get / upload / delete."""

from __future__ import annotations

from pathlib import Path

import typer
from rich import box
from rich.table import Table

from files_client import FilesAPIError, delete_file, get_file, list_files, upload_file
from imagine_client import is_dry_run as imagine_is_dry_run
from imagine_jobs import plate_id_from_filename, register_reference_asset

from cli.shared import console


def _force_dry(dry_run: bool) -> bool:
    return dry_run or imagine_is_dry_run()


def _print_json(payload: dict) -> None:
    console.print_json(data=payload)


def _print_file_id_hint(file_id: str) -> None:
    console.print(f"[bold green]file_id[/bold green]  {file_id}")
    console.print(
        "[dim]Next:[/dim] cinematic-studio imagine submit image_edit "
        f'-p "…" --file-id {file_id}'
    )


def register(app: typer.Typer) -> None:
    @app.command("list")
    def files_list(
        limit: int = typer.Option(20, "--limit", "-n", help="Page size"),
        order: str = typer.Option(None, "--order", help="asc | desc"),
        sort_by: str = typer.Option(
            None, "--sort-by", help="created_at | filename | size"
        ),
        pagination_token: str = typer.Option(
            None, "--pagination-token", help="Token from the previous page"
        ),
        filter_expr: str = typer.Option(
            None, "--filter", help="AIP-160 filter expression"
        ),
        json_output: bool = typer.Option(False, "--json", help="Machine-readable JSON"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Force mock response"),
    ):
        """List Files API objects (paginated metadata)."""
        try:
            result = list_files(
                limit=limit,
                order=order,
                sort_by=sort_by,
                pagination_token=pagination_token,
                filter_expr=filter_expr,
                dry_run=_force_dry(dry_run),
            )
        except FilesAPIError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
        if json_output:
            _print_json(result)
            return
        rows = list(result.get("data") or [])
        if result.get("dry_run"):
            console.print("[yellow]Dry-run[/yellow] — no live Files API call.")
        if not rows:
            console.print("[dim]No files.[/dim] Upload a plate: cinematic-studio files upload PATH")
            return
        table = Table(title="Files", box=box.ROUNDED)
        table.add_column("id", style="cyan")
        table.add_column("filename")
        table.add_column("bytes", justify="right")
        table.add_column("expires_at", style="dim")
        for row in rows:
            table.add_row(
                str(row.get("id") or ""),
                str(row.get("filename") or ""),
                str(row.get("bytes") or ""),
                str(row.get("expires_at") or "—"),
            )
        console.print(table)
        token = result.get("pagination_token")
        if token and len(rows) >= limit:
            console.print(f"[dim]Next page:[/dim] --pagination-token {token}")

    @app.command("get")
    def files_get(
        file_id: str = typer.Argument(..., help="Files API id (file_…)"),
        json_output: bool = typer.Option(False, "--json", help="Machine-readable JSON"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Force mock response"),
    ):
        """Show metadata for one stored file."""
        try:
            result = get_file(file_id, dry_run=_force_dry(dry_run))
        except FilesAPIError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
        if json_output:
            _print_json(result)
            return
        if result.get("dry_run"):
            console.print("[yellow]Dry-run[/yellow] — mock metadata.")
        console.print(f"[bold]{result.get('id')}[/bold]  {result.get('filename')}")
        console.print(f"bytes={result.get('bytes')}  expires_at={result.get('expires_at')}")
        public = result.get("public_url")
        if public:
            console.print(f"public_url={public}")

    @app.command("upload")
    def files_upload(
        path: Path = typer.Argument(..., help="Local image, video, or other file (max 50 MB)"),
        expires_after: int = typer.Option(
            None,
            "--expires-after",
            help="TTL seconds (3600–2592000). Omit = no expiry. Encoded before the file part.",
        ),
        purpose: str = typer.Option(
            "assistants",
            "--purpose",
            help="OpenAI-compat purpose label (xAI does not enforce it)",
        ),
        json_output: bool = typer.Option(False, "--json", help="Machine-readable JSON"),
        register_plate: bool = typer.Option(
            False,
            "--register-plate",
            help="Register the uploaded file_id as a reference plate",
        ),
        plate_id: str = typer.Option(
            None,
            "--plate-id",
            help="Asset id for --register-plate (default: slug from filename)",
        ),
        dry_run: bool = typer.Option(False, "--dry-run", help="Force mock response"),
    ):
        """Upload a file and print file_id for Imagine --file-id."""
        try:
            result = upload_file(
                path,
                expires_after=expires_after,
                purpose=purpose,
                dry_run=_force_dry(dry_run),
            )
        except FilesAPIError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
        fid = str(result.get("id") or "")
        if register_plate and fid:
            aid = (plate_id or "").strip() or plate_id_from_filename(
                str(result.get("filename") or path.name)
            )
            entry = register_reference_asset(
                aid,
                file_id=fid,
                notes="Files API upload",
            )
            result["plate_id"] = entry["asset_id"]
        if json_output:
            _print_json(result)
            return
        if result.get("dry_run"):
            console.print("[yellow]Dry-run[/yellow] — no live upload.")
        _print_file_id_hint(fid)
        console.print(
            f"[dim]{result.get('filename')} · {result.get('bytes')} bytes[/dim]"
        )
        if result.get("plate_id"):
            console.print(f"[green]Plate[/green] {result['plate_id']} ← {fid}")

    @app.command("delete")
    def files_delete(
        file_id: str = typer.Argument(..., help="Files API id to delete"),
        yes: bool = typer.Option(False, "--yes", "-y", help="Confirm deletion (required)"),
        json_output: bool = typer.Option(False, "--json", help="Machine-readable JSON"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Force mock response"),
    ):
        """Delete a stored file. Requires --yes."""
        if not yes:
            console.print("[red]Pass --yes to delete this file_id.[/red]")
            raise typer.Exit(1)
        try:
            result = delete_file(file_id, dry_run=_force_dry(dry_run))
        except FilesAPIError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
        if json_output:
            _print_json(result)
            return
        if result.get("dry_run"):
            console.print("[yellow]Dry-run[/yellow] — no live delete.")
        console.print(f"[green]Deleted[/green] {result.get('id')}")
