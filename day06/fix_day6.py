from pathlib import Path
import subprocess
import sys

# Retired Groq model and supported replacement
OLD_MODEL = "llama-3.3-70b-versatile"
NEW_MODEL = "openai/gpt-oss-120b"
ROOT = Path(__file__).resolve().parents[1]

EXTENSIONS = {
    ".py", ".env", ".example", ".md",
    ".json", ".yaml", ".yml", ".toml"
}


def replace_model(path: Path) -> bool:
    content = path.read_text(encoding="utf-8")
    if OLD_MODEL not in content:
        return False
    path.write_text(content.replace(OLD_MODEL, NEW_MODEL), encoding="utf-8")
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
