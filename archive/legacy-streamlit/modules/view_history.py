import streamlit as st
import os
from utils.db import SessionLocal, Session, Passage, Question, Word
from utils.llm_helpers import export_passage_to_pdf

def show():
    st.title("📜 View Learning History")
    st.write("Browse your saved passages, simplified texts, and questions.")

    db = SessionLocal()

    # ---------- Session Selection ----------
    sessions = db.query(Session).order_by(Session.created_at.desc()).all()

    if not sessions:
        st.info("No saved sessions yet. Try adding a passage in 'Add Passage' or using 'Learning Mode'.")
        return

    session_titles = [f"{s.id}: {s.topic or 'Untitled'} ({s.created_at.strftime('%Y-%m-%d %H:%M')})" for s in sessions]
    selected_session = st.selectbox("Select a learning session:", session_titles)

    if selected_session:
        session_id = int(selected_session.split(":")[0])
        selected = db.query(Session).filter(Session.id == session_id).first()

        st.divider()
        st.subheader(f"🗂 Session: {selected.topic or 'Untitled'}")
        st.caption(f"Created at: {selected.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

        # ---------- Display Passages ----------
        for p in selected.passages:
            st.markdown("### 📖 Original Passage")
            st.text_area("Original text", p.original_text or "—", height=150, disabled=True)

            if p.simplified_text:
                st.markdown("### ✏️ Simplified Version")
                st.text_area("Simplified text", p.simplified_text, height=150, disabled=True)

            # ---------- Questions ----------
            questions = db.query(Question).filter(Question.passage_id == p.id).all()
            if questions:
                st.markdown("### ❓ Comprehension Questions")
                for q in questions:
                    st.write(f"- {q.question_text}")

            # ---------- Vocabulary ----------
            words = db.query(Word).filter(Word.passage_id == p.id).all()
            if words:
                st.markdown("### 🗣 Vocabulary Words")
                for w in words:
                    st.write(f"**{w.word}** — {w.explanation}")

            # ---------- Export ----------
            export_filename = f"data/exports/session_{selected.id}_passage_{p.id}.txt"
            if st.button(f"💾 Export Passage #{p.id}", key=f"export_{p.id}"):
                os.makedirs("data/exports", exist_ok=True)
                with open(export_filename, "w", encoding="utf-8") as f:
                    f.write("=== Session Info ===\n")
                    f.write(f"Topic: {selected.topic or 'Untitled'}\n")
                    f.write(f"Date: {selected.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                    f.write("=== Original Passage ===\n")
                    f.write(p.original_text or "")
                    f.write("\n\n=== Simplified Version ===\n")
                    f.write(p.simplified_text or "")
                    f.write("\n\n=== Questions ===\n")
                    for q in questions:
                        f.write(f"- {q.question_text}\n")
                    f.write("\n\n=== Vocabulary ===\n")
                    for w in words:
                        f.write(f"{w.word}: {w.explanation}\n")

                st.success(f"Exported to `{export_filename}`")

            pdf_filename = f"data/exports/session_{selected.id}_passage_{p.id}.pdf"
            if st.button(f"📘 Export Passage #{p.id} to PDF", key=f"pdf_{p.id}"):
                os.makedirs("data/exports", exist_ok=True)
                message = export_passage_to_pdf(selected, p, questions, words, pdf_filename)
                st.success(message)

    db.close()