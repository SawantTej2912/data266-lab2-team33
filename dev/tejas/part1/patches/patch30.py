"""Patch for cell 30 (hybrid retrieval): a document named in the question always contributes its best pages."""
SP = r"C:\Users\tejas\AppData\Local\Temp\claude\deab2937ad871fff\63c6304a-a82d-4ec7-8d90-b0b10b1173c2\scratchpad" + "\\"
src = open(SP + "p1_cell30.py", encoding="utf-8").read()

anchor = '''    # 3. Fill the remaining slots by score.'''
assert src.count(anchor) == 1

addition = '''    # 2b. A document that the question names (Document 1, Supplement A, Briefing B) always contributes its two
    # best-matching pages, so its own sentences are in the evidence and not only a table of another document.
    if not named:
        document_names = {
            "DOC1": r"\\bdocument 1\\b|\\bdoc1\\b",
            "DOC2": r"\\bsupplement a\\b|\\bdocument 2\\b|\\bdoc2\\b",
            "DOC3": r"\\bbriefing b\\b|\\bdocument 3\\b|\\bdoc3\\b",
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

'''
src = src.replace(anchor, addition + anchor)
open(SP + "p1_new30.py", "w", encoding="utf-8").write(src)
print("cell 30 now", len(src.splitlines()), "lines")
