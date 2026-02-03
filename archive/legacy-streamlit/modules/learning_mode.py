import streamlit as st
import os
from utils.db import SessionLocal, Session, Passage, Question, Word
from utils.passage_loader import load_random_passage
from utils.llm_helpers import simplify_text, generate_questions, explain_word

def show():
    st.title("📖 Homework Helper - Learning Mode")

    db = SessionLocal()

    # Passage selection
    st.subheader("📚 Choose or Load a Passage")

    passage_files = [f for f in os.listdir("data/passages") if f.endswith(".txt")]
    selected_file = st.selectbox("Select a saved passage:", ["-- None --"] + passage_files)

    if selected_file != "-- None --":
        with open(f"data/passages/{selected_file}", "r", encoding="utf-8") as f:
            selected_text = f.read()
        st.session_state["loaded_passage"] = selected_text
        st.success(f"Loaded passage: {selected_file}")

    # Load random passage
    if st.button("📥 Load Random Passage"):
        passage_text = load_random_passage(save_to_db=False)
        if passage_text:
            st.session_state["loaded_passage"] = passage_text
            st.success("Loaded a random passage!")
        else:
            st.warning("No passages found locally or online.")

    topic = st.text_input("Enter a topic or short title for this passage:")
    text = st.text_area(
        "Paste the passage here or load one using the button above:",
        value=st.session_state.get("loaded_passage", ""),
        height=200
    )

    if st.button("Simplify Passage"):
        if text.strip():
            simplified = simplify_text(text)
            st.subheader("Simplified Version")
            st.write(simplified)

            # Save to DB
            try:
                session_obj = Session(topic=topic or "Untitled")
                db.add(session_obj)
                db.commit()

                passage = Passage(session_id=session_obj.id, original_text=text, simplified_text=simplified)
                db.add(passage)
                db.commit()
                st.success("Saved simplified passage!")

                # Generate comprehension questions
                st.subheader("Comprehension Questions")
                questions = generate_questions(text)
                st.write(questions)
                for q in questions.split("\n"):
                    if q.strip():
                        q_obj = Question(passage_id=passage.id, question_text=q.strip())
                        db.add(q_obj)
                db.commit()
            except Exception as e:
                st.error(f"Error saving passage: {e}")
        else:
            st.warning("Please paste or load a passage first.")

    st.divider()
    st.subheader("Word Helper")
    word = st.text_input("Enter a tricky word:")
    if st.button("Explain Word"):
        if word.strip() and text.strip():
            meaning = explain_word(word, text)
            st.write(meaning)
            try:
                last_passage = db.query(Passage).order_by(Passage.id.desc()).first()
                if last_passage:
                    w = Word(passage_id=last_passage.id, word=word.strip(), explanation=meaning)
                    db.add(w)
                    db.commit()
                    st.success("Word explanation saved!")
            except Exception as e:
                st.error(f"Error saving word: {e}")
        else:
            st.warning("Add both the passage and the word.")

    db.close()
