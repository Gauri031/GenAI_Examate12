"""Split PoshanGuide documents into chunks, keeping source, page and title (Day 07).

Supported files in documents/:
  .pdf   -> real page numbers (needs pypdf)
  .md    -> pages separated by a line:  <!-- page -->   (title = first '# ' heading)
  .txt   -> same as .md
  .json  -> a list of entries, each entry becomes one "page"

Run a quick check:  python -m app.chunking
"""
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "documents"

PAGE_MARKER = "<!-- page -->"
MAX_CHARS = 700   # target size of one chunk
OVERLAP = 120     # characters repeated from the previous chunk so context is not lost


@dataclass
class Chunk:
    id: str
    text: str
    source: str       # file name, e.g. infant_feeding.md
    page: int         # page number inside that file
    title: str        # document title
    chunk_index: int  # position of the chunk inside its page


# ---------- reading documents ----------
def _nice_title(path: Path) -> str:
    return path.stem.replace("_", " ").replace("-", " ").title()


def _read_pdf(path: Path):
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    meta_title = reader.metadata.title if reader.metadata else None
    title = (meta_title or "").strip() or _nice_title(path)
    pages = [(i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages)]
    return title, pages


def _read_text(path: Path):
    raw = path.read_text(encoding="utf-8")
    match = re.search(r"^#\s+(.+)$", raw, flags=re.MULTILINE)
    title = match.group(1).strip() if match else _nice_title(path)
    parts = raw.split(PAGE_MARKER) if PAGE_MARKER in raw else raw.split("\f")
    return title, [(i + 1, part) for i, part in enumerate(parts)]


def _read_json(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = [data]
    pages = []
    for i, entry in enumerate(data):
        if isinstance(entry, dict) and "answer" in entry:
            keys = ", ".join(entry.get("keywords", []))
            text = f"{keys}: {entry['answer']}" if keys else str(entry["answer"])
        elif isinstance(entry, dict):
            text = " ".join(str(v) for v in entry.values())
        else:
            text = str(entry)
        pages.append((i + 1, text))
    return _nice_title(path), pages


def _clean(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def load_documents(docs_dir: Path = DOCS_DIR) -> list[dict]:
    """Return one dict per page: {source, title, page, text}."""
    docs = []
    for path in sorted(Path(docs_dir).rglob("*")):
        if not path.is_file() or path.name.startswith(("_", ".")) or path.name.lower().startswith("readme"):
            continue
        ext = path.suffix.lower()
        if ext == ".pdf":
            title, pages = _read_pdf(path)
        elif ext in {".md", ".txt"}:
            title, pages = _read_text(path)
        elif ext == ".json":
            title, pages = _read_json(path)
        else:
            continue
        for page, text in pages:
            text = _clean(text)
            if text:
                docs.append({"source": path.name, "title": title, "page": page, "text": text})
    return docs


# ---------- chunking ----------
def _split_long(paragraph: str, max_chars: int) -> list[str]:
    """Split a very long paragraph at sentence ends (hard-cut if a sentence is still too long)."""
    pieces, current = [], ""
    for sentence in re.split(r"(?<=[.!?])\s+", paragraph):
        while len(sentence) > max_chars:
            if current:
                pieces.append(current)
                current = ""
            pieces.append(sentence[:max_chars])
            sentence = sentence[max_chars:]
        if current and len(current) + 1 + len(sentence) > max_chars:
            pieces.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        pieces.append(current)
    return pieces


def chunk_text(text: str, max_chars: int = MAX_CHARS, overlap: int = OVERLAP) -> list[str]:
    """Pack paragraphs into chunks of about max_chars, with a small overlap."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, current = [], ""
    for para in paragraphs:
        for piece in ([para] if len(para) <= max_chars else _split_long(para, max_chars)):
            if current and len(current) + 2 + len(piece) > max_chars:
                chunks.append(current)
                tail = current[-overlap:] if overlap else ""
                if " " in tail:
                    tail = tail[tail.find(" ") + 1:]
                current = f"{tail} {piece}".strip()
            else:
                current = f"{current}\n\n{piece}".strip()
    if current:
        chunks.append(current)
    return chunks


def chunk_documents(docs_dir: Path = DOCS_DIR) -> list[Chunk]:
    """Load every document and return all chunks with source, page, title."""
    chunks = []
    for doc in load_documents(docs_dir):
        safe_source = re.sub(r"\W+", "_", doc["source"])
        for i, piece in enumerate(chunk_text(doc["text"])):
            chunks.append(
                Chunk(
                    id=f"{safe_source}-p{doc['page']}-c{i}",
                    text=piece,
                    source=doc["source"],
                    page=doc["page"],
                    title=doc["title"],
                    chunk_index=i,
                )
            )
    return chunks


if __name__ == "__main__":
    all_chunks = chunk_documents()
    print(f"{len({c.source for c in all_chunks})} documents -> {len(all_chunks)} chunks")
    for c in all_chunks[:3]:
        print(f"\n[{c.id}] {c.title} | {c.source} | page {c.page}\n{c.text[:200]}...")
