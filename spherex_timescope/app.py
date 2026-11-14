from __future__ import annotations

import io
import html
import traceback
import textwrap
from typing import Any
import requests

import boto3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from astropy.io import fits
from botocore import UNSIGNED
from botocore.config import Config


# =========================================================
# CONFIGURATION
# =========================================================

BUCKET = "nasa-irsa-spherex"
REGION = "us-east-1"

RELEASES = {
    "QR3": "qr3",
    "QR2": "qr2",
}

MAX_FITS_MB = 180

OLLAMA_URL = "http://localhost:11434"
CHAT_MODEL = "qwen3:4b"
EMBED_MODEL = "bge-m3:latest"

NASA_KNOWLEDGE = [
    {
        "text": """
        SPHEREx is a NASA space telescope mission that performs
        an all-sky spectral survey in the near-infrared.
        Its observations provide information across multiple
        wavelength bands.
        """,
        "source": "NASA SPHEREx mission information",
        "url": "https://science.nasa.gov/mission/spherex/",
    },
    {
        "text": """
        FITS means Flexible Image Transport System. FITS files
        can contain image arrays, tables, and metadata headers.
        A FITS file can contain multiple Header Data Units (HDUs).
        """,
        "source": "Astropy FITS documentation",
        "url": "https://docs.astropy.org/en/stable/io/fits/",
    },
    {
        "text": """
        FITS headers contain keyword-value pairs describing
        information about the data. Common astronomical keywords
        include DATE-OBS, RA, DEC, CRVAL1, CRVAL2, and OBJECT.
        The meaning of a keyword depends on the data product.
        """,
        "source": "FITS and astronomical data documentation",
        "url": "https://docs.astropy.org/en/stable/io/fits/",
    },
    {
        "text": """
        Right Ascension (RA) and Declination (DEC) describe
        positions on the celestial coordinate system. RA is
        analogous to longitude and DEC is analogous to latitude.
        """,
        "source": "NASA/IPAC Infrared Science Archive",
        "url": "https://irsa.ipac.caltech.edu/",
    },
    {
        "text": """
        An image array contains numerical pixel values.
        Image dimensions describe the number of pixels along
        each axis. Pixel values should not automatically be
        interpreted as calibrated physical measurements.
        """,
        "source": "Astropy FITS documentation",
        "url": "https://docs.astropy.org/en/stable/io/fits/",
    },
    {
        "text": """
        Comparing astronomical images requires care. Images
        should be checked for sky position, wavelength coverage,
        calibration, masks, and image registration before
        interpreting pixel differences scientifically.
        """,
        "source": "SPHEREx archive documentation",
        "url": "https://caltech-ipac.github.io/spherex-archive-documentation/",
    },
]

