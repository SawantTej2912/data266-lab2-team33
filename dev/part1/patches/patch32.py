"""Apply the improvements to the answer-generation cell (cell 32) of the Part 1 notebook.

Reads  p1_cell32.py  (the original cell) and writes  p1_new32.py. Every change is anchored to the original text.
"""
SP = r"C:\Users\tejas\AppData\Local\Temp\claude\deab2937ad871fff\63c6304a-a82d-4ec7-8d90-b0b10b1173c2\scratchpad" + "\\"
src = open(SP + "p1_cell32.py", encoding="utf-8").read()


def replace(old, new, count=1):
    global src
    assert src.count(old) == count, f"anchor found {src.count(old)} times: {old[:60]!r}"
    src = src.replace(old, new)


# ---------------------------------------------------------------- 1. not_found answers must read like not_found
replace('''def not_found_result(answer):
    # The model sometimes writes the status name itself as the answer
    if answer.strip().lower() in {"", "not_found", "not found"}:
        answer = "The documents do not contain this information."
''', '''NOT_FOUND_PHRASES = (
    r"\\b(do(es)? not|don't|cannot|can't|unable|not (available|reported|provided|supported|found|mentioned|"
    r"contain|include|give|given|specified|covered)|no (information|data|value|mention|evidence))\\b"
)


def says_not_found(answer):
    """True if the answer reads like "the documents do not say" instead of stating a value."""
    text = answer.strip().lower().rstrip(".")
    return text in {"no", "none", "not found", "not_found"} or bool(re.search(NOT_FOUND_PHRASES, text))


def not_found_result(answer):
    # A not_found answer must say that the documents do not contain it. A bare "No" or a status name is not enough
    if len(answer.split()) < 5 or not says_not_found(answer):
        answer = "The documents do not contain this information."
''')

# ---------------------------------------------------------------- 2. a real answer with a stray not_found status
replace('''    if status == "not_found":
        return not_found_result(answer)

    answer = apply_calculation(answer, parsed.get("calculation"))''', '''    if status == "not_found":
        # The model sometimes writes a real answer and still says not_found. If the answer states a number that the
        # evidence really contains, the answer is kept and the status becomes "answered".
        in_evidence = [
            r for r in results
            if r["type"] != "visual" and any(
                re.search(rf"(?<![\\d.]){re.escape(n)}(?![\\d.])", r["content"])
                for n in re.findall(r"(?<![\\d.])\\d{1,3}(?:\\.\\d+)?(?![\\d.])", answer)
            )
        ]
        if says_not_found(answer) or not in_evidence:
            return not_found_result(answer)
        status = "answered"

    answer = apply_calculation(answer, parsed.get("calculation"))''')

# ---------------------------------------------------------------- 3. a cited table or figure is cited with its page
replace('''    # Figure references always come from the checked citations
    figure_references = [
        evidence[c]["figure_id"] for c in citations if evidence[c]["figure_id"]
    ]
''', '''    # Figure references always come from the checked citations
    figure_references = [
        evidence[c]["figure_id"] for c in citations if evidence[c]["figure_id"]
    ]

    # A table or figure is cited together with its page, as in the sample submission (DOC1:Table 1-1,DOC1:p1)
    for c in list(citations):
        page_source = f"{evidence[c]['doc_id']}:p{evidence[c]['page']}"
        if evidence[c]["figure_id"] and page_source not in citations:
            citations.append(page_source)
''')

# ---------------------------------------------------------------- 4. answer prompt: complete answers, name the replaced value
replace('''- Write one or two complete sentences that contain the key numbers and years. Do not answer with only a number, "Yes" or "No".''',
        '''- Answer the question completely in two to four sentences. Give the key numbers and years. When the question asks why or how, give the reasons or the explanation that the evidence states. Never answer with only a number, "Yes" or "No".
- When the answer is an outturn, a revised value or a corrected figure, you MUST also say which value it replaces, for example "2.4% (revised in July 2013, replacing 3.0%)".
- If an exact table gives the value, use the table and not a rough statement in the text.''')

