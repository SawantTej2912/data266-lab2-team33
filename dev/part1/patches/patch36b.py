"""Second pass on cell 36: questions about the documents ignore the user's temporary facts, and a fact that
applies to the question is used and shown next to what the documents report."""
SP = r"C:\Users\tejas\AppData\Local\Temp\claude\deab2937ad871fff\63c6304a-a82d-4ec7-8d90-b0b10b1173c2\scratchpad" + "\\"
src = open(SP + "p1_new36.py", encoding="utf-8").read()


def replace(old, new):
    global src
    assert src.count(old) == 1, f"anchor found {src.count(old)} times: {old[:60]!r}"
    src = src.replace(old, new)


replace('''def add_document_value(result, question, retriever=hybrid_retrieve):''', '''DOCUMENT_QUESTION = (
    r"\\b(according to|in|from|what (do|does)|do|does|is it in)\\b.{0,25}\\b(the |your )?(documents?|document \\d|briefing|supplement|knowledge base)\\b"
    r"|\\b(documents?|document \\d|briefing b|supplement a)\\b.{0,20}\\b(report|say|state|show|contain|give)"
)
CALCULATION_WORDS = r"\\b(how much|compare|difference|change|worse|better|more|less|larger|smaller|gap|percentage)\\b"
FACT_STOP_WORDS = {"the", "a", "an", "of", "in", "for", "to", "and", "is", "was", "were", "are", "use", "used", "should", "we",
                   "what", "do", "does", "assume", "that", "this", "chat", "conversation", "only", "instead", "new", "data",
                   "point", "value", "rate", "documents", "document", "according", "us", "our"}


def asks_about_documents(question):
    """A question that asks what the documents say must not use the user's temporary facts."""
    return bool(re.search(DOCUMENT_QUESTION, question, re.IGNORECASE))


def fact_words(text):
    words = set(re.findall(r"[a-z]+|(?:19|20)\\d\\d", text.lower().replace("u.s.", "us").replace("'s", "")))
    return words - FACT_STOP_WORDS


def fact_applies(question, fact):
    """A temporary fact applies if the question is about the same thing (country, variable) and the same year."""
    q, f = fact_words(question), fact_words(fact)
    years_q, years_f = {w for w in q if w.isdigit()}, {w for w in f if w.isdigit()}
    if years_q and years_f and not years_q & years_f:
        return False
    return bool(f) and len(q & f) / len(f) >= 0.6


def add_document_value(result, question, retriever=hybrid_retrieve, fact=None):''')

# the question about the documents is built from the user's fact (without the user's number) when there is one
replace('''    document_result = answer_question(question, retriever=retriever)      # no conversation facts: documents only''',
        '''    if fact:
        question = "What do the documents report about this: " + re.sub(r"-?\\b\\d{1,3}(?:\\.\\d+)?%?", "", fact)
    document_result = answer_question(question, retriever=retriever)      # no conversation facts: documents only''')
replace('''        resolved_question = resolve_question(question, history)
        result = answer_question(
            resolved_question,
            conversation_context=facts_as_context(facts),
            retriever=retriever
        )
        if result["status"] == "session_override":
            result = add_document_value(result, resolved_question, retriever)
''', '''        resolved_question = resolve_question(question, history)
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
''')
open(SP + "p1_new36.py", "w", encoding="utf-8").write(src)
print("cell 36 now", len(src.splitlines()), "lines")
