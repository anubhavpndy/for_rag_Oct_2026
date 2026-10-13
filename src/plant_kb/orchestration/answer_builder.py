def build_response(results):
    if not results:
        return "No matching passage found in the currently ingested files. Try different keywords or verify ingestion."
    lines = ["Retrieved source passages (verify the current approved document before operational use):"]
    for n, item in enumerate(results, 1):
        loc = item.get("source_location") or {}
        refs = []
        for key, label in (("page_number", "page"), ("sheet_name", "sheet"), ("row_number", "row"),
                           ("paragraph_number", "paragraph"), ("table_number", "table")):
            if loc.get(key) is not None: refs.append(f"{label} {loc[key]}")
        src = item.get("filename", "Unknown source")
        if refs: src += " — " + ", ".join(refs)
        lines.append(f"\n[{n}] {src}\n{item.get('chunk_text', '')}")
    return "\n".join(lines)
