import time

# Page of every figure and table, so a cited page can be compared with an expected figure
visual_source_pages = {
    f"{r['doc_id']}:{r['figure_id']}": (r["doc_id"], r["page"])
    for r in visual_records
}


def page_of(source):
    """Return (doc_id, page) for a source such as DOC2:p4 or DOC2:Figure A-3."""
    doc_id, name = source.split(":", 1)
    if re.fullmatch(r"p\d+", name):
        return (doc_id, int(name[1:]))
    return visual_source_pages.get(source)


def source_matches(source, expected_sources):
    """A figure or table must match exactly. A cited page matches any expected source on that page."""
    if source in expected_sources:
        return True
    if re.fullmatch(r"DOC\d:p\d+", source):
        return any(page_of(expected) == page_of(source) for expected in expected_sources)
    return False


def recall_at_5(results, expected_sources):
    """Share of the expected sources that are among the top 5 retrieved items."""
    if not expected_sources:
        return None

    top = results[:5]
    retrieved = {get_source_id(r) for r in top} | {f"{r['doc_id']}:p{r['page']}" for r in top}

    found = [source for source in expected_sources if source in retrieved]
    return len(found) / len(expected_sources)


def citation_accuracy(result, expected_sources):
    """Share of the cited sources that match an expected source."""
    citations = result.get("citations", [])
    if not citations:
        return 1.0 if not expected_sources else 0.0

    correct = sum(source_matches(c, expected_sources) for c in citations)
    return correct / len(citations)


def numbers_in(text):
    text = text.replace("−", "-")
    return [float(x) for x in re.findall(r"(?<![\w.])-?\d+(?:\.\d+)?", text)]


def answer_correct(result, item):
    """The status must be right. Numbers in the expected answer must appear in the answer (within 1%)."""
    if result.get("status") != item["expected_status"]:
        return False

    actual = result.get("answer", "").lower()

    forbidden = item.get("must_not_contain")
    if isinstance(forbidden, list) and any(text in actual for text in forbidden):
        return False

    expected_numbers = numbers_in(item["expected_answer"])
    actual_numbers = numbers_in(actual)

    if expected_numbers:
        return all(
            any(abs(found - value) <= max(0.01, abs(value) * 0.01) for found in actual_numbers)
            for value in expected_numbers
        )

    # Nothing to compare for an unanswerable question: the status is what matters
    if item["expected_status"] == "not_found":
        return True

    ignore = {"the", "a", "an", "and", "or", "is", "was", "of", "to", "in"}
    expected_words = set(re.findall(r"[a-z]+", item["expected_answer"].lower())) - ignore
    actual_words = set(re.findall(r"[a-z]+", actual))
    return not expected_words or len(expected_words & actual_words) / len(expected_words) >= 0.5


def f1_of_sets(predicted, expected):
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
    expected_labels = {s.split(":", 1)[1] for s in expected if not re.fullmatch(r"DOC\d:p\d+", s)}
    expected_citations = set(expected)
    for s in expected:
        if not re.fullmatch(r"DOC\d:p\d+", s) and page_of(s):
            expected_citations.add(f"{page_of(s)[0]}:p{page_of(s)[1]}")

    status_ok = result.get("status") == item["expected_status"]
    return (0.4 * bool(correct) + 0.2 * status_ok
            + 0.2 * f1_of_sets(result.get("figure_references", []), expected_labels)
            + 0.2 * f1_of_sets(result.get("citations", []), expected_citations))


def evaluate_system(retriever, system_name, items=None):
    rows = []
    conversation_memory.clear()

    ordered = (golden_set if items is None else items).sort_values(["conversation_id", "turn"])

    for _, item in ordered.iterrows():
        start = time.perf_counter()
        result = safe_chat_answer(item["conversation_id"], item["question"], retriever=retriever)
        seconds = time.perf_counter() - start

        correct = answer_correct(result, item)
        rows.append({
            "id": item["id"],
            "system": system_name,
            "category": item["category"],
            "question": item["question"],
            "expected_answer": item["expected_answer"],
            "actual_answer": result["answer"],
            "expected_status": item["expected_status"],
            "actual_status": result["status"],
            "correct": correct,
            "estimated_score": estimated_competition_score(result, item, correct),
            "recall_at_5": recall_at_5(result.get("retrieved", []), item["expected_sources"]),
            "citation_accuracy": citation_accuracy(result, item["expected_sources"]),
            "seconds": seconds,
            "citations": ",".join(result.get("citations", [])),
            "figure_references": ",".join(result.get("figure_references", []))
        })
        print(f"{system_name}: {item['id']} done")

    return pd.DataFrame(rows)