st.set_page_config(
    page_title="SPHEREx TimeScope",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# UI THEME
# =========================================================

st.markdown("""
<style>

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #081525 !important;
    color: #EAF4FF !important;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4 {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

/* Form labels */
.stApp label,
.stApp [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stWidgetLabel"] label {
    color: #DCEBFA !important;
    opacity: 1 !important;
}

.stMarkdown p,
.stMarkdown li,
[data-testid="stCaptionContainer"] {
    color: #DCEBFA !important;
}

[data-testid="stSidebar"] {
    background: #10243B !important;
    border-right: 1px solid #294863;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] label {
    color: #DCEBFA !important;
}

/* Select boxes */

[data-baseweb="select"] > div {
    background: #F4F7FB !important;
    border: 1px solid #45BFE0 !important;
    border-radius: 8px !important;
    min-height: 42px;
}

[data-baseweb="select"] span,
[data-baseweb="select"] input {
    color: #10243B !important;
    -webkit-text-fill-color: #10243B !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"] {
    background: #F4F7FB !important;
}

[role="option"],
[role="option"] * {
    background: #F4F7FB !important;
    color: #10243B !important;
    -webkit-text-fill-color: #10243B !important;
}

[role="option"]:hover {
    background: #D9F1FA !important;
}

/* Buttons */

.stButton button {
    background: #087FA5 !important;
    color: #FFFFFF !important;
    border: 1px solid #27BCE0 !important;
    border-radius: 9px !important;
    font-weight: 600;
    padding: .55rem 1rem;
}

.stButton button:hover {
    background: #0999C2 !important;
    border-color: #73E5FF !important;
}

/* Streamlit Navigation Tabs */

.stTabs button[role="tab"] {
    color: #FFFFFF !important;
    opacity: 1 !important;
    font-weight: 700 !important;
}

.stTabs button[role="tab"] p {
    color: #FFFFFF !important;
    opacity: 1 !important;
}

/* Emoji and text */
.stTabs button[role="tab"] span {
    color: #FFFFFF !important;
    opacity: 1 !important;
}

/* Selected tab */
.stTabs button[role="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
    border-bottom: 3px solid #45D6F5 !important;
}

/* Selected tab text */
.stTabs button[role="tab"][aria-selected="true"] p {
    color: #FFFFFF !important;
}
/* Hero section */

.hero {
    padding: 1.8rem 2rem;
    border: 1px solid #27617E;
    border-radius: 16px;
    background: linear-gradient(110deg, #12304C, #124B64);
    margin-bottom: 1.3rem;
}

.hero h1 {
    color: #FFFFFF !important;
    margin: 0;
    font-size: 2.3rem;
}

.hero p {
    color: #C7F1FF !important;
    margin-top: .6rem;
    font-size: 1.05rem;
}

.small-note {
    color: #A9C2D8 !important;
    font-size: .88rem;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# CUSTOM HTML TABLE
# Avoids PyArrow dependency
# =========================================================

def display_table(df: pd.DataFrame) -> None:

    headers = "".join(
        f"""
        <th style="
            padding:12px;
            text-align:left;
            background:#17415D;
            color:#FFFFFF;
            border-bottom:1px solid #45617A;
        ">{html.escape(str(col))}</th>
        """
        for col in df.columns
    )

    rows = ""

    for _, row in df.iterrows():

        cells = "".join(
            f"""
            <td style="
                padding:11px;
                color:#EAF4FF;
                border-bottom:1px solid #294863;
                overflow-wrap:anywhere;
            ">{html.escape(str(value))}</td>
            """
            for value in row
        )

        rows += f"<tr>{cells}</tr>"

    table_html = f"""
    <div style="
        overflow-x:auto;
        border:1px solid #35516E;
        border-radius:10px;
        margin:12px 0;
    ">
        <table style="
            width:100%;
            border-collapse:collapse;
            background:#10243B;
            font-size:13px;
        ">
            <thead>
                <tr>{headers}</tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    """

    # IMPORTANT: Remove indentation before rendering HTML.
    # This prevents Streamlit from displaying it as a code block.
    st.components.v1.html(
    table_html,
    height=min(520, max(180, 55 + len(df) * 42)),
    scrolling=True
)


# =========================================================
# AWS CONNECTION
# =========================================================

@st.cache_resource
def s3_client():

    return boto3.client(
        "s3",
        region_name=REGION,
        config=Config(
            signature_version=UNSIGNED,
            retries={"max_attempts": 3},
        ),
    )


# =========================================================
# ARCHIVE FUNCTIONS
# =========================================================

def list_prefixes(prefix: str) -> list[str]:

    paginator = s3_client().get_paginator(
        "list_objects_v2"
    )

    found = []

    for page in paginator.paginate(
        Bucket=BUCKET,
        Prefix=prefix,
        Delimiter="/",
    ):

        found.extend(
            item["Prefix"]
            for item in page.get("CommonPrefixes", [])
        )

    return sorted(found)


def list_fits(
    prefix: str,
    limit: int = 5000,
) -> list[dict[str, Any]]:

    paginator = s3_client().get_paginator(
        "list_objects_v2"
    )

    rows = []

    for page in paginator.paginate(
        Bucket=BUCKET,
        Prefix=prefix,
    ):

        for item in page.get("Contents", []):

            key = item["Key"]

            if key.lower().endswith(
                (".fits", ".fits.gz", ".fit")
            ):

                rows.append({
                    "key": key,
                    "size": item["Size"],
                    "modified": item["LastModified"],
                })

                if len(rows) >= limit:
                    return rows

    return rows


def download_fits(key: str) -> bytes:

    response = s3_client().get_object(
        Bucket=BUCKET,
        Key=key,
    )

    size = response.get("ContentLength", 0)

    if size > MAX_FITS_MB * 1024 * 1024:

        raise ValueError(
            f"File exceeds the {MAX_FITS_MB} MB safety limit."
        )

    return response["Body"].read()

# =========================================================
# FITS IMAGE AND METADATA FUNCTIONS
# =========================================================

def first_value(
    header: fits.Header,
    keys: list[str],
) -> str:

    for key in keys:

        value = header.get(key)

        if value is not None:
            return str(value)

    return "Not recorded in selected header"


def read_image(
    payload: bytes,
) -> tuple[np.ndarray, fits.Header, str, dict[str, Any]]:

    with fits.open(
        io.BytesIO(payload),
        memmap=False,
    ) as hdul:

        chosen = None
        chosen_name = ""

        for hdu in hdul:

            if (
                hdu.data is not None
                and getattr(hdu.data, "ndim", 0) >= 2
            ):

                if hdu.name.upper() == "IMAGE":

                    chosen = hdu
                    chosen_name = hdu.name
                    break

                if chosen is None:

                    chosen = hdu
                    chosen_name = hdu.name

        if chosen is None:

            raise ValueError(
                "No 2D image extension was found."
            )

        data = np.asarray(
            chosen.data,
            dtype=np.float32,
        )

        header = chosen.header.copy()
        primary = hdul[0].header.copy()

        for key in (
            "DATE-OBS",
            "DATE-BEG",
            "DATE-AVG",
            "MJD-OBS",
            "RA",
            "DEC",
            "OBJECT",
            "OBSID",
            "BAND",
            "DETECTOR",
        ):

            if key not in header and key in primary:
                header[key] = primary[key]

        metadata = {

            "Date": first_value(
                header,
                ["DATE-AVG", "DATE-BEG", "DATE-OBS", "DATE"],
            ),

            "Right Ascension": first_value(
                header,
                ["RA", "CRVAL1"],
            ),

            "Declination": first_value(
                header,
                ["DEC", "CRVAL2"],
            ),

            "Object": first_value(
                header,
                ["OBJECT", "TARGNAME"],
            ),

            "Observation ID": first_value(
                header,
                ["OBSID", "OBS_ID"],
            ),

            "Band / Detector": first_value(
                header,
                ["BAND", "DETECTOR"],
            ),

            "Image dimensions": (
                f"{data.shape[1]} × {data.shape[0]}"
            ),

            "Image extension": chosen_name,
        }

    return data, header, chosen_name, metadata


def metadata_table(
    meta: dict[str, Any],
) -> pd.DataFrame:

    return pd.DataFrame({
        "Property": list(meta.keys()),
        "Value": list(meta.values()),
    })

# =========================================================
# LOCAL AI + RAG FUNCTIONS
# =========================================================

def ollama_request(endpoint, payload):
    try:
        response = requests.post(
            f"{OLLAMA_URL}{endpoint}",
            json=payload,
            timeout=300
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        raise RuntimeError(
            "Ollama is taking too long. "
            "Please wait for the model to load and try again."
        )

    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Cannot connect to Ollama. "
            "Make sure Ollama is running."
        )

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Ollama request failed: {e}")


def create_embedding(text: str) -> np.ndarray:

    result = ollama_request(
        "/api/embed",
        {
            "model": EMBED_MODEL,
            "input": text,
        },
    )

    embeddings = result.get("embeddings")

    if not embeddings:
        raise RuntimeError(
            "Ollama did not return an embedding."
        )

    vector = np.asarray(
        embeddings[0],
        dtype=np.float32,
    )

    norm = np.linalg.norm(vector)

    if norm == 0:
        raise RuntimeError("Invalid zero-length embedding.")

    return vector / norm


@st.cache_data(show_spinner=False)
def get_knowledge_embeddings() -> np.ndarray:

    texts = [
        item["text"]
        for item in NASA_KNOWLEDGE
    ]

    result = ollama_request(
        "/api/embed",
        {
            "model": EMBED_MODEL,
            "input": texts,
        },
    )

    embeddings = np.asarray(
        result["embeddings"],
        dtype=np.float32,
    )

    norms = np.linalg.norm(
        embeddings,
        axis=1,
        keepdims=True,
    )

    return embeddings / np.maximum(norms, 1e-12)


def retrieve_knowledge(
    question: str,
    top_k: int = 3,
) -> list[dict]:

    query_vector = create_embedding(question)

    document_vectors = get_knowledge_embeddings()

    scores = document_vectors @ query_vector

    indexes = np.argsort(scores)[::-1][:top_k]

    return [
        {
            **NASA_KNOWLEDGE[int(index)],
            "score": float(scores[index]),
        }
        for index in indexes
    ]


def generate_ai_answer(
    question: str,
    observation_context: str,
) -> tuple[str, list[dict]]:

    retrieved = retrieve_knowledge(question)

    reference_context = "\n\n".join(
        f"Source: {item['source']}\n"
        f"Information: {item['text']}"
        for item in retrieved
    )

    prompt = f"""
You are the SPHEREx TimeScope AI Observation Assistant.

Your purpose is to help users understand SPHEREx observations,
FITS metadata, and general astronomical data concepts.

IMPORTANT RULES:
1. Use the selected observation context and retrieved references.
2. Never invent FITS metadata or observation values.
3. Clearly distinguish actual observation metadata from
   general background information.
4. If information is missing, say it is not available.
5. Do not claim that an image difference is scientifically
   valid merely because two arrays have matching dimensions.
6. Do not claim to perform scientific image interpretation.
7. Explain technical concepts in beginner-friendly language.
8. If the context does not support an answer, say so.

SELECTED OBSERVATION CONTEXT:
{observation_context}

RETRIEVED REFERENCE INFORMATION:
{reference_context}

USER QUESTION:
{question}

Answer clearly and concisely.
"""

    result = ollama_request(
        "/api/chat",
        {
            "model": CHAT_MODEL,
            "stream": False,
            "think": False,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "options": {
                "temperature": 0.2,
            },
        },
    )

    answer = result.get(
        "message", {}
    ).get("content", "").strip()

    if not answer:
        raise RuntimeError(
            "The AI model returned an empty response."
        )

    return answer, retrieved


def build_observation_context(
    metadata: dict,
    filename: str,
    header: fits.Header,
) -> str:

    metadata_text = "\n".join(
        f"{key}: {value}"
        for key, value in metadata.items()
    )

    header_lines = []

    for key, value in header.items():

        if key in ("COMMENT", "HISTORY"):
            continue

        if isinstance(value, (str, int, float, bool)):
            header_lines.append(
                f"{key}: {value}"
            )

        if len(header_lines) >= 50:
            break

    return f"""
Selected FITS filename: {filename}

Extracted metadata:
{metadata_text}

Selected FITS header entries:
{chr(10).join(header_lines)}
"""
# =========================================================
# IMAGE DISPLAY
# =========================================================

def display_image(
    data: np.ndarray,
    title: str,
) -> None:

    finite = data[np.isfinite(data)]

    if finite.size == 0:

        st.warning(
            f"{title}: no finite image pixels found."
        )
        return

    lo, hi = np.nanpercentile(
        finite,
        [2, 98],
    )

    if (
        not np.isfinite(lo)
        or not np.isfinite(hi)
        or lo == hi
    ):

        lo = np.nanmin(finite)
        hi = np.nanmax(finite) + 1e-9

    fig, ax = plt.subplots(figsize=(7, 6))

    fig.patch.set_facecolor("#10243B")
    ax.set_facecolor("#10243B")

    ax.imshow(
        data,
        origin="lower",
        cmap="inferno",
        vmin=lo,
        vmax=hi,
    )

    ax.set_title(title, color="white")
    ax.set_xlabel("Pixel", color="white")
    ax.set_ylabel("Pixel", color="white")
    ax.tick_params(colors="white")

    fig.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True,
    )

    plt.close(fig)


# =========================================================
# HEADER
# =========================================================

st.components.v1.html(
    """
    <div style="
        background: linear-gradient(135deg, #123B56, #0B263D);
        border: 1px solid #26718A;
        border-radius: 16px;
        padding: 30px 34px;
        font-family: Arial, sans-serif;
        color: #FFFFFF;
    ">
        <div style="
            font-size: 30px;
            font-weight: 700;
            margin-bottom: 14px;
        ">
            🌌 SPHEREx TimeScope
        </div>

        <div style="
            font-size: 16px;
            line-height: 1.8;
            color: #D5EAF5;
        ">
            Explore infrared observations.<br>
            Compare real SPHEREx images across observing periods.
        </div>
    </div>
    """,
    height=175,
    scrolling=False,
)

st.caption(
    "A student-built exploration interface for publicly "
    "available NASA SPHEREx Level 2 data."
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("Data Source")

    release_label = st.selectbox(
        "Data Release",
        list(RELEASES.keys()),
        index=0,
    )

    release = RELEASES[release_label]

    st.caption(
        f"Public AWS bucket: s3://{BUCKET}/{release}/"
    )

    st.divider()

    st.header("How to Use")

    st.markdown("""
    1. Choose a data release.
    2. Select a planning period.
    3. Choose a processing version and detector.
    4. Browse available FITS files.
    5. Compare two observations.
    """)

    st.caption(
        "Files are downloaded only when selected."
    )


# =========================================================
# NAVIGATION TABS
# =========================================================

tab_explore, tab_compare, tab_ai, tab_about = st.tabs([
    "🛰️ Explore Archive",
    "🔭 Compare Observations",
    "🤖 AI Assistant",
    "ℹ️ About",
])

# =========================================================
# TAB 1: EXPLORE ARCHIVE
# =========================================================

with tab_explore:

    st.subheader(
        "Browse SPHEREx Level 2 Observations"
    )

    st.write(
        "Explore available SPHEREx observations "
        "by planning period, processing version, and detector."
    )

    try:

        planning_prefixes = list_prefixes(
            f"{release}/level2/"
        )

        planning_names = [
            p.rstrip("/").split("/")[-1]
            for p in planning_prefixes
        ]

        if not planning_names:

            st.warning(
                "No planning-period folders were returned."
            )

        else:

            period = st.selectbox(
                "Weekly Planning Period",
                planning_names,
            )

            period_prefix = (
                f"{release}/level2/{period}/"
            )

            version_names = [
                p.rstrip("/").split("/")[-1]
                for p in list_prefixes(period_prefix)
            ]

            if not version_names:

                st.warning(
                    "No processing versions were found."
                )

            else:

                version = st.selectbox(
                    "Processing Version",
                    version_names,
                )

                version_prefix = (
                    f"{period_prefix}{version}/"
                )

                detector_names = [
                    p.rstrip("/").split("/")[-1]
                    for p in list_prefixes(version_prefix)
                ]

                if not detector_names:

                    st.warning(
                        "No detector folders were found."
                    )

                else:

                    detector = st.selectbox(
                        "Detector / Spectral Band",
                        detector_names,
                    )

                    fits_prefix = (
                        f"{version_prefix}{detector}/"
                    )

                    with st.spinner(
                        "Loading files from NASA's public archive..."
                    ):

                        fits_rows = list_fits(fits_prefix)

                    if fits_rows:

                        df = pd.DataFrame(fits_rows)

                        df["size_mb"] = (
                            df["size"] / (1024 * 1024)
                        ).round(2)

                        df["modified"] = (
                            pd.to_datetime(df["modified"])
                            .dt.strftime("%Y-%m-%d %H:%M UTC")
                        )

                        st.success(
                            f"Found {len(df)} FITS file(s) in this folder."
                        )

                        display_table(
                            df[
                                ["key", "size_mb", "modified"]
                            ]
                        )

                        st.caption(
                            "Files are listed from the selected "
                            "detector folder. They may not all "
                            "represent the same sky position."
                        )

                    else:

                        st.info(
                            "No FITS files were found in this folder."
                        )

    except Exception:

        st.error(
            "Could not browse the public S3 archive."
        )

        st.code(traceback.format_exc())

        st.info(
            "The app uses anonymous read-only access. "
            "No AWS account or credentials are required."
        )


# =========================================================
# TAB 2: COMPARE OBSERVATIONS
# =========================================================

with tab_compare:

    st.subheader(
        "Compare Two SPHEREx Observations"
    )

    st.write(
        "Select two FITS files to inspect their image previews "
        "and available metadata."
    )

    try:

        periods = [
            p.rstrip("/").split("/")[-1]
            for p in list_prefixes(
                f"{release}/level2/"
            )
        ]

        if not periods:

            st.warning(
                "No planning periods are currently available."
            )

        else:

            col1, col2 = st.columns(2)

            with col1:

                period_a = st.selectbox(
                    "Planning Period",
                    periods,
                    key="cmp_period",
                )

            versions = [
                p.rstrip("/").split("/")[-1]
                for p in list_prefixes(
                    f"{release}/level2/{period_a}/"
                )
            ]

            if versions:

                version_a = st.selectbox(
                    "Processing Version",
                    versions,
                    key="cmp_version",
                )

                detectors = [
                    p.rstrip("/").split("/")[-1]
                    for p in list_prefixes(
                        f"{release}/level2/"
                        f"{period_a}/{version_a}/"
                    )
                ]

            else:

                detectors = []

            if detectors:

                detector_a = st.selectbox(
                    "Detector",
                    detectors,
                    key="cmp_detector",
                )

                prefix_a = (
                    f"{release}/level2/{period_a}/"
                    f"{version_a}/{detector_a}/"
                )

                with st.spinner(
                    "Loading available FITS files..."
                ):

                    files_a = list_fits(prefix_a)

                if len(files_a) >= 2:

                    options = [
                        item["key"]
                        for item in files_a
                    ]

                    with col1:

                        file_a = st.selectbox(
                            "Observation A",
                            options,
                            format_func=lambda x: x.split("/")[-1],
                        )

                    with col2:

                        file_b = st.selectbox(
                            "Observation B",
                            options,
                            index=1,
                            format_func=lambda x: x.split("/")[-1],
                        )

                    if st.button(
                        "Load and Compare Observations",
                        type="primary",
                        use_container_width=True,
                    ):

                        if file_a == file_b:

                            st.warning(
                                "Please select two different FITS files."
                            )

                        else:

                            with st.spinner(
                                "Downloading and reading FITS files..."
                            ):

                                bytes_a = download_fits(file_a)
                                bytes_b = download_fits(file_b)

                                data_a, _, _, meta_a = read_image(
                                    bytes_a
                                )

                                data_b, _, _, meta_b = read_image(
                                    bytes_b
                                )

                            st.session_state["comparison"] = {

                                "a": (
                                    data_a,
                                    meta_a,
                                    file_a,
                                ),

                                "b": (
                                    data_b,
                                    meta_b,
                                    file_b,
                                ),
                            }

                elif files_a:

                    st.info(
                        "Only one FITS file was found. "
                        "Two files are needed for comparison."
                    )

                else:

                    st.info(
                        "No FITS files were found."
                    )

            else:

                st.info(
                    "No processing-version or detector folders found."
                )

    except Exception:

        st.error(
            "Could not load the observation list or FITS data."
        )

        st.code(traceback.format_exc())


    # Display loaded comparison

    comparison = st.session_state.get("comparison")

    if comparison:

        data_a, meta_a, key_a = comparison["a"]
        data_b, meta_b, key_b = comparison["b"]

        st.divider()

        st.markdown("### Observation Previews")

        left, right = st.columns(2)

        with left:

            st.markdown("**Observation A**")

            st.caption(
                key_a.split("/")[-1]
            )

            display_image(
                data_a,
                "SPHEREx Observation A",
            )

            display_table(
                metadata_table(meta_a)
            )

        with right:

            st.markdown("**Observation B**")

            st.caption(
                key_b.split("/")[-1]
            )

            display_image(
                data_b,
                "SPHEREx Observation B",
            )

            display_table(
                metadata_table(meta_b)
            )

        st.markdown("### Comparison Checks")

        date_a = meta_a["Date"]
        date_b = meta_b["Date"]

        missing_date = "Not recorded in selected header"

        if (
            date_a != missing_date
            and date_b != missing_date
        ):

            if date_a != date_b:

                st.success(
                    f"Different observation times reported: "
                    f"{date_a} and {date_b}."
                )

            else:

                st.warning(
                    "The selected FITS headers report "
                    "the same observation time."
                )

        else:

            st.info(
                "A recognized observation-time keyword "
                "was not found in one or both headers."
            )

        if data_a.shape == data_b.shape:

            st.info(
                "The images have matching pixel dimensions. "
                "The following pixel difference is exploratory only. "
                "It is not a scientifically registered difference image."
            )

            finite = (
                np.isfinite(data_a)
                & np.isfinite(data_b)
            )

            if finite.any():

                difference = np.full(
                    data_a.shape,
                    np.nan,
                    dtype=np.float32,
                )

                difference[finite] = (
                    data_b[finite] - data_a[finite]
                )

                limit = np.nanpercentile(
                    np.abs(difference[finite]),
                    98,
                )

                fig, ax = plt.subplots(
                    figsize=(8, 6)
                )

                fig.patch.set_facecolor("#10243B")
                ax.set_facecolor("#10243B")

                image = ax.imshow(
                    difference,
                    origin="lower",
                    cmap="coolwarm",
                    vmin=-limit,
                    vmax=limit,
                )

                ax.set_title(
                    "Exploratory Pixel Difference (B − A)",
                    color="white",
                )

                ax.set_xlabel("Pixel", color="white")
                ax.set_ylabel("Pixel", color="white")
                ax.tick_params(colors="white")

                fig.colorbar(
                    image,
                    ax=ax,
                    label="Image value difference",
                )

                fig.tight_layout()

                st.pyplot(
                    fig,
                    use_container_width=True,
                )

                plt.close(fig)

        else:

            st.warning(
                "The images have different dimensions. "
                "A pixel-wise difference cannot be calculated."
            )
# =========================================================
# TAB 3: AI OBSERVATION ASSISTANT
# =========================================================

with tab_ai:

    st.subheader("AI Observation Assistant")

    st.write(
        "Ask questions about a selected SPHEREx FITS observation. "
        "The assistant uses local Ollama models, observation metadata, "
        "and retrieved reference information."
    )

    st.caption(
        "Local models: Qwen3:4b + BGE-M3"
    )

    # ---------------------------------------------
    # Ollama connection check
    # ---------------------------------------------

    if st.button("Check Ollama Connection"):

        try:

            result = ollama_request(
                "/api/tags",
                {},
            )

            model_names = [
                item["name"]
                for item in result.get("models", [])
            ]

            if CHAT_MODEL in model_names and EMBED_MODEL in model_names:

                st.success(
                    "Ollama is connected and both required models are available."
                )

            else:

                st.warning(
                    "Ollama is running, but one or both required models "
                    "were not found. Check the model names using ollama list."
                )

                st.write(model_names)

        except Exception as exc:

            st.error(str(exc))

    st.divider()

    # ---------------------------------------------
    # Select an observation
    # ---------------------------------------------

    st.markdown("### 1. Select an observation")

    try:

        ai_periods = [
            p.rstrip("/").split("/")[-1]
            for p in list_prefixes(
                f"{release}/level2/"
            )
        ]

        if not ai_periods:

            st.warning(
                "No planning periods are currently available."
            )

        else:

            ai_period = st.selectbox(
                "Planning Period",
                ai_periods,
                key="ai_period",
            )

            ai_versions = [
                p.rstrip("/").split("/")[-1]
                for p in list_prefixes(
                    f"{release}/level2/{ai_period}/"
                )
            ]

            if ai_versions:

                ai_version = st.selectbox(
                    "Processing Version",
                    ai_versions,
                    key="ai_version",
                )

                ai_detectors = [
                    p.rstrip("/").split("/")[-1]
                    for p in list_prefixes(
                        f"{release}/level2/{ai_period}/{ai_version}/"
                    )
                ]

                if ai_detectors:

                    ai_detector = st.selectbox(
                        "Detector",
                        ai_detectors,
                        key="ai_detector",
                    )

                    ai_prefix = (
                        f"{release}/level2/{ai_period}/"
                        f"{ai_version}/{ai_detector}/"
                    )

                    ai_files = list_fits(ai_prefix)

                    if ai_files:

                        ai_options = [
                            item["key"]
                            for item in ai_files
                        ]

                        selected_ai_file = st.selectbox(
                            "Select FITS Observation",
                            ai_options,
                            format_func=lambda x: x.split("/")[-1],
                            key="ai_fits_file",
                        )

                        if st.button(
                            "Load Observation for AI",
                            type="primary",
                        ):

                            try:

                                with st.spinner(
                                    "Downloading and reading FITS metadata..."
                                ):

                                    payload = download_fits(
                                        selected_ai_file
                                    )

                                    data, header, extension, metadata = read_image(
                                        payload
                                    )

                                    context = build_observation_context(
                                        metadata,
                                        selected_ai_file,
                                        header,
                                    )

                                    st.session_state[
                                        "ai_observation_context"
                                    ] = context

                                    st.session_state[
                                        "ai_observation_name"
                                    ] = selected_ai_file.split("/")[-1]

                                    st.session_state[
                                        "ai_observation_metadata"
                                    ] = metadata

                                    st.session_state[
                                        "ai_messages"
                                    ] = []

                                st.success(
                                    "Observation loaded successfully."
                                )

                            except Exception as exc:

                                st.error(
                                    f"Could not load observation: {exc}"
                                )

                    else:

                        st.info(
                            "No FITS files were found in this detector folder."
                        )

                else:

                    st.info(
                        "No detector folders were found."
                    )

            else:

                st.info(
                    "No processing versions were found."
                )

    except Exception as exc:

        st.error(
            f"Could not load archive observations: {exc}"
        )

    st.divider()

    # ---------------------------------------------
    # Observation context
    # ---------------------------------------------

    observation_context = st.session_state.get(
        "ai_observation_context"
    )

    if observation_context:

        st.markdown("### 2. Loaded observation")

        st.success(
            f"Active observation: "
            f"{st.session_state.get('ai_observation_name', 'Unknown')}"
        )

        display_table(
            metadata_table(
                st.session_state.get(
                    "ai_observation_metadata",
                    {},
                )
            )
        )

        # -----------------------------------------
        # Ask questions
        # -----------------------------------------

        st.markdown("### 3. Ask the AI assistant")

        question = st.text_input(
            "Your question",
            placeholder="Explain the observation metadata...",
            key="ai_question",
        )

        if st.button(
            "Ask AI",
            type="primary",
            disabled=not question.strip(),
        ):

            try:

                with st.spinner(
                    "Retrieving information and generating an answer..."
                ):

                    answer, sources = generate_ai_answer(
                        question,
                        observation_context,
                    )

                if "ai_messages" not in st.session_state:
                    st.session_state["ai_messages"] = []

                st.session_state["ai_messages"].append(
                    {
                        "question": question,
                        "answer": answer,
                        "sources": sources,
                    }
                )

            except Exception as exc:

                st.error(
                    f"AI assistant error: {exc}"
                )

        # -----------------------------------------
        # Display conversation
        # -----------------------------------------

        for message in st.session_state.get(
            "ai_messages",
            [],
        ):

            with st.chat_message("user"):
                st.write(message["question"])

            with st.chat_message("assistant"):

                st.write(message["answer"])

                with st.expander("Retrieved reference sources"):

                    for source in message["sources"]:

                        st.markdown(
                            f"**{source['source']}**"
                        )

                        st.caption(
                            source["text"].strip()
                        )

                        st.markdown(
                            f"[Open source documentation]({source['url']})"
                        )

                        st.divider()

    else:

        st.info(
            "Select and load a FITS observation above to start "
            "asking questions."
        )
# =========================================================
# TAB 4: ABOUT
# =========================================================

with tab_about:

    st.subheader("About SPHEREx TimeScope")

    st.markdown("""
    **SPHEREx TimeScope** is an educational application
    designed to make public SPHEREx infrared observations
    easier to explore and inspect.

    ### Main Features

    - Browse public QR2 and QR3 Level 2 archive folders.
    - Explore planning periods and processing versions.
    - View available FITS observation files.
    - Inspect selected FITS image previews.
    - Review observation metadata.
    - Compare two selected observations.
    - Generate an exploratory pixel-difference preview
      when image dimensions match.

    ### NASA Data Source

    NASA SPHEREx Quick Release spectral images hosted
    by Caltech/IPAC IRSA.

    **QR3 Dataset DOI:**  
    https://doi.org/10.26131/IRSA662

    **Public AWS Archive:**  
    https://nasa-irsa-spherex.s3.amazonaws.com/

    **Archive Documentation:**  
    https://caltech-ipac.github.io/spherex-archive-documentation/

    ### Scientific Limitations

    Two files are not automatically observations of the
    same sky region.

    A scientifically valid time-domain comparison requires
    checking sky coordinates, observation times, wavelength
    coverage, masks, image registration, and calibration.

    The pixel-difference preview in this application is
    exploratory and is not a calibrated scientific measurement.
    """)

    st.markdown("### Data Acknowledgement")

    st.write(
        "This publication makes use of data products from the "
        "Spectro-Photometer for the History of the Universe, "
        "Epoch of Reionization and Ices Explorer (SPHEREx), "
        "which is a joint project of the Jet Propulsion Laboratory "
        "and the California Institute of Technology, and is funded "
        "by the National Aeronautics and Space Administration."
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    '<p class="small-note">'
    'SPHEREx TimeScope · Educational Prototype · '
    'NASA SPHEREx Public Archive'
    '</p>',
    unsafe_allow_html=True,
)            