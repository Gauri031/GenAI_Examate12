from pathlib import Path
import re
import subprocess
import sys

NEW_MODEL = "openai/gpt-oss-120b"
ROOT = Path(__file__).resolve().parents[1]

EXTENSIONS = {
    ".py", ".env", ".example", ".md",
    ".json", ".yaml", ".yml", ".toml"
}


def replace_model(path: Path) -> bool:
    content = path.read_text(encoding="utf-8")
    if path.name == "llm.py":
        updated, count = re.subn(
            r'(?m)^(\s*"model":\s*os\.getenv\("GROQ_MODEL",\s*")[^"]+("),?$',
            rf"\g<1>{NEW_MODEL}\g<2>",
            content,
        )
    elif path.name in {".env", ".env.example"}:
        updated, count = re.subn(
            r"(?m)^(\s*GROQ_MODEL=)[^\r\n]*",
            rf"\g<1>{NEW_MODEL}",
            content,
        )
    else:
        return False
    if count == 0 or updated == content:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    updated = []

    for folder in ("app", "eval"):
        directory = ROOT / folder
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix in EXTENSIONS and replace_model(path):
                updated.append(str(path.relative_to(ROOT)))

    for filename in (".env.example", ".env"):
        path = ROOT / filename
        if path.is_file() and replace_model(path):
            updated.append(filename)

    print("MODEL UPDATE COMPLETE")
    print("New model:", NEW_MODEL)
    print("Updated files:", updated)
    print("\nRunning Day 6 evaluation...\n")

    result = subprocess.run(
        [sys.executable, "eval/run_compare.py"],
        cwd=ROOT,
        check=False,
    )
    if result.returncode == 0:
        print("\nEvaluation completed. Check eval/prompt_compare.md")
    else:
        print(f"\nEvaluation failed with exit code {result.returncode}.")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
