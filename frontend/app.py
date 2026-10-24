import html
import os
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "25"))

st.set_page_config(
    page_title="Aster | Knowledge Workspace",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #17211f;
        --muted: #71807a;
        --green: #126b55;
        --green-dark: #0d4c3e;
        --mint: #e9f4ee;
        --line: #e5ebe7;
        --paper: #ffffff;
    }

    html, body, [class*="css"] {
        font-family: 'Aptos', 'Segoe UI', sans-serif;
        color: var(--ink);
    }
    .stApp {
        background:
            radial-gradient(ellipse at 70% 0%, rgba(222, 239, 228, .55), transparent 34rem),
            #f7f9f7;
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] {
        background: #fff;
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.6rem; }
    .block-container {
        max-width: 1420px;
        padding-top: 2.3rem;
        padding-bottom: 4rem;
    }
    h1, h2, h3 {
        font-family: 'Manrope', sans-serif;
        color: var(--ink);
        letter-spacing: -.035em;
    }
    .brand {
        display: flex;
        align-items: center;
        gap: 11px;
        padding: 0 0 1.8rem 0;
    }
    .brand-mark {
        display: grid;
        place-items: center;
        width: 38px;
        height: 38px;
        border-radius: 12px;
        background: var(--green);
        color: #fff;
        font-size: 21px;
        box-shadow: 0 6px 16px rgba(18, 107, 85, .2);
    }
    .brand-name {
        font: 800 17px 'Aptos', 'Segoe UI', sans-serif;
        letter-spacing: -.04em;
        color: var(--ink);
    }
    .brand-caption {
        color: var(--muted);
        font-size: 10px;
        letter-spacing: .12em;
        text-transform: uppercase;
        margin-top: 1px;
    }
    .side-label {
        color: #98a39e;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: .13em;
        text-transform: uppercase;
        padding: 0 0 9px 3px;
    }
    .nav-item {
        padding: 10px 12px;
        border-radius: 10px;
        color: #54625c;
        font-size: 13px;
        margin-bottom: 4px;
    }
    .nav-item.active {
        background: var(--mint);
        color: var(--green-dark);
        font-weight: 700;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] > button {
        min-height: 40px;
        border: 0;
        background: transparent !important;
        color: #54625c !important;
        text-align: left;
        justify-content: flex-start;
        padding-left: 12px;
        box-shadow: none;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] > button p,
    [data-testid="stSidebar"] [data-testid="stButton"] > button span {
        color: inherit !important;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] > button[kind="primary"] {
        background: var(--mint) !important;
        color: var(--green-dark) !important;
        font-weight: 700;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
        border: 0;
        background: var(--mint) !important;
        color: var(--green-dark) !important;
    }
    .side-status {
        margin-top: 1.6rem;
        border: 1px solid var(--line);
        border-radius: 14px;
        background: #fbfcfb;
        padding: 14px;
    }
    .side-status-title {
        font-size: 11px;
        color: var(--muted);
        margin-bottom: 9px;
    }
    .status-dot {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #33a77e;
        margin-right: 7px;
        vertical-align: 1px;
    }
    .status-dot.offline { background: #d58163; }
    .status-copy { font-size: 12px; font-weight: 600; color: var(--ink); }
    .eyebrow {
        color: var(--green);
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .14em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .page-title {
        font: 800 clamp(32px, 4vw, 47px)/1.12 'Aptos', 'Segoe UI', sans-serif;
        letter-spacing: -.055em;
        margin: 0;
        color: var(--ink);
    }
    .page-subtitle {
        color: #687770;
        font-size: 15px;
        line-height: 1.7;
        max-width: 640px;
        margin-top: 12px;
    }
    .top-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        border: 1px solid #dce9df;
        background: rgba(255,255,255,.8);
        border-radius: 999px;
        padding: 9px 13px;
        color: #426254;
        font-size: 11px;
        font-weight: 600;
        white-space: nowrap;
    }
    .stat-card, .panel {
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: 16px;
        box-shadow: 0 5px 20px rgba(32, 53, 42, .035);
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--paper);
        border-color: var(--line);
        border-radius: 16px;
        box-shadow: 0 5px 20px rgba(32, 53, 42, .035);
        padding: 1.4rem;
    }
    .stat-card { padding: 17px 19px; min-height: 91px; }
    .stat-label {
        font-size: 11px;
        color: var(--muted);
        margin-bottom: 8px;
    }
    .stat-value {
        font: 700 21px 'Aptos', 'Segoe UI', sans-serif;
        color: var(--ink);
        letter-spacing: -.04em;
    }
    .panel { padding: 23px; }
    .panel-heading {
        font: 700 17px 'Aptos', 'Segoe UI', sans-serif;
        letter-spacing: -.03em;
        margin: 0 0 5px;
        color: var(--ink);
    }
    .panel-caption {
        color: var(--muted);
        font-size: 12px;
        line-height: 1.6;
        margin-bottom: 18px;
    }
    .upload-symbol {
        display: grid;
        place-items: center;
        width: 43px;
        height: 43px;
        border-radius: 13px;
        background: var(--mint);
        color: var(--green);
        font-size: 22px;
        margin-bottom: 14px;
    }
    .stFileUploader [data-testid="stFileUploaderDropzone"] {
        background: #fbfdfb;
        border: 1px dashed #b8cec0;
        border-radius: 13px;
    }
    .stFileUploader [data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--green);
        background: #f4faf6;
    }
    .stButton > button {
        min-height: 43px;
        border-radius: 10px;
        border: 1px solid var(--green);
        background: var(--green);
        color: white;
        font-weight: 700;
        transition: all .18s ease;
    }
    .stButton > button:hover {
        border-color: var(--green-dark);
        background: var(--green-dark);
        color: white;
        box-shadow: 0 5px 14px rgba(18, 107, 85, .16);
    }
    .upload-note {
        color: #84918b;
        font-size: 11px;
        margin-top: 11px;
    }
    .feature-row {
        display: flex;
        gap: 12px;
        align-items: flex-start;
        margin: 17px 0;
    }
    .feature-number {
        display: grid;
        place-items: center;
        flex: 0 0 27px;
        height: 27px;
        border-radius: 9px;
        background: #edf5ef;
        color: var(--green);
        font-size: 11px;
        font-weight: 700;
    }
    .feature-title {
        color: var(--ink);
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 3px;
    }
    .feature-copy { color: var(--muted); font-size: 11px; line-height: 1.5; }
    .document-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 13px 15px;
        border: 1px solid var(--line);
        border-radius: 12px;
        margin-top: 9px;
        background: #fff;
    }
    .document-name {
        color: var(--ink);
        font-size: 12px;
        font-weight: 600;
        overflow-wrap: anywhere;
    }
    .document-meta { color: var(--muted); font-size: 10px; margin-top: 3px; }
    .document-pill {
        background: #eaf5ee;
        color: #287457;
        border-radius: 999px;
        padding: 5px 9px;
        font-size: 10px;
        font-weight: 700;
        white-space: nowrap;
        margin-left: 12px;
    }
    div[data-testid="stAlert"] { border-radius: 12px; }
    [data-testid="stChatMessage"] {
        border: 1px solid var(--line);
        border-radius: 16px;
        background: white !important;
        color: var(--ink) !important;
    }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {
        color: var(--ink) !important;
    }
    [data-testid="stChatInput"] {
        border-radius: 16px;
        border-color: #cbd9d0;
        background: white !important;
    }
    [data-testid="stChatInput"] textarea {
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink) !important;
        caret-color: var(--green);
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #71807a !important;
        -webkit-text-fill-color: #71807a !important;
    }
    .chat-kicker {
        color: var(--green);
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .14em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .chat-title {
        color: var(--ink);
        font: 800 clamp(30px, 4vw, 42px)/1.15 'Aptos', 'Segoe UI', sans-serif;
        letter-spacing: -.05em;
    }
    .chat-subtitle {
        color: var(--muted);
        font-size: 14px;
        margin-top: 8px;
        margin-bottom: 24px;
    }
    .chat-kicker, .chat-title, .chat-subtitle, .suggestion-label {
        -webkit-text-fill-color: currentColor;
    }
    .suggestion-label {
        color: var(--muted);
        font-size: 12px;
        font-weight: 600;
        margin: 12px 0 8px;
    }
    .source-chip {
        display: inline-block;
        background: #edf5ef;
        color: #28654f;
        border-radius: 8px;
        padding: 5px 8px;
        font-size: 11px;
        margin: 4px 5px 0 0;
    }
    @media (max-width: 750px) {
        .block-container { padding-top: 1.2rem; }
        .panel { padding: 18px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=10, show_spinner=False)
def check_backend() -> tuple[bool, str]:
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=3)
        response.raise_for_status()
    except requests.RequestException as exc:
        return False, str(exc)

    if response.json().get("status") != "ok":
        return False, "The backend returned an unexpected health response."
    return True, ""


def format_bytes(size: int) -> str:
    if size < 1024 * 1024:
        return f"{size / 1024:.0f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


if "documents" not in st.session_state:
    st.session_state.documents = []
if "workspace_page" not in st.session_state:
    st.session_state.workspace_page = "library"
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

backend_online, backend_error = check_backend()

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-mark">✦</div>
            <div>
                <div class="brand-name">Aster</div>
                <div class="brand-caption">Knowledge workspace</div>
            </div>
        </div>
        <div class="side-label">Workspace</div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(
        "▦  Document library",
        use_container_width=True,
        type="primary" if st.session_state.workspace_page == "library" else "secondary",
    ):
        st.session_state.workspace_page = "library"
        st.rerun()
    if st.button(
        "⌕  Ask your documents",
        use_container_width=True,
        type="primary" if st.session_state.workspace_page == "chat" else "secondary",
    ):
        st.session_state.workspace_page = "chat"
        st.rerun()
    st.markdown(
        f"""
        <div class="side-status">
            <div class="side-status-title">System status</div>
            <div class="status-copy">
                <span class="status-dot {' ' if backend_online else 'offline'}"></span>
                {'API connected' if backend_online else 'API unavailable'}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not backend_online:
        st.caption(f"Could not reach {BACKEND_URL}: {backend_error}")
    if st.button("Refresh connection", use_container_width=True):
        check_backend.clear()
        st.rerun()
    st.markdown(
        f'<div class="upload-note">Connected to <code>{html.escape(BACKEND_URL)}</code></div>',
        unsafe_allow_html=True,
    )

def submit_chat_question(question: str) -> None:
    question = question.strip()
    if not question:
        return
    history = st.session_state.chat_messages[-8:]
    st.session_state.chat_messages.append({"role": "user", "content": question})
    st.session_state.chat_error = ""
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                "question": question,
                "history": [
                    {"role": message["role"], "content": message["content"]}
                    for message in history
                ],
            },
            timeout=(5, 120),
        )
        response.raise_for_status()
        payload = response.json()
        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": payload["answer"],
                "sources": payload.get("sources", []),
            }
        )
    except requests.RequestException as exc:
        st.session_state.chat_error = f"Could not get an answer: {exc}"
    except (KeyError, ValueError) as exc:
        st.session_state.chat_error = f"The answer service returned an invalid response: {exc}"


if st.session_state.workspace_page == "chat":
    st.markdown('<div class="chat-kicker">Hybrid knowledge assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="chat-title">Ask your documents.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="chat-subtitle">Get grounded answers from your PDFs, with relevant '
        'knowledge-graph context and page citations.</div>',
        unsafe_allow_html=True,
    )
    indexed_docs = [
        document
        for document in st.session_state.documents
        if document.get("status") == "indexed"
    ]
    try:
        documents_response = requests.get(f"{BACKEND_URL}/documents", timeout=5)
        documents_response.raise_for_status()
        indexed_docs = documents_response.json()
    except requests.RequestException as exc:
        st.error(f"Could not load the indexed document list: {exc}")
    if not indexed_docs:
        st.info("Upload a PDF and wait for indexing to finish before asking questions.")

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("sources"):
                with st.expander("Sources used"):
                    for source in message["sources"]:
                        st.markdown(
                            f'<span class="source-chip">[{html.escape(source["label"])}] '
                            f'{html.escape(source["filename"])} · p. '
                            f'{html.escape(str(source["page_number"]))}</span>',
                            unsafe_allow_html=True,
                        )

    if not st.session_state.chat_messages:
        st.markdown('<div class="suggestion-label">Try asking</div>', unsafe_allow_html=True)
        prompts = [
            "Summarize the main ideas",
            "What are the key entities and how are they connected?",
            "What does the document say about its architecture?",
        ]
        prompt_cols = st.columns(len(prompts))
        for column, prompt in zip(prompt_cols, prompts):
            with column:
                if st.button(prompt, use_container_width=True, disabled=not backend_online):
                    submit_chat_question(prompt)
                    st.rerun()

    if st.session_state.get("chat_error"):
        st.error(st.session_state.chat_error)
    if not backend_online:
        st.warning("The API is offline. Start the backend to ask questions.")
    prompt = st.chat_input(
        "Ask a question about your indexed PDFs...",
        disabled=not backend_online or not indexed_docs,
    )
    if prompt:
        with st.spinner("Searching your documents and connected knowledge..."):
            submit_chat_question(prompt)
        st.rerun()
    if st.button("Clear conversation"):
        st.session_state.chat_messages = []
        st.session_state.chat_error = ""
        st.rerun()
    st.stop()

st.markdown('<div class="eyebrow">Your knowledge, in one place</div>', unsafe_allow_html=True)
header_col, badge_col = st.columns([5, 1.45], vertical_alignment="center")
with header_col:
    st.markdown(
        '<h1 class="page-title">A clearer way to work<br>with your documents.</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-subtitle">Add your PDF sources to the workspace. '
        'Keep your documents organized and ready for the next stage of your '
        'knowledge workflow.</div>',
        unsafe_allow_html=True,
    )
with badge_col:
    st.markdown(
        '<div class="top-badge"><span class="status-dot"></span>Private workspace</div>',
        unsafe_allow_html=True,
    )

st.write("")
stats = st.columns(3)
with stats[0]:
    st.markdown(
        f'<div class="stat-card"><div class="stat-label">Sources this session</div>'
        f'<div class="stat-value">{len(st.session_state.documents):02d}</div></div>',
        unsafe_allow_html=True,
    )
with stats[1]:
    st.markdown(
        f'<div class="stat-card"><div class="stat-label">Maximum PDF size</div>'
        f'<div class="stat-value">{MAX_UPLOAD_MB} MB</div></div>',
        unsafe_allow_html=True,
    )
with stats[2]:
    st.markdown(
        f'<div class="stat-card"><div class="stat-label">Backend</div>'
        f'<div class="stat-value">{"Online" if backend_online else "Offline"}</div></div>',
        unsafe_allow_html=True,
    )

st.write("")
upload_col, info_col = st.columns([1.55, 1], gap="large")

with upload_col:
    with st.container(border=True):
        st.markdown('<div class="upload-symbol">↑</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-heading">Add a source document</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="panel-caption">Upload a PDF to add it to your document library. '
            f'Files up to {MAX_UPLOAD_MB} MB are supported.</div>',
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "Choose a PDF",
            type=["pdf"],
            accept_multiple_files=False,
            help=f"Maximum file size: {MAX_UPLOAD_MB} MB",
            label_visibility="collapsed",
        )
        if uploaded_file is not None:
            st.caption(f"Selected: {uploaded_file.name} · {format_bytes(uploaded_file.size)}")
        if st.button(
            "Upload document",
            type="primary",
            use_container_width=True,
            disabled=uploaded_file is None or not backend_online,
        ):
            if uploaded_file.size > MAX_UPLOAD_MB * 1024 * 1024:
                st.error(f"This PDF exceeds the {MAX_UPLOAD_MB} MB upload limit.")
            else:
                try:
                    with st.spinner("Uploading your document..."):
                        response = requests.post(
                            f"{BACKEND_URL}/documents/upload",
                            files={
                                "file": (
                                    uploaded_file.name,
                                    uploaded_file.getvalue(),
                                    "application/pdf",
                                )
                            },
                            timeout=30,
                        )
                    if response.ok:
                        document = response.json()
                        st.session_state.documents.insert(0, document)
                        st.success(
                            f"{document['filename']} was uploaded. Indexing is running "
                            "in the background."
                        )
                        st.rerun()
                    try:
                        detail = response.json().get("detail", response.text)
                    except ValueError:
                        detail = response.text
                    st.error(f"Upload failed ({response.status_code}): {detail}")
                except requests.RequestException as exc:
                    st.error(f"Could not upload the PDF: {exc}")
        st.markdown(
            '<div class="upload-note">PDF format only · Your original filename is preserved in the library</div>',
            unsafe_allow_html=True,
        )

with info_col:
    with st.container(border=True):
        st.markdown('<div class="panel-heading">A focused workspace</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="panel-caption">A simple starting point for building a searchable '
            'knowledge base from your own materials.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="feature-row">
                <div class="feature-number">01</div>
                <div><div class="feature-title">Add your source</div>
                <div class="feature-copy">Upload a local PDF to the connected API.</div></div>
            </div>
            <div class="feature-row">
                <div class="feature-number">02</div>
                <div><div class="feature-title">Build your knowledge base</div>
                <div class="feature-copy">Prepare the document for vector and graph indexing.</div></div>
            </div>
            <div class="feature-row">
                <div class="feature-number">03</div>
                <div><div class="feature-title">Explore with hybrid retrieval</div>
                <div class="feature-copy">Bring semantic search and connected context together.</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")
st.markdown('<div class="panel-heading">Recent documents</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="panel-caption">PDFs uploaded in this browser session.</div>',
    unsafe_allow_html=True,
)
if any(document["status"] == "processing" for document in st.session_state.documents):
    if st.button("Refresh indexing status"):
        for document in st.session_state.documents:
            if document["status"] != "processing":
                continue
            try:
                response = requests.get(
                    f"{BACKEND_URL}/documents/{document['document_id']}",
                    timeout=5,
                )
                response.raise_for_status()
                document.update(response.json())
            except requests.RequestException as exc:
                st.error(f"Could not refresh {document['filename']} status: {exc}")

if not st.session_state.documents:
    st.info("Your library is ready. Upload a PDF to see it here.")
else:
    for document in st.session_state.documents:
        st.markdown(
            f"""
            <div class="document-row">
                <div>
                    <div class="document-name">{html.escape(document["filename"])}</div>
                    <div class="document-meta">{format_bytes(document["size_bytes"])} · {document.get("chunk_count", 0)} chunks · {document.get("entity_count", 0)} entities · {document.get("relation_count", 0)} relationships · {html.escape(str(document.get("stage", document["status"])))}</div>
                </div>
                <div class="document-pill">{html.escape(str(document["status"]).title())}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if document["status"] == "failed":
            st.error(f"{document['filename']}: {document.get('error', 'Indexing failed.')}")
