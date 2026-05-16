import re

SECTION_TYPE_MAP = {
    "1": "description",
    "2": "consumable",
    "3": "special_tools",
    "4": "equipment",
    "5": "installation",
    "6": "inspection",
    "7": "repair",
    "8": "cleaning",
}

# Matches the ATA chapter number embedded in HTML comments, e.g. <!-- **72-30-01** -->
_RE_ATA_COMMENT = re.compile(r"<!--\s*\*\*(72-30-\d{2})\*\*\s*-->")

# Matches a MAINTENANCE PRACTICE(S) H1 heading that signals the start of a new component block.
# The component name is everything before " - MAINTENANCE".
_RE_MAINT_H1 = re.compile(
    r"^#\s+([A-Z][A-Z0-9 &,./\-]+?)\s*-\s*MAINTENANCE\s+PRACTICE",
    re.IGNORECASE,
)

# Matches a numbered sub-section heading (with or without leading #s).
# Captures the section number and title text.
_RE_SECTION = re.compile(r"^#{0,4}\s*(\d+)\.\s+(.+)")

MIN_CHAR_COUNT = 50


def parse_manual_sections(file_path: str) -> list[dict]:
    with open(file_path, encoding="utf-8") as fh:
        lines = fh.readlines()

    chunks: list[dict] = []

    current_ata: str | None = None
    current_component: str | None = None
    in_maint_block: bool = False

    current_section_num: str | None = None
    current_section_title: str | None = None
    current_lines: list[str] = []

    def flush_section():
        if current_section_num is None or current_ata is None or current_component is None:
            return
        text = "".join(current_lines).strip()
        if len(text) < MIN_CHAR_COUNT:
            return
        chunks.append(
            {
                "ata_chapter": current_ata,
                "component_name": current_component,
                "section_num": current_section_num,
                "section_title": current_section_title,
                "procedure_type": SECTION_TYPE_MAP.get(current_section_num, "other"),
                "text": text,
                "char_count": len(text),
            }
        )

    for raw_line in lines:
        line = raw_line.rstrip("\n")

        ata_match = _RE_ATA_COMMENT.search(line)
        if ata_match:
            current_ata = ata_match.group(1)
            continue

        maint_match = _RE_MAINT_H1.match(line.strip())
        if maint_match:
            flush_section()
            current_section_num = None
            current_section_title = None
            current_lines = []
            in_maint_block = True
            raw_name = maint_match.group(1).strip()
            current_component = re.sub(r"\s+", " ", raw_name)
            continue

        if not in_maint_block:
            continue

        section_match = _RE_SECTION.match(line.strip())
        if section_match:
            candidate_num = section_match.group(1)
            candidate_title = section_match.group(2).strip()
            if int(candidate_num) <= 10:
                flush_section()
                current_section_num = candidate_num
                current_section_title = candidate_title
                current_lines = []
                continue

        if current_section_num is not None:
            current_lines.append(raw_line)

    flush_section()
    return chunks


def get_installation_chunks(file_path: str) -> list[dict]:
    return [c for c in parse_manual_sections(file_path) if c["procedure_type"] == "installation"]


if __name__ == "__main__":
    import os

    _MANUAL_PATH = os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "KG", "压气机维修手册.md"
    )
    _MANUAL_PATH = os.path.normpath(_MANUAL_PATH)

    chunks = parse_manual_sections(_MANUAL_PATH)
    print(f"Total chunks parsed: {len(chunks)}\n")
    for c in chunks:
        print(
            f"[{c['ata_chapter']}] {c['component_name'][:40]:<40} "
            f"sec={c['section_num']} type={c['procedure_type']:<14} chars={c['char_count']}"
        )

    print(f"\nInstallation-only chunks: {len(get_installation_chunks(_MANUAL_PATH))}")
