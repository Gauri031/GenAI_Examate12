"""Downloads source documents into data/raw/. Run from day04/: python -m app.fetch"""
from pathlib import Path

import requests

from app.config import REQUEST_TIMEOUT

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
SOURCES = {
    "popular.html": "https://nin.res.in/popular.html",
    "DGI24thJune2024fin.pdf": "https://www.nin.res.in/dietaryguidelines/pdfjs/locale/DGI24thJune2024fin.pdf",
    "nin_home.html": "https://www.nin.res.in/",
}


def download(name, url, timeout=REQUEST_TIMEOUT):
    RAW.mkdir(parents=True, exist_ok=True)
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "PoshanGuide-student-project"})
        resp.raise_for_status()
        (RAW / name).write_bytes(resp.content)
        print(f"OK   {name} ({len(resp.content)//1024} KB)")
        return True
    except requests.exceptions.Timeout:
        print(f"FAIL {name}: timed out after {timeout}s")
    except requests.exceptions.HTTPError as e:
        print(f"FAIL {name}: HTTP error {e}")
    except requests.exceptions.RequestException as e:
        print(f"FAIL {name}: {e}")
    return False


def main():
    results = [download(n, u) for n, u in SOURCES.items()]
    print(f"{sum(results)}/{len(results)} documents downloaded")


if __name__ == "__main__":
    main()
