# Hybrid retrieval using dense search + BM25

def find_named_visuals(query):
    """Return every Figure/Table label named in a query.

    Handles "Figure A-2", "Figures A-6 and A-7", "Tables 1-1, 1-2" and "Figure B-5 (corrected)".
    """
    pattern = (
        r"\b(corrected\s+)?(Figure|Table)s?\s+"
        r"((?:[12A-C]-\d+(?:\s*\(corrected\))?(?:\s*(?:,|/|&|and|or)\s*)*)+)"
    )

    labels = []
    for prefix, kind, ids in re.findall(pattern, query, re.IGNORECASE):
        for number, suffix in re.findall(r"([12A-C]-\d+)(\s*\(corrected\))?", ids, re.IGNORECASE):
            label = f"{kind.capitalize()} {number.upper()}"
            if prefix or suffix:
                label += " (corrected)"
            if label not in labels:
                labels.append(label)
    return labels


def hybrid_retrieve(query, top_k=5, max_visuals=2):
    query_embedding = embedding_model.encode(
        [query],
        normalize_embeddings=True
    )[0]

    dense_order = chroma_dense_order(query_embedding)
    bm25_scores = bm25.get_scores(tokenize(query))
    bm25_order = np.argsort(bm25_scores)[::-1]

    # Reciprocal Rank Fusion of the dense (ChromaDB) and keyword (BM25) rankings
    scores = np.zeros(len(all_items))

    for rank, idx in enumerate(dense_order):
        scores[idx] += 1 / (60 + rank + 1)

    for rank, idx in enumerate(bm25_order):
        scores[idx] += 1 / (60 + rank + 1)

    # Lookups. Low-trust content is left out, so it can never become evidence.
    visual_index = {}
    page_index = {}
    table_index = {}
    for i, item in enumerate(all_items):
        if item["trust_level"] == "low":
            continue
        if item["type"] == "visual":
            visual_index[item["figure_id"]] = i
        elif item["type"] == "page":
            page_index[(item["doc_id"], item["page"])] = i
        elif item["type"] == "table":
            table_index[item["figure_id"]] = i

    selected = []
    seen = set()

    def add(i):
        # One record per visual and one per page, so duplicates do not use up top_k
        item = all_items[i]
        key = item["figure_id"] or (item["doc_id"], item["page"])
        if key not in seen:
            seen.add(key)
            selected.append(i)

    def add_text_evidence(i):
        # A table's exact text is used before the page it sits on.
        # Another match from the same page then adds the rest of the page.
        item = all_items[i]
        if item["type"] == "table":
            add(i)
            return
        key = (item["doc_id"], item["page"])
        for label in page_tables.get(key, []):
            if label not in seen:
                add(table_index[label])
                return
        add(page_index[key])

    # 1. Objects named in the query always come first, followed by the pages they are on.
    # A corrected figure replaces its original, unless the query asks for the original
    # or names both versions.
    named = find_named_visuals(query)
    asks_for_original = re.search(r"original|uncorrected|before the correction", query, re.IGNORECASE)

    named_found = []
    for label in named:
        corrected = label + " (corrected)"
        if corrected in visual_index and corrected not in named and not asks_for_original:
            label = corrected
        if label in visual_index and label not in named_found:
            named_found.append(label)

    for label in named_found:
        add(visual_index[label])
    for label in named_found:
        item = all_items[visual_index[label]]
        add(page_index[(item["doc_id"], item["page"])])

    order = np.argsort(scores)[::-1]

    # 2. Source diversity: without named objects, each trusted document gets one slot first,
    # so one document cannot crowd out another. If the query mentions a year, the slot goes
    # to the document's best table row with that year. Otherwise it goes to its best text or table.
    if not named:
        years = re.findall(r"\b(?:19|20)\d\d\b", query)
        docs_covered = set()

        for only_rows_with_year in (True, False):
            for i in order:
                item = all_items[i]
                if item["type"] == "visual" or item["trust_level"] == "low" or item["doc_id"] in docs_covered:
                    continue
                if only_rows_with_year and not (item["type"] == "table" and any(y in item["content"] for y in years)):
                    continue
                docs_covered.add(item["doc_id"])
                add_text_evidence(i)

    # 2b. A document that the question names (Document 1, Supplement A, Briefing B) always contributes its two
    # best-matching pages, so its own sentences are in the evidence and not only a table of another document.
    if not named:
        document_names = {
            "DOC1": r"\bdocument 1\b|\bdoc1\b",
            "DOC2": r"\bsupplement a\b|\bdocument 2\b|\bdoc2\b",
            "DOC3": r"\bbriefing b\b|\bdocument 3\b|\bdoc3\b",
        }
        for doc_id, pattern in document_names.items():
            if re.search(pattern, query, re.IGNORECASE):
                pages_added = 0
                for i in order:
                    item = all_items[i]
                    if item["doc_id"] == doc_id and item["type"] == "page" and item["trust_level"] != "low":
                        add(i)
                        pages_added += 1
                        if pages_added == 2:
                            break

    # 3. Fill the remaining slots by score.
    # When objects are named, no other visuals are added, so look-alike figures are not mixed in.
    visual_count = len(named_found)

    for i in order:
        if len(selected) >= top_k:
            break

        item = all_items[i]

        if item["trust_level"] == "low":
            continue

        if item["type"] == "visual":
            if named or visual_count >= max_visuals:
                continue
            # Use the corrected version of a visual when one exists
            i = visual_index.get(item["figure_id"] + " (corrected)", i)
            if all_items[i]["figure_id"] not in seen:
                visual_count += 1
            add(i)
        elif named:
            # Named objects are the main evidence: other tables are not added
            if item["type"] != "table":
                add(page_index[(item["doc_id"], item["page"])])
        else:
            add_text_evidence(i)

    results = []
    for i in selected:
        result = {**all_items[i], "score": float(scores[i])}
        key = (result["doc_id"], result["page"])

        # A matching table row brings in the complete table
        if result["type"] == "table":
            result["content"] = table_text[result["figure_id"]]

        # Show each table's numbers once: as exact text, not also as loose page text
        if result["type"] == "page" and key in page_tables and all(label in seen for label in page_tables[key]):
            result["content"] = pages_without_tables[key]

        results.append(result)

    return results