# Connected GitHub Tools Catalog (v4.5)

**Model-aware usage (v4.5):** Prefer `grok-4-auto` for listing/status, `grok-v9-4p5-chat-expert` for deep analysis & PR bodies, `grok-v9-4p5-multi` for multi-step release orchestration.

This reference lists all discovered `github___*` tools available via `call_connected_tool`. Use the exact `tool_name` and match the JSON schema for `arguments`.

**Core pattern**:
```json
{
  "tool_name": "github___tool-name-here",
  "arguments": { ... exact schema below ... }
}
```

## Repository Management
- **github___create_repository** — Create new repo (personal or org)
  - Required: `name`
  - Optional: `description`, `private` (bool), `autoInit` (bool), `organization`

- **github___fork_repository** — Fork repo to your account/org
  - Required: `owner`, `repo`
  - Optional: `organization`

- **github___search_repositories** — Powerful search (use for listing your repos)
  - Required: `query` (supports `user:login`, `org:`, `is:private`, `language:`, `topic:`, stars:>N, etc.)
  - Optional: `sort` (stars|forks|updated|help-wanted-issues), `order` (asc|desc), `perPage`, `page`, `minimal_output`

## File Operations
- **github___create_or_update_file** — Create or update single file
  - Required: `owner`, `repo`, `path`, `content`, `message`, `branch`
  - Optional: `sha` (required for updates — obtain via `git rev-parse branch:path` or prior read)

- **github___push_files** — Bulk push multiple files in one commit (ideal for bootstrap)
  - Required: `owner`, `repo`, `branch`, `message`, `files` (array of `{path, content}`)

- **github___delete_file** — Delete a file
  - Required: `owner`, `repo`, `path`, `message`, `branch`

## Branches
- **github___list_branches**
  - Required: `owner`, `repo`
  - Optional: `page`, `perPage`

- **github___create_branch**
  - Required: `owner`, `repo`, `branch`
  - Optional: `from_branch` (defaults to repo default)

## Issues
- **github___issue_write** — Create or update issue
  - Required: `method` ("create"|"update"), `owner`, `repo`
  - Optional: `title`, `body`, `labels` (array), `assignees` (array), `milestone`, `state` ("open"|"closed"), `state_reason`, `duplicate_of`, `type`

- **github___issue_read**
  - Required: `method` ("get"|"get_comments"|"get_sub_issues"|"get_labels"), `owner`, `repo`, `issue_number`
  - Optional: `page`, `perPage`

- **github___add_issue_comment**
  - Required: `owner`, `repo`, `issue_number`, `body`

- **github___sub_issue_write** — Parent-child issue relationships
  - Required: `method` ("add"|"remove"|"reprioritize"), `owner`, `repo`, `issue_number`, `sub_issue_id`
  - Optional: `before_id`/`after_id`, `replace_parent`

- **github___search_issues** — Advanced issue search (scoped to `is:issue`)
  - Required: `query`
  - Optional: `owner`/`repo` (to scope), `sort`, `order`, `page`, `perPage`

## Pull Requests
- **github___create_pull_request**
  - Required: `owner`, `repo`, `title`, `head`, `base`
  - Optional: `body`, `draft` (bool), `maintainer_can_modify` (bool)

- **github___list_pull_requests**
  - Required: `owner`, `repo`
  - Optional: `state` ("open"|"closed"|"all"), `head`, `base`, `sort`, `direction`, `page`, `perPage`

- **github___search_pull_requests** — Advanced PR search (scoped to `is:pr`)
  - Required: `query`
  - Optional: `owner`/`repo`, `sort`, `order`, `page`, `perPage`

- **github___pull_request_read**
  - Required: `method` ("get" | "get_diff" | "get_status" | "get_files" | "get_review_comments" | "get_reviews" | "get_comments" | "get_check_runs"), `owner`, `repo`, `pullNumber`
  - Optional: `page`, `perPage`, `after` (cursor for threads)

- **github___update_pull_request**
  - Required: `owner`, `repo`, `pullNumber`
  - Optional: `title`, `body`, `state`, `base`, `draft`, `reviewers` (array), `maintainer_can_modify`

- **github___pull_request_review_write**
  - Required: `method` ("create"|"submit_pending"|"delete_pending"|"resolve_thread"|"unresolve_thread"), `owner`, `repo`, `pullNumber`
  - Optional: `body`, `event` ("APPROVE"|"REQUEST_CHANGES"|"COMMENT"), `commitID`, `threadId`

- **github___update_pull_request_branch** — Sync PR branch with base
  - Required: `owner`, `repo`, `pullNumber`
  - Optional: `expectedHeadSha`

- **github___merge_pull_request**
  - Required: `owner`, `repo`, `pullNumber`
  - Optional: `merge_method` ("merge"|"squash"|"rebase"), `commit_title`, `commit_message`

## Commits, Releases, Tags
- **github___get_commit**
  - Required: `owner`, `repo`, `sha` (SHA, branch, or tag)
  - Optional: `include_diff` (bool, default true), `page`, `perPage`

- **github___search_commits**
  - Required: `query` (supports `repo:`, `author:`, `committer-date:>=YYYY-MM-DD`, etc.)
  - Optional: `sort` ("author-date"|"committer-date"), `order`, `page`, `perPage`

- **github___list_releases**
  - Required: `owner`, `repo`
  - Optional: `page`, `perPage`

- **github___list_tags**
  - Required: `owner`, `repo`
  - Optional: `page`, `perPage`

## Other
- **github___list_issue_types** — For orgs with custom issue types
  - Required: `owner` (org)

- **github___search_code** — Fast code search across all GitHub
  - Required: `query` (supports `repo:`, `path:`, `extension:`, `language:`, `size:`, `is:archived`, etc.)
  - Optional: `sort`, `order`, `page`, `perPage`

**Notes**:
- All tools support standard pagination (`page`, `perPage`).
- Owner can be username or organization.
- For your personal account, always start with `github___get_me` to get exact `login`.
- New tools may appear — re-run `search_connected_tools` with query "github" if needed.
- Destructive actions (delete, merge, close) should be confirmed with the user first.

Last updated: 2026-07-20 (v4.5 model routing + comprehensive coverage of available connected tools).
