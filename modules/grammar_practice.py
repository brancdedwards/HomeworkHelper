import streamlit as st
from utils.llm_helpers import generate_grammar_question, get_grammar_hint, generate_sentences_from_topics, get_available_categories
from utils.db import log_attempt

DEBUG = False  # Set to False to disable debug logs

def show():
    st.title("📘 Grammar Practice")
    st.write("Practice identifying grammar concepts such as parts of speech, similes, and metaphors.")

    st.info("💡 Tip: You can generate new sentences for fresh practice.")

    mode = st.radio(
        "How would you like to generate practice questions?",
        ("Generate at random", "Let me choose a category")
    )

    from utils.llm_helpers import get_available_categories

    try:
        categories = get_available_categories()
    except Exception as e:
        st.error(f"Error loading categories from database: {e}")
        categories = []

    if mode == "Let me choose a category":
        chosen_category = st.selectbox("Select a category:", categories)
    else:
        chosen_category = None

    num_sentences = st.slider("How many sentences do you want to practice with?", 1, 10, 3)
    if st.button("🔄 Generate Sentences"):
        with st.spinner("Generating sentences..."):
            if mode == "Generate at random":
                sentences = generate_sentences_from_topics(n=num_sentences, category=chosen_category)
            else:
                sentences = generate_sentences_from_topics(n=num_sentences, category=chosen_category)
            if not sentences:
                st.error("Failed to generate sentences. Please check your API or LLM settings.")
                return

            st.session_state["grammar_sentences"] = sentences
            # Clear previous answers, submitted flags, hints, and questions when new sentences are generated
            for i in range(len(sentences)):
                st.session_state.pop(f"ans_{i+1}", None)
                st.session_state.pop(f"submitted_{i+1}", None)
                st.session_state.pop(f"hint_{i+1}", None)
            st.session_state.pop("grammar_questions", None)
            st.success(f"Generated {len(sentences)} sentences!")

    sentences = st.session_state.get("grammar_sentences", [])
    if not sentences:
        st.write("👆 Generate sentences to begin.")
        return

    # Generate questions once and store them in session_state to avoid regeneration on each rerun
    if "grammar_questions" not in st.session_state:
        questions = []
        for sentence in sentences:
            # Pull the last used category or default to general
            category = st.session_state.get("last_category", "general")
            if DEBUG:
                st.write(f"DEBUG: Using category '{category}' for question generation on sentence: {sentence}")

            # Thread category into question generation

            question = generate_grammar_question(
                sentence,
                include_answer=True,
                category=category,
            )

            # Store category for continuity
            st.session_state["last_category"] = category

            if not question:
                question = {"prompt": "Could not generate question.", "options": [], "answer": ""}
            questions.append(question)
        st.session_state["grammar_questions"] = questions

    st.subheader("🧠 Identify Grammar Elements")
    questions = st.session_state["grammar_questions"]

    # Iterate over stored questions to display stable forms and persist answers/hints
    for i, question in enumerate(questions, start=1):
        sentence = sentences[i-1]
        st.markdown(f"**Sentence {i}:** {question['prompt']}")

        if not question or not question.get("prompt"):
            st.warning("Could not generate question.")
            continue

        # st.write(f"DEBUG: questions: {question["prompt"]}")
        options = question.get("options", [])
        options2 = sentence.get("options", [])
        if DEBUG:
            st.write(f"DEBUG options1: {options}")
        # st.write(f"DEBUG options2: {options2}")


        if options:
            # Initialize session state for answer, submitted, and hint if not present
            if f"ans_{i}" not in st.session_state:
                st.session_state[f"ans_{i}"] = None
            if f"submitted_{i}" not in st.session_state:
                st.session_state[f"submitted_{i}"] = False
            if f"hint_{i}" not in st.session_state:
                st.session_state[f"hint_{i}"] = ""
            if f"correct_{i}" not in st.session_state:
                st.session_state[f"correct_{i}"] = False

            # Determine if the answer was correct and disable radio if so
            # Initialize correctness state
            if f"correct_{i}" not in st.session_state:
                st.session_state[f"correct_{i}"] = False

            # If previously correct, keep it locked

            is_correct = st.session_state[f"correct_{i}"]

            # Use empty container to hold form and hint to avoid rerun issues
            container = st.empty()
            with container.form(key=f"form_{i}"):
                selected_index = (
                    options.index(st.session_state[f"ans_{i}"])
                    if st.session_state[f"ans_{i}"] in options
                    else 0
                )

                answer = st.radio(
                    "Choose an answer:",
                    options,
                    index=selected_index,
                    key=f"radio_{i}",
                    help="Hover here for a tip: think about what role the word plays in the sentence.",
                    disabled=is_correct,
                )

                # Must stay inside the form
                submitted = st.form_submit_button(f"✅ Check Answer {i}")

                if submitted:
                    current_choice = answer
                    st.session_state[f"ans_{i}"] = current_choice
                    st.session_state[f"submitted_{i}"] = True

                    if current_choice == question["answer"]:
                        st.session_state[f"hint_{i}"] = "Correct! 🎉"
                        st.session_state[f"correct_{i}"] = True
                        is_correct = True
                    else:
                        topic = current_choice.lower().strip()
                        if DEBUG:
                            st.write(f"DEBUG topic: {topic}")
                        hint = get_grammar_hint(topic)
                        st.session_state[f"hint_{i}"] = (
                            f"That's not quite right. {hint}"
                            if hint
                            else f"That's not quite right! A {topic} usually plays a specific role in the sentence."
                        )
            # Display hint or success message below the form
            if st.session_state[f"submitted_{i}"]:
                if st.session_state[f"hint_{i}"] == "Correct! 🎉":
                    st.success(st.session_state[f"hint_{i}"])
                else:
                    st.warning(st.session_state[f"hint_{i}"])
        else:
            # For free text input questions
            if f"input_{i}" not in st.session_state:
                st.session_state[f"input_{i}"] = ""
            if f"submitted_{i}" not in st.session_state:
                st.session_state[f"submitted_{i}"] = False

            user_input = st.text_input("Your answer:", key=f"input_{i}", value=st.session_state[f"input_{i}"])
            st.session_state[f"input_{i}"] = user_input
            if st.button(f"✅ Submit Answer {i}", key=f"sub_{i}"):
                st.session_state[f"submitted_{i}"] = True

            if st.session_state[f"submitted_{i}"]:
                st.info(f"The correct answer is: **{question['answer']}**")

    st.markdown("---")
    st.subheader("📘 Grammar Helper")
    user_query = st.text_input("Need help with a grammar term?", placeholder="e.g. adverb, subject, predicate...")
    if user_query:
        hint = get_grammar_hint(user_query)
        st.info(hint)
