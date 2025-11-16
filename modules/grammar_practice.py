import streamlit as st
from utils.llm_helpers import generate_grammar_question, get_grammar_hint, generate_sentences_from_topics, get_available_categories
from utils.db import log_attempt
from config.logger import log
from utils.text_utils import normalize_answer

DEBUG = False  # Set to False to disable debug logs

def get_hint_topic(selected_answer, question_topic):
    from utils.llm_helpers import get_grammar_hint
    st.write(f"DEBUG (hint resolver): trying selected='{selected_answer}', fallback='{question_topic}'")
    log.debug(f"DEBUG (hint resolver): trying selected='{selected_answer}', fallback='{question_topic}'")

    # Step 1: Try selected answer
    hint = get_grammar_hint(selected_answer)
    st.write(f"DEBUG (hint returned): hint: {hint}")
    log.debug(f"DEBUG (hint returned): hint: {hint}")
    if hint and not hint.lower().startswith("Remember, think about how the word is used"):
        if not any(kw in hint.lower() for kw in ["sentence", "example", "word", "topic"]):
            return hint

    # Step 2: Fallback to actual topic
    if question_topic:
        fallback_hint = get_grammar_hint(question_topic)
        if fallback_hint and "not quite right" not in fallback_hint.lower():
            return fallback_hint

    # Step 3: Final fallback
    return "That's not quite right! Remember to think about how punctuation or structure affects the sentence."

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
        # Use questions directly from the topic-based generator
        questions = sentences  # These already include topic, question, options, and answer
        for q in questions:
            # Prefer the category returned by the generator
            if "category" not in q or not q["category"]:
                q["category"] = chosen_category or "general"

        # Preserve only the last used category for session continuity
        if questions:
            st.session_state["last_category"] = chosen_category or questions[-1].get("category", "general")

        st.session_state["grammar_questions"] = questions

    st.subheader("🧠 Identify Grammar Elements")
    questions = st.session_state["grammar_questions"]

    # Iterate over stored questions to display stable forms and persist answers/hints
    for i, question in enumerate(questions, start=1):
        sentence = sentences[i-1]
        category_label = question.get('category', 'General').replace('_', ' ').title()
        st.markdown(f"**Sentence {i}\n:** {question['question']}")

        if not question or not question.get("question"):
            st.warning("Could not generate question.")
            continue

        options = question.get("options", [])
        options2 = sentence.get("options", [])


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

                    if normalize_answer(current_choice, question.get("topic", "")) == normalize_answer(question["answer"], question.get("topic", "")):
                        st.session_state[f"hint_{i}"] = "Correct! 🎉"
                        st.session_state[f"correct_{i}"] = True
                        is_correct = True
                    else:
                        topic = current_choice.lower().strip()
                        question_topic = question.get("topic")
                        st.write(f"DEBUG: topic: {topic}")
                        log.debug(f"DEBUG: topic: {topic}")

                        if DEBUG:
                            st.write(f"DEBUG topic: {topic}")
                            log.debug(f"DEBUG topic: {topic}")
                        st.write(f"DEBUG: topic: {topic}, question_topic: {question_topic}")
                        log.debug(f"DEBUG: topic: {topic}, question_topic: {question_topic}")
                        hint = get_hint_topic(topic, question_topic)
                        st.session_state[f"hint_{i}"] = (
                            f"That's not quite right (grammar_practice hint). {hint}"
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

            default_value = st.session_state.get(f"input_{i}", "")
            user_input = st.text_input("Your answer:", key=f"input_{i}", value=default_value)
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
