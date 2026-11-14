"""Download the source documents into data/raw/. Run: python -m app.fetch."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import requests

from app.config import REQUEST_TIMEOUT

DATA = Path(__file__).resolve().parent.parent / "data"
RAW = DATA / "raw"
MANIFEST = DATA / "source_manifest.json"
PDF_URL = "https://www.nin.res.in/dietaryguidelines/pdfjs/locale/DGI24thJune2024fin.pdf"
ARCHIVED_PDF_URL = (
    "https://web.archive.org/web/20260311091911id_/"
    "https://www.nin.res.in/dietaryguidelines/pdfjs/locale/DGI24thJune2024fin.pdf"
)
SOURCES = {
    "popular.html": ("https://nin.res.in/popular.html",),
    "DGI24thJune2024fin.pdf": (PDF_URL, ARCHIVED_PDF_URL),
    "nin_home.html": ("https://www.nin.res.in/",),
}


def download(name, urls, timeout=REQUEST_TIMEOUT):
    RAW.mkdir(parents=True, exist_ok=True)
    for url in urls:
        try:
            resp = requests.get(
                url,
                timeout=timeout,
                headers={"User-Agent": "PoshanGuide-student-project"},
            )
            resp.raise_for_status()
            content = resp.content
            if not content:
                raise ValueError("the response body is empty")
            if name.lower().endswith(".pdf") and not content.startswith(b"%PDF-"):
                raise ValueError("the response is not a PDF")

            (RAW / name).write_bytes(content)
            print(f"OK   {name} ({len(content) // 1024} KB) from {resp.url}")
            return {
                "file": name,
                "source_url": urls[0],
                "download_url": resp.url,
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        except requests.exceptions.Timeout:
            print(f"WARN {name}: timed out after {timeout}s at {url}")
        except requests.exceptions.HTTPError as e:
            print(f"WARN {name}: HTTP error at {url}: {e}")
        except requests.exceptions.RequestException as e:
            print(f"WARN {name}: request failed at {url}: {e}")
        except ValueError as e:
            print(f"WARN {name}: invalid response at {url}: {e}")

    print(f"FAIL {name}: all source URLs failed")
    return None


def main():
    results = [download(name, urls) for name, urls in SOURCES.items()]
    successful = [result for result in results if result is not None]
    print(f"{len(successful)}/{len(SOURCES)} documents downloaded")
    if len(successful) != len(SOURCES):
        return 1

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "documents": successful,
    }
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Saved source checksums to {MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
