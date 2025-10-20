import streamlit as st
from datetime import datetime
from utils.db import SessionLocal, Concept
from utils.llm_helpers import export_concepts_to_pdf
from utils.parser_newsletter import parse_newsletter
from utils.topic_manager import update_topics
from utils.topic_manager import sync_yaml_to_db, sync_db_to_yaml, sync_topics_to_concepts
from PIL import Image
import pytesseract
import os


def show():
    st.header("Admin - Topic Management")
    with st.expander("🔄 Sync Options"):
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Sync YAML File → Topics Table"):
                sync_yaml_to_db()
                st.success("✅ Synced YAML to Topics Table")

        with col2:
            if st.button("Sync YAML → Concept Table"):
                sync_topics_to_concepts()
                st.success("✅ Synced YAML to Concept Table")

        with col3:
            if st.button("Sync Database → YAML"):
                sync_db_to_yaml()
                st.success("✅ Synced database to YAML")
        st.caption(
            "Use these buttons to synchronize concepts between the YAML file and the database. "
            "YAML → Database updates the database from the YAML file, while Database → YAML exports the current database to YAML."
        )

    st.title("🧠 Admin - Weekly Concepts Manager")
    st.write("Upload newsletters or add learning topics manually. Supports image OCR and text parsing.")

    db = SessionLocal()

    # ---------- Newsletter Upload / OCR ----------
    st.subheader("📷 Upload or Paste Newsletter")
    tab1, tab2 = st.tabs(["📸 Upload Image", "📝 Paste Text"])

    with tab1:
        uploaded_file = st.file_uploader("Upload newsletter image", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Newsletter Preview", use_container_width=True)

            with st.spinner("🔍 Extracting text with OCR..."):
                text = pytesseract.image_to_string(image)

            st.text_area("Extracted Text (editable)", value=text, height=250, key="ocr_text")

            if st.button("🧩 Parse & Update Topics (from image)"):
                topics = parse_newsletter(st.session_state.ocr_text)
                update_topics(topics)
                st.success(f"✅ Parsed and updated {len(topics)} topics successfully!")

    with tab2:
        raw_text = st.text_area("Paste newsletter text here", height=250)
        if st.button("🧩 Parse & Update Topics (from text)"):
            topics = parse_newsletter(raw_text)
            update_topics(topics)
            st.success(f"✅ Parsed and updated {len(topics)} topics successfully!")

    # ---------- Add New Concept ----------
    st.subheader("➕ Add New Concept")
    with st.form("add_concept_form"):
        col1, col2 = st.columns(2)
        with col1:
            date_start = st.date_input("Start Date", value=datetime.now().date())
            date_end = st.date_input("End Date (optional)")
        with col2:
            subject = st.text_input("Subject (e.g. Reading/Writing, Vocabulary, Math)")
            type_ = st.selectbox("Type", ["vocab", "grammar", "reading", "math", "science", "other"])
        topic = st.text_area("Topic or Description", height=100)
        notes = st.text_area("Optional Notes", height=80)
        submitted = st.form_submit_button("💾 Save Concept")

        if submitted:
            if not subject or not topic:
                st.warning("Please fill out both subject and topic.")
            else:
                new_concept = Concept(
                    date_start=date_start,
                    date_end=date_end if date_end else None,
                    subject=subject.strip(),
                    topic=topic.strip(),
                    type=type_,
                    notes=notes.strip() if notes else None,
                )
                db.add(new_concept)
                db.commit()
                st.success(f"✅ Added concept: {subject} - {topic}")

    # ---------- Display Recent Concepts ----------
    st.subheader("📋 Recent Concepts")
    concepts = db.query(Concept).order_by(Concept.date_start.desc()).limit(15).all()

    if concepts:
        for c in concepts:
            st.markdown(f"**{c.subject}** ({c.type or 'N/A'})")
            st.caption(f"{c.date_start} → {c.date_end or 'N/A'}")
            st.write(c.topic)
            if c.notes:
                st.info(f"🗒 Notes: {c.notes}")

            # Delete option
            if st.button(f"🗑 Delete {c.id}", key=f"del_{c.id}"):
                db.delete(c)
                db.commit()
                st.warning(f"Deleted concept {c.id}")
                st.experimental_rerun()

            st.markdown("---")
    else:
        st.info("No concepts have been added yet.")

    # ---------- Export Section ----------
    st.subheader("📤 Export Concepts to PDF")
    export_path = "data/exports/concepts_summary.pdf"
    if st.button("📘 Generate Concepts Summary PDF"):
        os.makedirs("data/exports", exist_ok=True)
        message = export_concepts_to_pdf(concepts, export_path)
        st.success(message)
        st.write(f"📁 Saved to `{export_path}`")

    db.close()