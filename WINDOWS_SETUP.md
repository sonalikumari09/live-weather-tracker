# Windows Setup Guide (for a friend, zero to running)

> For Windows 10 / 11, 64-bit. Goal: run **Know Your Weather** (`app.py`). You only need **Python + VS Code (+ Git optional)**. No Node, Docker, or database.

## What to install (overview)

| # | Software | Why this project needs it | Size |
|---|---|---|---|
| 1 | Python 3.11 (from python.org) | The app *is* Python; runs Streamlit + APIs | ~30 MB |
| 2 | VS Code + Python extension | Easiest editor + terminal to run commands | ~100 MB |
| 3 | Git (optional) | Only if copying project via `git clone`; otherwise a ZIP copy works | ~60 MB |
| 4 | Project libraries | `streamlit`, `requests`, `pandas` — installed via pip, not downloaded manually | auto |

---

## Step 1 — Install Python (most important)

1. Go to **https://www.python.org/downloads/windows/** → click **"Windows installer (64-bit)"** under the latest **Python 3.11.x** (3.11 is safest for `pandas`/`streamlit`; 3.12 also works, avoid 3.13 if anything fails).
2. Run the `.exe`. **On the very first screen, TICK ✅ "Add python.exe to PATH"** (if you miss this, `python` won't be recognized later).
3. Click **Install Now** → wait → **Close**.
4. **Check (new terminal!):** press `Win + R`, type `powershell`, Enter, then run:
   ```powershell
   python --version
   pip --version
   ```
   Expected: `Python 3.11.x` and `pip 24.x ...`. If `python` says "not recognized", either reopen the terminal or use `py --version` / `py -m pip --version` instead (the `py` launcher always works on Windows).

## Step 2 — Install VS Code + Python extension

1. Go to **https://code.visualstudio.com/** → **Download for Windows** → install with all defaults.
2. Open VS Code → left sidebar **Extensions** (Ctrl+Shift+X) → search **"Python"** by Microsoft → **Install**.
3. **Check:** in VS Code open a terminal (`Ctrl + `` ` ``) and run `python --version` again — same version as Step 1 should appear.

## Step 3 — Install Git (optional, pick ONE way to get the project)

- **Option A (no Git):** copy the project folder (`app.py, geo.py, weather.py, i18n.py, ui_effects.py, requirements.txt, *.md`) via ZIP/USB into e.g. `C:\Users\HerName\weather\`.
- **Option B (with Git):** install from **https://git-scm.com/download/win** (defaults), then:
  ```powershell
  git --version
  git clone <your-repo-url>
  cd <project-folder>
  ```
- **Check:** folder must contain `app.py` + `requirements.txt`. In VS Code: **File → Open Folder** → select it.

## Step 4 — Create a virtual environment (keeps libraries tidy)

In the project folder terminal (VS Code terminal or PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

- Prompt should now start with `(.venv)`.
- If PowerShell blocks it (`cannot be loaded because running scripts is disabled`), run once:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
  then activate again. (CMD alternative: `.\.venv\Scripts\activate.bat`.)
- **Check:** `where python` should point inside `.venv\Scripts\python.exe`.

## Step 5 — Install project libraries

```powershell
pip install -r requirements.txt
```

**Check each one:**
```powershell
pip show streamlit requests pandas
python -c "import streamlit, pandas, requests; print('all ok')"
```
Expected: versions printed, `all ok`. This project needs only these 3 — if someone tells her to install Node/Docker/MySQL, she can skip it.

## Step 6 — Run the website

```powershell
streamlit run app.py --server.port 8501
```

- First run may take ~30 s (pandas loads). Browser should open automatically; if not, open **http://localhost:8501** manually.
- **Test:** type `843301`, press **Enter** → should show Dumra, Sitamarhi. Try `Bajpatti, Sitamarhi`.
- Stop anytime with **Ctrl+C**. Re-run with the same command (activate `.venv` first if terminal was closed).

## Step 7 — Quick fault table (Windows-only gotchas)

| Symptom | Fix |
|---|---|
| `python is not recognized` | PATH missed → reinstall Python with "Add to PATH" ticked, or use `py` instead of `python` |
| `pip is not recognized` | `py -m pip install -r requirements.txt` |
| `Activate.ps1 cannot be loaded` | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`, retry |
| `Port 8501 is already in use` | Old app still running → close other terminal, or `streamlit run app.py --server.port 8502` |
| Browser shows "No internet / server error" | Wi-Fi off or API blocked → reconnect, retry (office firewalls sometimes block `api.open-meteo.com`) |
| Hindi/Bhojpuri shows boxes `□□` | Install a Devanagari font (Windows usually has Mangal/Nirmala UI; Windows Update fixes it) |

## One-line recheck (copy-paste anytime)

```powershell
python --version; pip --version; python -c "import streamlit, pandas, requests; print('ready')"
```

If all three print without red errors, her laptop is ready for this project.
