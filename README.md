# 🌌 SPHEREx TimeScope

**Explore NASA SPHEREx infrared observations, inspect FITS data, and ask questions using AI.**

SPHEREx TimeScope is a student-built educational web application designed to make publicly available NASA SPHEREx Level 2 archive data easier to explore and understand.

## Features

- Browse public SPHEREx QR2 and QR3 archive data.
- Explore planning periods, processing versions, and detector folders.
- View and download FITS observation files.
- Preview astronomical images and inspect observation metadata.
- Compare two selected observations.
- Generate exploratory pixel-difference previews when image dimensions match.
- Ask questions about observations and astronomy using an AI-powered assistant.
- Retrieve relevant reference information for AI-generated answers.

## Technology Stack

- Python
- Streamlit
- Boto3
- Astropy
- NumPy and Pandas
- Matplotlib
- Ollama
- Qwen3:4b — language model
- BGE-M3 — embedding model

## NASA Data Sources

The application uses publicly available SPHEREx data hosted by NASA/IPAC IRSA.

- **AWS S3 Bucket:** `nasa-irsa-spherex`
- **Region:** `us-east-1`
- **Dataset DOI:** [10.26131/IRSA662](https://doi.org/10.26131/IRSA662)
- **Public Archive:** https://nasa-irsa-spherex.s3.amazonaws.com/
- **Documentation:** https://caltech-ipac.github.io/spherex-archive-documentation/

## Screenshots

**Dashboard**
<img width="1477" height="877" alt="image" src="https://github.com/user-attachments/assets/b5ad4494-8d78-4bf7-8863-739408605271" />

**FITS Image Explorer**
<img width="1087" height="531" alt="image" src="https://github.com/user-attachments/assets/f299be5c-d53d-4eb1-ba39-a9a09beb85dd" />

**Observation Comparison**
<img width="833" height="747" alt="image" src="https://github.com/user-attachments/assets/5f451af8-c4b0-49f8-b1a2-efc1985d659a" />
<img width="840" height="877" alt="image" src="https://github.com/user-attachments/assets/8253bb18-df17-4e7c-862a-90d7392cfaf8" />

**AI Assistant**
<img width="837" height="855" alt="image" src="https://github.com/user-attachments/assets/bb362f61-166a-43cd-b653-6fbd6d445b1c" />
<img width="792" height="953" alt="image" src="https://github.com/user-attachments/assets/745e9416-68e0-4740-b146-f3cb5ce93f33" />
<img width="825" height="991" alt="image" src="https://github.com/user-attachments/assets/5aaf0f99-9e12-4d23-a5b0-960583238d71" />




## Installation

### 1. Clone the repository

```bash
git clone https://github.com/subanaash/spherex-timescope.git
cd spherex-timescope
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up Ollama

Install Ollama from https://ollama.com/

Download the required models:

```bash
ollama pull qwen3:4b
ollama pull bge-m3
```

Make sure Ollama is running locally at:

`http://localhost:11434`

### 5. Run the application

```bash
python -m streamlit run app.py
```

Open the local URL displayed in your terminal, usually:

`http://localhost:8501`

## Scientific Limitations

SPHEREx TimeScope is an educational exploration prototype, not a scientific analysis pipeline.

The pixel-difference preview is exploratory and is not automatically WCS-aligned, wavelength-matched, masked, or scientifically calibrated. Matching image dimensions alone does not establish that two observations are scientifically comparable.

AI-generated explanations should be checked against official archive documentation and scientific sources.

## Acknowledgement

This project uses publicly available SPHEREx data products from the Spectro-Photometer for the History of the Universe, Epoch of Reionization and Ices Explorer (SPHEREx), a joint project of the Jet Propulsion Laboratory and the California Institute of Technology, funded by NASA.

---

**Project:** SPHEREx TimeScope  
**Status:** Educational Prototype  
**Built for:** NASA Space Apps Challenge 2026
