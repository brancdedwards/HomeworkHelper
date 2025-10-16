import streamlit as st
from utils.llm_helpers import generate_sentences, generate_grammar_question

def show():
    st.title("📘 Grammar Practice")
    st.write("Practice identifying grammar concepts such as parts of speech, similes, and metaphors.")

    st.info("💡 Tip: You can generate new sentences for fresh practice.")

    num_sentences = st.slider("How many sentences do you want to practice with?", 1, 5, 3)
    if st.button("🔄 Generate Sentences"):
        with st.spinner("Generating sentences..."):
            sentences = generate_sentences(num_sentences)
            if not sentences:
                st.error("Failed to generate sentences. Please check your API or LLM settings.")
                return

            st.session_state["grammar_sentences"] = sentences
            st.success(f"Generated {len(sentences)} sentences!")

    sentences = st.session_state.get("grammar_sentences", [])
    if not sentences:
        st.write("👆 Generate sentences to begin.")
        return

    st.subheader("🧠 Identify Grammar Elements")
    for i, sentence in enumerate(sentences, start=1):
        st.markdown(f"**Sentence {i}:** {sentence}")
        question = generate_grammar_question(sentence)
        if not question:
            st.warning("Could not generate question.")
            continue

        st.write(question["prompt"])
        options = question.get("options", [])
        if options:
            answer = st.radio("Choose an answer:", options, key=f"ans_{i}")
            if st.button(f"✅ Check Answer {i}", key=f"check_{i}"):
                if answer == question["answer"]:
                    st.success("Correct! 🎉")
                else:
                    st.error(f"Incorrect. The correct answer is **{question['answer']}**.")
        else:
            st.text_input("Your answer:", key=f"input_{i}")
            if st.button(f"✅ Submit Answer {i}", key=f"sub_{i}"):
                st.info(f"The correct answer is: **{question['answer']}**")
