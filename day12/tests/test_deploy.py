"""Deployment config: small checks that keep the public deploy and the CI working."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


def test_dockerfile_listens_on_the_port_given_by_the_host():
    text = read("Dockerfile")
    assert "${PORT:-8000}" in text      # Render sets PORT, Hugging Face and local Docker use 8000
    assert "0.0.0.0" in text


def test_dockerfile_does_not_run_as_root():
    assert "USER app" in read("Dockerfile")


def test_dockerignore_keeps_secrets_out_of_the_image():
    lines = read(".dockerignore").splitlines()
    assert ".env" in lines
    assert ".git" in lines


def test_env_example_has_no_real_key():
    text = read(".env.example")
    assert "GROQ_API_KEY=your_groq_key_here" in text
    assert "gsk_" not in text           # real Groq keys start with gsk_


def test_ci_workflow_runs_ruff_pytest_and_docker_build():
    ci = ROOT.parent / ".github" / "workflows" / "ci.yml"
    if not ci.exists():
        pytest.skip("ci.yml is at the repo root, so it is not there when this folder is deployed alone")
    text = ci.read_text(encoding="utf-8")
    for word in ("ruff check", "pytest", "docker build"):
        assert word in text
