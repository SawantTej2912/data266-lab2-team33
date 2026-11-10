# Resolve follow-up questions using only the current conversation

FOLLOW_UP_WORDS = {"that", "it", "they", "them", "those", "same", "instead", "again", "now", "then", "also", "else", "other",
                   "themselves", "itself"}


def is_follow_up(question):
    """A question probably depends on earlier turns if it is very short or points back with a word like "that"."""
    text = question.lower().strip()
    words = re.findall(r"[a-z']+", text)
    return (
        len(words) < 6
        or text.startswith(("and ", "what about", "how about", "also "))
        or any(word in FOLLOW_UP_WORDS for word in words)
    )


def resolve_question(question, history):
    """Rewrite a follow-up as a standalone question. Other questions are left exactly as they are."""
    if not history or not is_follow_up(question):
        return question

    # The most recent question comes first, because "that year" and "it" usually point to the latest turn
    previous = "\n".join(f"- {turn['resolved_question']}" for turn in reversed(history[-3:]))

    prompt = f"""
Rewrite the current question as a standalone question.

Rules:
- Keep every figure name, table name, country, variable and year that the current question already contains.
- Fill in only what is missing, using the earlier questions of this conversation.
- Words such as "that year", "then", "it" or "there" refer to the MOST RECENT earlier question, which is listed first.
- Do not answer the question. Do not add new facts.
- Return only the rewritten question.

Earlier questions (the most recent first):
{previous}

Current question:
{question}
"""

    rewritten = run_vlm(
        [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        max_new_tokens=80
    )

    # Keep the original if the rewrite is unusable or loses a figure or table name
    lost_name = any(label not in find_named_visuals(rewritten) for label in find_named_visuals(question))
    if not rewritten or len(rewritten) > 300 or lost_name:
        return question

    return rewritten