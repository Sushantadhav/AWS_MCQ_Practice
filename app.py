
import streamlit as st
import json
import random

st.set_page_config(
    page_title="AWS MCQ Practice",
    page_icon="📝",
    layout="centered"
)

st.title("AWS Cloud Practitioner")
st.caption("Randomized MCQ Practice Portal")

# ---------- SELECT SET ----------
set_number = st.selectbox(
    "Select Question Set",
    range(1, 9),
    format_func=lambda x: f"Set {x}"
)

with open(
    f"question_sets/set_{set_number}.json",
    "r",
    encoding="utf-8"
) as f:
    questions = json.load(f)

total = len(questions)

# ---------- INITIALIZE / RESET SET ----------
if st.session_state.get("active_set") != set_number:
    st.session_state.active_set = set_number
    st.session_state.question_order = random.sample(
        range(total), total
    )
    st.session_state.current = 0
    st.session_state.answers = {}
    st.session_state.submitted = False

# First-time initialization
if "question_order" not in st.session_state:
    st.session_state.active_set = set_number
    st.session_state.question_order = random.sample(
        range(total), total
    )
    st.session_state.current = 0
    st.session_state.answers = {}
    st.session_state.submitted = False

# ---------- GET RANDOMIZED QUESTION ----------
current = st.session_state.current
original_index = st.session_state.question_order[current]
q = questions[original_index]

# ---------- RESULT PAGE ----------
if st.session_state.submitted:

    correct_count = 0
    wrong_count = 0
    unanswered = 0

    for position, original_index in enumerate(
        st.session_state.question_order
    ):
        user_answer = sorted(
            st.session_state.answers.get(original_index, [])
        )

        correct_answer = sorted(
            questions[original_index]["correct_answer"]
        )

        if not user_answer:
            unanswered += 1
        elif user_answer == correct_answer:
            correct_count += 1
        else:
            wrong_count += 1

    score = (correct_count / total) * 100

    st.success("Test Submitted Successfully!")

    st.metric("Final Score", f"{score:.2f} / 100")

    col1, col2, col3 = st.columns(3)
    col1.metric("Correct", correct_count)
    col2.metric("Wrong", wrong_count)
    col3.metric("Skipped", unanswered)

    st.divider()
    st.header("Answer Review")

    for position, original_index in enumerate(
        st.session_state.question_order
    ):
        review_q = questions[original_index]

        user_answer = sorted(
            st.session_state.answers.get(original_index, [])
        )

        correct_answer = sorted(
            review_q["correct_answer"]
        )

        with st.expander(f"Question {position + 1}"):

            st.write(review_q["question"])

            for letter, option in review_q["options"].items():

                if letter in correct_answer:
                    st.success(
                        f"{letter}. {option} — Correct Answer"
                    )

                elif letter in user_answer:
                    st.error(
                        f"{letter}. {option} — Your Answer"
                    )

                else:
                    st.write(f"{letter}. {option}")

            if not user_answer:
                st.warning("Not attempted")

            elif user_answer == correct_answer:
                st.success("Your answer is correct.")

            else:
                st.error(
                    "Your answer: " + ", ".join(user_answer)
                )

    if st.button("Start New Random Test"):
        st.session_state.question_order = random.sample(
            range(total), total
        )
        st.session_state.current = 0
        st.session_state.answers = {}
        st.session_state.submitted = False
        st.rerun()

# ---------- QUESTION PAGE ----------
else:

    st.progress((current + 1) / total)

    st.write(f"Question {current + 1} of {total}")

    st.divider()

    st.subheader(q["question"])

    options = q["options"]

    previous_answer = st.session_state.answers.get(
        original_index, []
    )

    # Single-answer question
    if len(q["correct_answer"]) == 1:

        selected = st.radio(
            "Select your answer:",
            list(options.keys()),
            format_func=lambda x: f"{x}. {options[x]}",
            index=(
                list(options.keys()).index(previous_answer[0])
                if previous_answer
                and previous_answer[0] in options
                else None
            ),
            key=f"radio_{set_number}_{original_index}"
        )

        user_answer = [selected] if selected else []

    # Multiple-answer question
    else:

        st.info("Select all correct options.")

        user_answer = []

        for letter, option in options.items():

            checked = st.checkbox(
                f"{letter}. {option}",
                value=letter in previous_answer,
                key=f"check_{set_number}_{original_index}_{letter}"
            )

            if checked:
                user_answer.append(letter)

    # Save answer against original question
    st.session_state.answers[original_index] = user_answer

    # Check whether current question is attempted
    is_answered = len(user_answer) > 0

    st.divider()

    # Count attempted questions
    answered_count = sum(
        bool(answer)
        for answer in st.session_state.answers.values()
    )

    st.caption(f"Answered: {answered_count} / {total}")

    # ---------- NAVIGATION ----------
    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "← Previous",
            disabled=current == 0,
            use_container_width=True
        ):
            st.session_state.current -= 1
            st.rerun()

    with col2:

        if current < total - 1:

            if st.button(
                "Next →",
                type="primary",
                disabled=not is_answered,
                use_container_width=True
            ):
                st.session_state.current += 1
                st.rerun()

        else:
            st.warning("You have reached the last question.")

    # ---------- SUBMIT TEST ----------
    st.divider()

    if st.button(
        "Submit Test",
        type="primary",
        disabled=(
            answered_count != total
            or not is_answered
        ),
        use_container_width=True
    ):
        st.session_state.submitted = True
        st.rerun()