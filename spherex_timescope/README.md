# SPHEREx TimeScope
**Explore How the Universe Changes Over Time**

SPHEREx TimeScope is a lightweight Streamlit application for browsing public NASA SPHEREx Level 2 spectral-image files hosted in the anonymous AWS S3 bucket and comparing two selected FITS observations.

## Features
- Browse QR2 and QR3 archive folders.
- Navigate planning period → processing version → detector.
- List FITS observations and their file sizes.
- Download selected FITS files only when requested.
- Display image previews and selected FITS header metadata.
- Compare two images side by side.
- Show an exploratory pixel-difference preview when dimensions match.

## Important scientific limitation
This MVP is an archive browser and visual comparison tool. It does **not** automatically establish that two observations cover the same sky coordinates or wavelength range. A scientifically valid time-domain comparison requires WCS-based sky matching, wavelength matching, quality masking, image registration, and calibration. The difference image is explicitly labelled exploratory and must not be interpreted as a calibrated scientific result.

## Requirements
- Windows 10/11
- Python 3.10–3.13
- `uv` (recommended) or pip
- Internet connection

## Run on Windows (recommended)
1. Extract the ZIP.
2. Open the extracted folder in PowerShell.
3. Run:

```powershell
uv run --python 3.12 streamlit run app.py
```

If `uv` asks to create an environment, allow it. Alternatively:

```powershell
uv venv --python 3.12
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
uv run streamlit run app.py
```

Or double-click `run_windows.bat` if `uv` is installed and available on PATH.

Streamlit will print a local URL, usually `http://localhost:8501`. Open it in your browser.

## Data access
The application uses anonymous, read-only S3 access to:

- Bucket: `nasa-irsa-spherex`
- Region: `us-east-1`
- Prefixes: `qr2/level2/` and `qr3/level2/`

No AWS account, access key, or secret key is required. Files are downloaded only after the user selects them. A file-size safety limit is applied.

## Project structure
```text
spherex_timescope_submission/
├── app.py
├── requirements.txt
├── pyproject.toml
├── run_windows.bat
├── README.md
├── PROJECT_REPORT.md
├── .gitignore
└── data/
```

## Data citation
For QR3 data, cite DOI: https://doi.org/10.26131/IRSA662

Required acknowledgement:

> This publication makes use of data products from the Spectro-Photometer for the History of the Universe, Epoch of Reionization and Ices Explorer (SPHEREx), which is a joint project of the Jet Propulsion Laboratory and the California Institute of Technology, and is funded by the National Aeronautics and Space Administration.

For QR2 data, use DOI 10.26131/IRSA652.

## Before submitting
- Run the app on the machine and confirm the S3 archive listing works.
- Load at least two real FITS files and capture screenshots.
- Include screenshots in the final submission.
- State honestly that this version provides visual comparison, not scientifically registered time-domain analysis.
- Check the current NASA Space Apps challenge submission rules and add the team/member details requested there.
