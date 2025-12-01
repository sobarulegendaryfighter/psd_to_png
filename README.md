# PSD2PNGExporter — Build instructions (GitHub Actions)

This repository contains a GUI script `psd2png_gui.py` and a GitHub Actions workflow that builds a Windows EXE using PyInstaller.

## How to get the built EXE (no local Python required)

1. Create a new GitHub repository (private or public).
2. Add the following files to the repo root:
   - `psd2png_gui.py`
   - `requirements.txt`
   - `.github/workflows/build-windows.yml`
   - `README.md` (optional)
3. Commit and push to GitHub (branch `main` or `master` recommended).

Example (local git commands):
```bash
git init
git add .
git commit -m "Initial commit: PSD2PNG exporter and build workflow"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
