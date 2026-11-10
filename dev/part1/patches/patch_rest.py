"""Patches for cells 34 (follow-ups), 36 (conversation handling) and 45 (evaluation) of the Part 1 notebook."""
SP = r"C:\Users\tejas\AppData\Local\Temp\claude\deab2937ad871fff\63c6304a-a82d-4ec7-8d90-b0b10b1173c2\scratchpad" + "\\"


def patch(name_in, name_out, edits):
    src = open(SP + name_in, encoding="utf-8").read()
    for old, new in edits:
        assert src.count(old) == 1, f"{name_in}: anchor found {src.count(old)} times: {old[:60]!r}"
        src = src.replace(old, new)
    open(SP + name_out, "w", encoding="utf-8").write(src)
    print(name_out, len(src.splitlines()), "lines")


# ---------------------------------------------------------------- cell 34: follow-up questions
patch("p1_cell34.py", "p1_new34.py", [
    ('''FOLLOW_UP_WORDS = {"that", "it", "they", "them", "those", "same", "instead", "again", "now", "then", "also", "else", "other"}''',
     '''FOLLOW_UP_WORDS = {"that", "it", "they", "them", "those", "same", "instead", "again", "now", "then", "also", "else", "other",
                   "themselves", "itself"}'''),
    ('''    previous = "\\n".join(f"- {turn['resolved_question']}" for turn in history[-3:])''',
     '''    # The most recent question comes first, because "that year" and "it" usually point to the latest turn
    previous = "\\n".join(f"- {turn['resolved_question']}" for turn in reversed(history[-3:]))'''),
    ('''- Fill in only what is missing, using the earlier questions of this conversation.''',
     '''- Fill in only what is missing, using the earlier questions of this conversation.
- Words such as "that year", "then", "it" or "there" refer to the MOST RECENT earlier question, which is listed first.'''),
    ('''Earlier questions:
{previous}''', '''Earlier questions (the most recent first):
{previous}'''),
])

# ---------------------------------------------------------------- cell 36: a session value is shown next to the document value
patch("p1_cell36.py", "p1_new36.py", [
    ('''def chat_answer(conversation_id, question, retriever=hybrid_retrieve):''',
     '''def add_document_value(result, question, retriever=hybrid_retrieve):
    """A value given by the user is always shown next to what the documents report (answering rule 5)."""
    if "documents report" in result["answer"].lower():
        return result

    document_result = answer_question(question, retriever=retriever)      # no conversation facts: documents only
    if document_result["status"] == "not_found":
        reported = "the documents do not report this value."
    else:
        reported = document_result["answer"]

    answer = " ".join(f"{result['answer'].rstrip('.')}. The documents report: {reported}".split()[:120])
    return {**result, "answer": answer, "citations": document_result["citations"],
            "figure_references": document_result["figure_references"], "retrieved": document_result["retrieved"]}


def chat_answer(conversation_id, question, retriever=hybrid_retrieve):'''),
    ('''            if result["status"] == "answered":
                result["status"] = "session_override"
''', '''            if result["status"] == "answered":
                result["status"] = "session_override"
            if result["status"] == "session_override":
                result = add_document_value(result, resolved_question, retriever)
'''),
    ('''        result = answer_question(
            resolved_question,
            conversation_context=facts_as_context(facts),
            retriever=retriever
        )

    history.append({''', '''        result = answer_question(
            resolved_question,
            conversation_context=facts_as_context(facts),
            retriever=retriever
        )
        if result["status"] == "session_override":
            result = add_document_value(result, resolved_question, retriever)

    history.append({'''),
])

# ---------------------------------------------------------------- cell 45: evaluate any question set, and a local proxy of the competition score
patch("p1_cell45.py", "p1_new45.py", [
    ('''def evaluate_system(retriever, system_name):
    rows = []
    conversation_memory.clear()

    ordered = golden_set.sort_values(["conversation_id", "turn"])
''', '''def f1_of_sets(predicted, expected):
    """Overlap of two sets of labels. Two empty sets match perfectly."""
    predicted, expected = set(predicted), set(expected)
    if not predicted and not expected:
        return 1.0
    hits = len(predicted & expected)
    if not hits:
        return 0.0
    precision, recall = hits / len(predicted), hits / len(expected)
    return 2 * precision * recall / (precision + recall)


def estimated_competition_score(result, item, correct):
    """A rough local version of the competition score: 0.4 answer + 0.2 status + 0.2 figure references + 0.2 citations.

    The expected citations are the expected sources plus the page of every expected table or figure, which is the
    format of the sample submission. It is only an estimate, because the real answer key is hidden."""
    expected = item["expected_sources"]
    expected_labels = {s.split(":", 1)[1] for s in expected if not re.fullmatch(r"DOC\\d:p\\d+", s)}
    expected_citations = set(expected)
    for s in expected:
        if not re.fullmatch(r"DOC\\d:p\\d+", s) and page_of(s):
            expected_citations.add(f"{page_of(s)[0]}:p{page_of(s)[1]}")

    status_ok = result.get("status") == item["expected_status"]
    return (0.4 * bool(correct) + 0.2 * status_ok
            + 0.2 * f1_of_sets(result.get("figure_references", []), expected_labels)
            + 0.2 * f1_of_sets(result.get("citations", []), expected_citations))


def evaluate_system(retriever, system_name, items=None):
    rows = []
    conversation_memory.clear()

    ordered = (golden_set if items is None else items).sort_values(["conversation_id", "turn"])
'''),
    ('''        rows.append({
            "id": item["id"],''', '''        correct = answer_correct(result, item)
        rows.append({
            "id": item["id"],'''),
    ('''            "correct": answer_correct(result, item),''', '''            "correct": correct,
            "estimated_score": estimated_competition_score(result, item, correct),'''),
])
