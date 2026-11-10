conversation_memory = {}     # conversation_id -> list of turns. Nothing here is ever written to ChromaDB.


def facts_as_context(facts):
    if not facts:
        return ""
    return "Temporary facts given by the user in this conversation:\n" + "\n".join(f"- {fact}" for fact in facts)


DOCUMENT_QUESTION = (
    r"\b(according to|in|from|what (do|does)|do|does|is it in)\b.{0,25}\b(the |your )?(documents?|document \d|briefing|supplement|knowledge base)\b"
    r"|\b(documents?|document \d|briefing b|supplement a)\b.{0,20}\b(report|say|state|show|contain|give)"
)
CALCULATION_WORDS = r"\b(how much|compare|difference|change|worse|better|more|less|larger|smaller|gap|percentage)\b"
FACT_STOP_WORDS = {"the", "a", "an", "of", "in", "for", "to", "and", "is", "was", "were", "are", "use", "used", "should", "we",
                   "what", "do", "does", "assume", "that", "this", "chat", "conversation", "only", "instead", "new", "data",
                   "point", "value", "rate", "documents", "document", "according", "us", "our"}


def asks_about_documents(question):
    """A question that asks what the documents say must not use the user's temporary facts."""
    return bool(re.search(DOCUMENT_QUESTION, question, re.IGNORECASE))


def fact_words(text):
    words = set(re.findall(r"[a-z]+|(?:19|20)\d\d", text.lower().replace("u.s.", "us").replace("'s", "")))
    return words - FACT_STOP_WORDS


def fact_applies(question, fact):
    """A temporary fact applies if the question is about the same thing (country, variable) and the same year."""
    q, f = fact_words(question), fact_words(fact)
    years_q, years_f = {w for w in q if w.isdigit()}, {w for w in f if w.isdigit()}
    if years_q and years_f and not years_q & years_f:
        return False
    return bool(f) and len(q & f) / len(f) >= 0.6


def add_document_value(result, question, retriever=hybrid_retrieve, fact=None):
    """A value given by the user is always shown next to what the documents report (answering rule 5)."""
    if "documents report" in result["answer"].lower():
        return result

    if fact:
        question = "What do the documents report about this: " + re.sub(r"-?\b\d{1,3}(?:\.\d+)?%?", "", fact)
    document_result = answer_question(question, retriever=retriever)      # no conversation facts: documents only
    if document_result["status"] == "not_found":
        reported = "the documents do not report this value."
    else:
        reported = document_result["answer"]

    answer = " ".join(f"{result['answer'].rstrip('.')}. The documents report: {reported}".split()[:120])
    return {**result, "answer": answer, "citations": document_result["citations"],
            "figure_references": document_result["figure_references"], "retrieved": document_result["retrieved"]}


def chat_answer(conversation_id, question, retriever=hybrid_retrieve):
    history = conversation_memory.setdefault(conversation_id, [])
    facts = [turn["user_fact"] for turn in history if turn["user_fact"]]
    action = classify_message(question)
    resolved_question = question
    user_fact = ""

    if action == "permanent_change":
        result = {
            "answer": "The knowledge base is read-only and cannot be changed permanently. "
                      "Values given in a chat only apply inside that conversation.",
            "status": "session_override",
            "citations": [],
            "figure_references": [],
            "retrieved": []
        }

    elif action == "override":
        fact_text, asked = split_override(question)
        user_fact, document_question = extract_override(fact_text)
        facts.append(user_fact)

        if asked:
            # The message gives a value and also asks something, so answer using the value
            resolved_question = resolve_question(asked, history)
            result = answer_question(
                resolved_question,
                conversation_context=facts_as_context(facts),
                retriever=retriever,
                retrieval_query=resolved_question + " " + document_question
            )
            if result["status"] == "answered":
                result["status"] = "session_override"
            if result["status"] == "session_override":
                result = add_document_value(result, resolved_question, retriever)
        else:
            # The message only gives a value: store it and report what the documents say
            resolved_question = document_question
            document_result = answer_question(document_question, retriever=retriever)
            if document_result["status"] == "not_found":
                reported = "the documents do not report this value."
            else:
                reported = document_result["answer"]

            result = {
                "answer": f"For this conversation, use: {user_fact}. The documents report: {reported}",
                "status": "session_override",
                "citations": document_result["citations"],
                "figure_references": document_result["figure_references"],
                "retrieved": document_result["retrieved"]
            }

    else:
        resolved_question = resolve_question(question, history)
        applicable = [fact for fact in facts if fact_applies(resolved_question, fact)]

        if asks_about_documents(question) or asks_about_documents(resolved_question) or not applicable:
            # The question is about the documents, or no temporary fact applies: the facts are left out completely
            result = answer_question(resolved_question, retriever=retriever)
        elif re.search(CALCULATION_WORDS, resolved_question, re.IGNORECASE):
            # The question needs the user's value in a calculation: the model works with it
            result = answer_question(
                resolved_question,
                conversation_context=facts_as_context(applicable),
                retriever=retriever
            )
            if result["status"] == "answered":
                result["status"] = "session_override"
            if result["status"] == "session_override":
                result = add_document_value(result, resolved_question, retriever)
        else:
            # The question asks for the value itself: use the user's value and say what the documents report
            result = add_document_value(
                {"answer": f"For this conversation, use: {applicable[-1]}.", "status": "session_override",
                 "citations": [], "figure_references": [], "retrieved": []},
                resolved_question, retriever, fact=applicable[-1]
            )

    history.append({
        "question": question,
        "resolved_question": resolved_question,
        "answer": result["answer"],
        "status": result["status"],
        "user_fact": user_fact
    })

    return result


def safe_chat_answer(conversation_id, question, retriever=hybrid_retrieve):
    """One failing question must never stop a whole run."""
    try:
        return chat_answer(conversation_id, question, retriever=retriever)
    except Exception as error:
        print("Error in", conversation_id, ":", error)
        return not_found_result("The question could not be answered because of an error.")