# ---------------------------------------------------------------- 5. the checks after the first answer
replace('''def answer_question(
    question,''', '''def build_text_evidence(results):
    """The evidence as text only (pages and tables), for the short checks below."""
    content = []
    for r in results:
        if r["type"] == "visual":
            continue
        header = f"\\nSOURCE_ID: {get_source_id(r)} | TRUST: {r['trust_level']}\\n"
        content.append({"type": "text", "text": header + r["content"] + "\\n"})
    return content


def ask_json(instructions, results, max_new_tokens=200):
    """One short question about the evidence. Returns the JSON object of the reply, or an empty dict."""
    content = [{"type": "text", "text": instructions + "\\nEVIDENCE:\\n"}] + build_text_evidence(results)
    content.append({"type": "text", "text": "\\nReturn ONLY the JSON."})
    output = run_vlm([{"role": "user", "content": content}], max_new_tokens=max_new_tokens)
    match = re.search(r"\\{.*\\}", output, re.DOTALL)
    try:
        parsed = json.loads(match.group(0)) if match else {}
    except json.JSONDecodeError:
        parsed = {}
    return parsed if isinstance(parsed, dict) else {}


PREMISE_CHECK = """You check the assumptions of a question. Reply with JSON only.

QUESTION: {question}

Task: does the question take for granted something (for example that a value rose, fell, was above a level, or that an event happened) that the EVIDENCE clearly contradicts?
- Answer true only if a number in the evidence contradicts the assumption.
- A question that simply asks for a value, or asks why about something that really happened, is NOT a false premise.

Return: {{"false_premise": true or false, "correct_fact": "<one sentence with the number from the evidence>", "source": "<SOURCE_ID>"}}
"""

CONFLICT_CHECK = """You compare sources. Reply with JSON only.

QUESTION: {question}

Task: do two TRUSTED sources report DIFFERENT numbers for exactly the quantity that the question asks about (the same country or region, the same variable and the same year)?
- An outturn that replaces a forecast (marked *), a stated revision and a corrected figure are updates, NOT conflicts.
- Different years, countries, definitions or samples are NOT conflicts.
- Use only numbers that are written in the sources.

Return: {{"conflict": true or false, "quantity": "<what the question asks, for example the inflation rate of Canada in 1999>", "values": [{{"source": "<SOURCE_ID>", "value": "<number as written>"}}]}}
Give two or more entries in "values" only when conflict is true.
"""

TRUST_RANK = {"high": 3, "medium": 2, "low": 1}


def number_in_source(value, record):
    """The value must really be written in that source (a page, an exact table)."""
    numbers = re.findall(r"-?\\d+(?:\\.\\d+)?", str(value).replace("\\u2212", "-"))
    text = record["content"].replace("\\u2212", "-")
    return bool(numbers) and all(re.search(rf"(?<![\\d.]){re.escape(n.lstrip('-'))}(?![\\d.])", text) for n in numbers[:1])


def with_pages(sources, evidence):
    out = []
    for s in sources:
        out.append(s)
        page = f"{evidence[s]['doc_id']}:p{evidence[s]['page']}"
        if evidence[s]["figure_id"] and page not in out:
            out.append(page)
    return out


def verify_result(result, question, results):
    """Two short checks on an answer: a false premise, and two trusted sources that disagree.

    A check only changes the answer if what the model reports can be found in the evidence it points to."""
    if result["status"] != "answered" or find_named_visuals(question):
        return result

    evidence = {get_source_id(r): r for r in results if r["trust_level"] != "low"}

    # 1. false premise
    check = ask_json(PREMISE_CHECK.format(question=question), results)
    source = check.get("source")
    fact = check.get("correct_fact")
    if check.get("false_premise") is True and source in evidence and isinstance(fact, str) and number_in_source(
        next(iter(re.findall(r"-?\\d+(?:\\.\\d+)?", fact)), ""), evidence[source]
    ):
        citations = with_pages([source], evidence)
        return {**result, "answer": f"The question assumes something that is not true. {fact}", "status": "false_premise",
                "citations": citations, "figure_references": [evidence[c]["figure_id"] for c in citations if evidence[c]["figure_id"]]}

    # 2. two trusted sources with different values
    check = ask_json(CONFLICT_CHECK.format(question=question), results, max_new_tokens=250)
    values = check.get("values") if check.get("conflict") is True else None
    if isinstance(values, list):
        found = {}
        for entry in values:
            if isinstance(entry, dict) and entry.get("source") in evidence and number_in_source(entry.get("value"), evidence[entry["source"]]):
                found.setdefault(evidence[entry["source"]]["doc_id"], (entry["source"], str(entry["value"]).strip()))
        numbers = {re.sub(r"[^\\d.\\-]", "", v) for _, v in found.values()}
        if len(found) >= 2 and len(numbers) >= 2:
            ranked = sorted(found.values(), key=lambda sv: -TRUST_RANK[evidence[sv[0]]["trust_level"]])
            best, other = ranked[0], ranked[1]
            quantity = check.get("quantity") if isinstance(check.get("quantity"), str) else "this value"
            answer = (
                f"The sources disagree about {quantity}. {evidence[best[0]]['doc_id']} reports {best[1]}, "
                f"but {evidence[other[0]]['doc_id']} reports {other[1]}. "
                f"{evidence[best[0]]['doc_id']} has the higher trust level, so {best[1]} is preferred."
            )
            citations = with_pages([best[0], other[0]], evidence)
            return {**result, "answer": answer, "status": "conflict", "citations": citations,
                    "figure_references": [evidence[c]["figure_id"] for c in citations if evidence[c]["figure_id"]]}

    return result


def answer_question(
    question,''')

replace('''    result = clean_result(parse_model_output(output), evidence_items, question, has_facts=bool(conversation_context))
    result["retrieved"] = results''', '''    result = clean_result(parse_model_output(output), evidence_items, question, has_facts=bool(conversation_context))

    # Facts given by the user are not document evidence, so the checks only run on questions about the documents
    if not conversation_context:
        result = confirm_existence(result, question, evidence_items)
        result = check_false_premise(result, question, evidence_items)
        result = rescue_not_found(result, question, evidence_items)
        result = check_conflict(result, question, evidence_items)
        result = add_replaced_value(result, question, evidence_items)
    result["retrieved"] = results''')


# ---------------------------------------------------------------- 6. the exact table lines that best match the question
replace('''    content += build_evidence(evidence_items)
    content.append({"type": "text", "text": f"\\nQUESTION:\\n{question}\\n\\nReturn ONLY the JSON."})''', '''    content += build_evidence(evidence_items)
    key_lines = key_table_lines(question, evidence_items)
    if key_lines:
        content.append({"type": "text", "text": "\\nKEY TABLE LINES (exact table lines that match the words and the year of the question; use them if they answer it, otherwise use the rest of the evidence, which also includes text):\\n" + "\\n".join(key_lines) + "\\n"})
    content.append({"type": "text", "text": f"\\nQUESTION:\\n{question}\\n\\nReturn ONLY the JSON."})''')

open(SP + "p1_new32.py", "w", encoding="utf-8").write(src)
print("patched cell 32:", len(src.splitlines()), "lines")
