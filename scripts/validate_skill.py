#!/usr/bin/env python3
"""Validate the distributable Kainan skill without third-party packages."""

from __future__ import annotations

import re
import subprocess
import sys
from math import ceil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
MAX_LINES = 150
MAX_CHARACTERS = 5_000
MAX_APPROX_TOKENS = 4_500

REQUIRED = (
    "SKILL.md",
    "README.md",
    "LICENSE",
    "agents/openai.yaml",
    "references/knowledge/凯南恋爱聊天风格.md",
    "references/knowledge/来源与证据说明.md",
    "references/practical/场景回复模式.md",
    "documentation/product.md",
    "documentation/architecture.md",
    "documentation/flows.md",
    "documentation/permissions.md",
    "documentation/variables.md",
    "documentation/knowledge-base.md",
)


def require(path: str) -> Path | None:
    target = ROOT / path
    if not target.exists():
        ERRORS.append(f"missing required path: {path}")
        return None
    return target


def approx_tokens(text: str) -> int:
    cjk = len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", text))
    latin = len(re.findall(r"[A-Za-z0-9_]+", text))
    other = len(re.findall(r"[^\sA-Za-z0-9_\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", text))
    return cjk + ceil(latin * 1.3) + ceil(other / 4)


def validate_frontmatter() -> None:
    path = require("SKILL.md")
    if path is None:
        return
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        ERRORS.append("SKILL.md has invalid YAML frontmatter boundaries")
        return
    front = match.group(1)
    keys = re.findall(r"^([A-Za-z0-9_-]+):", front, re.MULTILINE)
    if keys != ["name", "description"]:
        ERRORS.append(f"frontmatter keys must be name, description; got {keys}")
    name = re.search(r"^name:\s*(.+)$", front, re.MULTILINE)
    description = re.search(r"^description:\s*(.+)$", front, re.MULTILINE)
    value = name.group(1).strip() if name else ""
    desc = description.group(1).strip() if description else ""
    if value != "kainan-love-coach" or not re.fullmatch(r"[a-z0-9-]{1,64}", value):
        ERRORS.append(f"invalid skill name: {value!r}")
    if not desc or len(desc) > 1024 or "<" in desc or ">" in desc:
        ERRORS.append("description is empty, too long, or contains angle brackets")


def validate_budget() -> None:
    path = ROOT / "SKILL.md"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if len(text.splitlines()) > MAX_LINES:
        ERRORS.append(f"SKILL.md exceeds {MAX_LINES} lines")
    if len(text) > MAX_CHARACTERS:
        ERRORS.append(f"SKILL.md exceeds {MAX_CHARACTERS} characters")
    if approx_tokens(text) > MAX_APPROX_TOKENS:
        ERRORS.append(f"SKILL.md exceeds approximate token budget {MAX_APPROX_TOKENS}")


def validate_content() -> None:
    skill = ROOT / "SKILL.md"
    if skill.is_file():
        text = skill.read_text(encoding="utf-8")
        markers = (
            "默认只读取当前问题直接需要的 1–3 份参考",
            "先给一句可发送版本",
            "拒绝/不适",
            "不适，立即降级并停止推进",
            "不声称是本人或官方团队",
        )
        for marker in markers:
            if marker not in text:
                ERRORS.append(f"SKILL.md missing behavior marker: {marker}")
    agent = ROOT / "agents/openai.yaml"
    if agent.is_file() and "$kainan-love-coach" not in agent.read_text(encoding="utf-8"):
        ERRORS.append("agents/openai.yaml default prompt must mention $kainan-love-coach")


def validate_links() -> None:
    pattern = re.compile(r"\]\(([^)]+)\)")
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for raw in pattern.findall(text):
            target = raw.strip().split("#", 1)[0]
            if not target or re.match(r"^(?:https?://|mailto:)", target):
                continue
            if not (path.parent / target).resolve().exists():
                ERRORS.append(f"broken local link in {path.relative_to(ROOT)}: {raw}")


def validate_runtime() -> None:
    runtime_roots = (ROOT / "SKILL.md", ROOT / "agents", ROOT / "references", ROOT / "assets")
    forbidden_suffixes = {".docx", ".doc", ".xlsx", ".xls", ".zip"}
    for root in runtime_roots:
        if not root.exists():
            continue
        paths = (root,) if root.is_file() else root.rglob("*")
        for path in paths:
            if path.is_file() and path.suffix.lower() in forbidden_suffixes:
                ERRORS.append(f"raw source file inside runtime content: {path.relative_to(ROOT)}")
            if path.is_file() and path.suffix.lower() in {".pyc", ".pyo"}:
                ERRORS.append(f"compiled artifact inside runtime content: {path.relative_to(ROOT)}")

    if (ROOT / ".git").exists():
        tracked = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, check=False, capture_output=True, text=True
        ).stdout.splitlines()
        for item in tracked:
            if item.endswith("来源台账与证据说明.md") or item.lower().endswith(".docx"):
                ERRORS.append(f"local source material is tracked: {item}")


def validate_secrets() -> None:
    patterns = (
        r"gh[pousr]_[A-Za-z0-9_]{20,}",
        r"github_pat_[A-Za-z0-9_]{20,}",
        r"-----BEGIN [A-Z ]+ PRIVATE KEY-----",
    )
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in {".md", ".yaml", ".yml", ".py"}:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in patterns:
            if re.search(pattern, text):
                ERRORS.append(f"possible credential pattern in {path.relative_to(ROOT)}")


def main() -> int:
    for path in REQUIRED:
        require(path)
    validate_frontmatter()
    validate_budget()
    validate_content()
    validate_links()
    validate_runtime()
    validate_secrets()
    if ERRORS:
        for error in ERRORS:
            print(f"ERROR: {error}")
        return 1
    print("kainan-love-coach validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
