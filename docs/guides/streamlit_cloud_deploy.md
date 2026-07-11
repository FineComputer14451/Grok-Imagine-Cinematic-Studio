# Deploy Web UI on Streamlit Community Cloud

Host the Cinematic Studio dashboard (`web_ui/app.py`) on [Streamlit Community Cloud](https://share.streamlit.io) for a public or private interactive demo.

**Studio version:** 3.8.1+ · **Entry file:** `web_ui/app.py` · **Python:** 3.12 (`runtime.txt`)

---

## Prerequisites

1. A [GitHub](https://github.com) account with access to this repository (or your fork)
2. A [Streamlit Community Cloud](https://share.streamlit.io) account (sign in with GitHub)
3. Optional: an [xAI API key](https://console.x.ai/) for live Imagine / chat (without it, the app runs in **dry-run** mode)

---

## Deploy in 5 minutes

1. Push the latest `main` (or your branch) to GitHub so these files are present:
   - `web_ui/app.py`
   - `requirements.txt` (includes `streamlit` + CLI deps)
   - `runtime.txt` → `python-3.12`
   - `.streamlit/config.toml`
2. Open [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Configure:

   | Field | Value |
   |-------|--------|
   | Repository | `FineComputer14451/Grok-Imagine-Cinematic-Studio` (or your fork) |
   | Branch | `main` (or your deploy branch) |
   | Main file path | `web_ui/app.py` |
   | App URL (optional) | e.g. `cinematic-studio` → `https://cinematic-studio.streamlit.app` |

4. Click **Deploy** and wait for the build (pip install from root `requirements.txt`).
5. Optional secrets (live API): **App settings → Secrets** → paste:

   ```toml
   XAI_API_KEY = "xai-your-key-here"
   ```

   Template: `.streamlit/secrets.toml.example`

6. Open the app URL. You should see **Dashboard** with a Community Cloud notice about ephemeral storage.

---

## What works on Cloud

| Feature | Cloud behavior |
|---------|----------------|
| Dashboard / model stack / models verify | Works (repo registry) |
| Settings model pickers | Works |
| Quota estimates | Works (session-local) |
| Guided Production Bible wizard | Works; files write under ephemeral disk |
| DNA / sequences / batches create | Works until app **reboot** (ephemeral FS) |
| Imagine live generate | Needs `XAI_API_KEY` in Secrets |
| Imagine dry-run | Default without key |
| Grok CLI plugin details | May show “not available” (no Grok CLI on Cloud) |
| NSFW page | Opt-in via Settings checkbox |

---

## Local parity

```bash
git clone https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio.git
cd Grok-Imagine-Cinematic-Studio
pip install -r requirements.txt
# optional local secrets (gitignored)
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# edit secrets.toml with your key
streamlit run web_ui/app.py
```

Key resolution order (Settings + runtime):

1. Password field in **Settings** (session)
2. Environment variable `XAI_API_KEY`
3. Streamlit secrets (`XAI_API_KEY` or `[xai] api_key`)

The Web UI copies the resolved key into `os.environ` so `tools/imagine_client.py` dry-run detection stays consistent.

---

## Secrets security

- **Never** commit `.streamlit/secrets.toml` (gitignored)
- Prefer Cloud **Secrets** UI over typing keys into the public app session
- Rotate keys if a shared demo was used with a real key in the password field
- Public apps: anyone can open the URL — treat dry-run demos as the default for public deploys

---

## Reboot / ephemeral filesystem

Streamlit Cloud may reboot the container. Runtime dirs (`characters/`, `sequences/`, `sfw_batches/`, `nsfw_batches/`, `artifacts/`) are **not durable** on Cloud unless you commit them (most are gitignored).

For lasting DNA / sequences / production state:

- Run the UI **locally** against a git clone, or
- Use the **CLI** on a machine with persistent disk, or
- Export important JSON before the Cloud app sleeps/reboots

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Build fails on `streamlit` / `openai` | Ensure root `requirements.txt` is on the deployed branch |
| `ModuleNotFoundError: lib` | Main file must be `web_ui/app.py` (not a different path) |
| `tools` import errors | Cloud must clone full repo (not a sparse sparse-checkout of `web_ui/` only) |
| Always dry-run | Add `XAI_API_KEY` under App settings → Secrets; reboot app |
| Empty DNA / sequences | Expected on fresh Cloud deploy (gitignore + ephemeral disk) |
| Theme wrong | Confirm `.streamlit/config.toml` is in the repo root path Cloud uses |

Logs: Streamlit Cloud → manage app → **Logs**.

---

## Fork deploy (recommended for personal keys)

1. Fork the repo on GitHub  
2. Deploy **your fork** on Community Cloud  
3. Put secrets only on your Cloud app  
4. Pull upstream when you want studio updates  

---

## Related

- Local UI: `README.md` → Streamlit Web UI  
- Install / plugin: `docs/guides/installation_guide.md`  
- Models: `references/MODELS.md` · `python tools/cinematic_studio_cli.py models verify`
