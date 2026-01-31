
import streamlit as st
import os
from datetime import datetime
from typing import Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


def extract_text_from_txt(file) -> str:
    """Extract text from a TXT file-like object."""
    try:
        return file.read().decode("utf-8")
    except Exception as e:
        st.error(f"Error reading TXT file: {e}")
        return ""


def extract_text_from_pdf(file) -> str:
    """Extract text from a PDF file-like object using PyMuPDF."""
    if fitz is None:
        st.error("PyMuPDF (fitz) is not installed. Cannot extract PDF text.")
        return ""
    text = ""
    try:
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
    return text.strip()


def get_uploaded_passage_text(uploaded_file) -> Optional[str]:
    """Return the text content from the uploaded file, if any."""
    if uploaded_file is None:
        return None
    filename = uploaded_file.name.lower()
    if filename.endswith(".txt"):
        return extract_text_from_txt(uploaded_file)
    elif filename.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    else:
        st.error("Unsupported file type.")
        return None


def save_passage(text: str, title: Optional[str]) -> str:
    """Save passage text to file and return the filename."""
    os.makedirs("data/passages", exist_ok=True)
    safe_title = (
        title.strip().replace(" ", "_")
        if title and title.strip()
        else f"passage_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    filename = f"{safe_title}.txt"
    file_path = os.path.join("data/passages", filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text.strip())
    return filename


def show():
    st.title("📝 Add New Passage")
    st.write(
        "Paste or upload a passage (from homework, PDF, or ReadWorks) and save it locally as a .txt file for future use."
    )

    uploaded_text = ""

    # ---- File Upload Section ----
    st.subheader("📤 Upload Passage File")
    uploaded_file = st.file_uploader("Upload a .txt or .pdf file", type=["txt", "pdf"])
    if uploaded_file is not None:
        uploaded_text = get_uploaded_passage_text(uploaded_file) or ""
        if uploaded_text:
            st.success(f"Loaded text from `{uploaded_file.name}`")
            with st.expander("📄 Preview Uploaded Content"):
                st.write(uploaded_text[:2000] + ("..." if len(uploaded_text) > 2000 else ""))

    # ---- Manual Entry Section ----
    st.subheader("✏️ Or Paste Passage Text Manually")
    with st.form("add_passage_form"):
        title = st.text_input("Title (optional, will become the filename if provided):")
        passage_text = st.text_area(
            "Passage text:",
            value=uploaded_text if uploaded_text else "",
            height=250,
        )
        submitted = st.form_submit_button("💾 Save Passage")

        if submitted:
            if not passage_text.strip():
                st.warning("Please enter or upload some text before saving.")
            else:
                filename = save_passage(passage_text, title)
                st.success(f"✅ Saved passage as `{filename}`!")
                with st.expander("📖 Preview Saved Passage"):
                    st.write(passage_text.strip())

    st.info("💡 Tip: Saved passages can be used in Learning Mode under 'Select a saved passage.'")