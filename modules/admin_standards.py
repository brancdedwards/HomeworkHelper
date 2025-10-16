

import streamlit as st
from datetime import datetime
from utils.db import SessionLocal, Concept
from utils.llm_helpers import export_concepts_to_pdf
import os

def show():
    st.title("🧠 Admin - Weekly Concepts Manager")
    st.write("Add or review weekly learning topics and vocabulary entries.")

    db = SessionLocal()

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