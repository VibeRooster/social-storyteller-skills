#!/usr/bin/env python3
"""Create and validate Agent Skills in this repository.

Usage:
  python3 scripts/skills.py validate
  python3 scripts/skills.py new <skill-name> [--category <category>] [--description <text>]
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
TEMPLATE_DIR = ROOT / "templates" / "skill-template"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PLACEHOLDER_MARKERS = ("your-skill-name", "Replace this")
RESERVED_NAME_WORDS = ("anthropic", "claude")
KNOWN_FRONTMATTER = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
PATH_RE = re.compile(r"(?<![\w./-])((?:references|scripts|assets)/[A-Za-z0-9_./-]+)")


class SkillFormatError(Exception):
    """Raised when a skill file is not readable as frontmatter plus markdown."""


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def check_name(name: str, label: str = "name") -> list[str]:
    errors: list[str] = []
    if not name:
        return [f"{label} is empty"]
    if len(name) > 64:
        errors.append(f"{label} exceeds 64 characters")
    if not NAME_RE.fullmatch(name):
        errors.append(
            f"{label} must be lowercase letters, numbers, and single hyphens, "
            "and must not start or end with a hyphen"
        )
    for word in RESERVED_NAME_WORDS:
        if word in name:
            errors.append(f"{label} contains {word!r}, which Claude Code rejects")
    return errors


def split_frontmatter(text: str, path: Path) -> tuple[str, str]:
    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        raise SkillFormatError(f"{path}: SKILL.md must start with YAML frontmatter")
    end = normalized.find("\n---\n", 4)
    if end == -1:
        raise SkillFormatError(f"{path}: frontmatter is missing a closing ---")
    return normalized[4:end], normalized[end + 5 :]


def parse_scalar(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] == '"':
        inner = value[1:-1]
        return inner.replace("\\\\", "\0").replace('\\"', '"').replace("\0", "\\")
    if len(value) >= 2 and value[0] == value[-1] and value[0] == "'":
        return value[1:-1].replace("''", "'")
    return value


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def parse_frontmatter(frontmatter: str, path: Path) -> dict:
    data: dict = {}
    lines = frontmatter.split("\n")
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.strip().startswith("#"):
            index += 1
            continue
        if line.startswith(" ") or line.startswith("\t"):
            raise SkillFormatError(f"{path}: unexpected indented line in frontmatter: {line!r}")
        if ":" not in line:
            raise SkillFormatError(f"{path}: invalid frontmatter line: {line!r}")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        index += 1
        if key == "metadata":
            if raw_value:
                raise SkillFormatError(f"{path}: metadata must be a nested map of strings")
            metadata: dict[str, str] = {}
            while index < len(lines) and (
                lines[index].startswith("  ") or not lines[index].strip()
            ):
                nested = lines[index]
                index += 1
                if not nested.strip():
                    continue
                if not nested.startswith("  ") or nested.startswith("   "):
                    raise SkillFormatError(f"{path}: metadata entries must be indented two spaces")
                if ":" not in nested:
                    raise SkillFormatError(f"{path}: invalid metadata line: {nested!r}")
                nested_key, nested_value = nested.split(":", 1)
                metadata[nested_key.strip()] = parse_scalar(nested_value)
            data["metadata"] = metadata
            continue
        if raw_value in {">", ">-", "|", "|-"}:
            block: list[str] = []
            while index < len(lines) and (
                lines[index].startswith("  ") or not lines[index].strip()
            ):
                if lines[index].strip():
                    block.append(lines[index].strip())
                index += 1
            joiner = "\n" if raw_value.startswith("|") else " "
            data[key] = joiner.join(block).strip()
            continue
        data[key] = parse_scalar(raw_value)
    return data


def linked_paths(body: str) -> list[str]:
    found: list[str] = []
    for match in LINK_RE.findall(body):
        target = match.split()[0].strip()
        if target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        found.append(target.split("#", 1)[0])
    for match in PATH_RE.findall(body):
        found.append(match.rstrip("."))
    return found


def validate_skill(skill_file: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    relative = skill_file.relative_to(ROOT)
    text = skill_file.read_text(encoding="utf-8")
    if "\\" in text:
        errors.append(f"{relative}: use forward slashes in paths")
    try:
        frontmatter, body = split_frontmatter(text, relative)
        data = parse_frontmatter(frontmatter, relative)
    except SkillFormatError as exc:
        return [str(exc)], []
    for key in data:
        if key not in KNOWN_FRONTMATTER:
            warnings.append(
                f"{relative}: unknown frontmatter field {key!r} is not in the Agent Skills spec"
            )
    name = str(data.get("name", "")).strip()
    description = str(data.get("description", "")).strip()
    errors.extend(f"{relative}: {issue}" for issue in check_name(name))
    if name and skill_file.parent.name != name:
        errors.append(
            f"{relative}: name {name!r} must match the directory {skill_file.parent.name!r}"
        )
    if not description:
        errors.append(f"{relative}: description is required")
    elif len(description) > 1024:
        errors.append(f"{relative}: description exceeds 1024 characters")
    elif re.match(r"^(I |You |We )\b", description):
        errors.append(f"{relative}: write the description in third person")
    if "<" in name or re.search(r"</?[A-Za-z]", description):
        errors.append(f"{relative}: name and description must not contain XML tags")
    compatibility = str(data.get("compatibility", "")).strip()
    if compatibility and len(compatibility) > 500:
        errors.append(f"{relative}: compatibility exceeds 500 characters")
    metadata = data.get("metadata", {})
    if metadata and not isinstance(metadata, dict):
        errors.append(f"{relative}: metadata must be a map")
    elif isinstance(metadata, dict):
        for meta_key, meta_value in metadata.items():
            if not isinstance(meta_value, str):
                errors.append(f"{relative}: metadata.{meta_key} must be a string")
        if metadata.get("internal", "").lower() == "true":
            warnings.append(f"{relative}: hidden from default installs (metadata.internal)")
    line_count = text.count("\n") + (0 if text.endswith("\n") else 1)
    if line_count > 500:
        errors.append(f"{relative}: SKILL.md is {line_count} lines; keep it under 500")
    skill_root = skill_file.parent
    depth = len(skill_file.relative_to(SKILLS_DIR).parts) - 1
    if depth > 3:
        errors.append(
            f"{relative}: nested {depth} directories under skills/; installers only walk 3"
        )
    for sibling in skill_root.rglob("*"):
        if not sibling.is_file():
            continue
        if sibling.suffix.lower() not in {".md", ".txt", ".json", ".py", ".sh"}:
            continue
        sibling_text = sibling.read_text(encoding="utf-8")
        for marker in PLACEHOLDER_MARKERS:
            if marker in sibling_text:
                errors.append(
                    f"{sibling.relative_to(ROOT)}: still contains template marker {marker!r}"
                )
    seen: set[str] = set()
    for target in linked_paths(body):
        if target in seen or not target:
            continue
        seen.add(target)
        destination = (skill_root / target).resolve()
        if skill_root.resolve() not in destination.parents and destination != skill_root.resolve():
            errors.append(f"{relative}: link escapes the skill directory: {target}")
            continue
        if not destination.is_file():
            errors.append(f"{relative}: missing linked file {target}")
    return errors, warnings


def iter_skills() -> list[Path]:
    if not SKILLS_DIR.is_dir():
        return []
    return sorted(SKILLS_DIR.rglob("SKILL.md"))


def command_validate(_: argparse.Namespace) -> None:
    skills = iter_skills()
    errors: list[str] = []
    warnings: list[str] = []
    for skill in skills:
        skill_errors, skill_warnings = validate_skill(skill)
        errors.extend(skill_errors)
        warnings.extend(skill_warnings)
    for warning in warnings:
        print(f"warning: {warning}")
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
    if not skills:
        print("No published skills yet. Catalog layout is valid.")
        return
    print(f"Validated {len(skills)} skill{'s' if len(skills) != 1 else ''}.")


def command_new(args: argparse.Namespace) -> None:
    name_errors = check_name(args.name)
    if name_errors:
        fail("; ".join(name_errors))
    category = args.category
    if category:
        category_errors = check_name(category, "category")
        if category_errors:
            fail("; ".join(category_errors))
        destination = SKILLS_DIR / category / args.name
    else:
        destination = SKILLS_DIR / args.name
    if destination.exists():
        fail(f"{destination.relative_to(ROOT)} already exists")
    if not TEMPLATE_DIR.is_dir():
        fail(f"missing template: {TEMPLATE_DIR.relative_to(ROOT)}")
    shutil.copytree(TEMPLATE_DIR, destination)
    example = destination / "SKILL.md.example"
    skill_file = destination / "SKILL.md"
    text = example.read_text(encoding="utf-8")
    text = text.replace("name: your-skill-name", f"name: {args.name}", 1)
    title = args.name.replace("-", " ").title()
    text = text.replace("# Your Skill Name", f"# {title}", 1)
    if args.description:
        description = " ".join(args.description.split())
        text = re.sub(
            r"^description:.*$",
            "description: " + yaml_quote(description),
            text,
            count=1,
            flags=re.MULTILINE,
        )
    skill_file.write_text(text, encoding="utf-8")
    example.unlink()
    print(f"Created {skill_file.relative_to(ROOT)}")
    print("Edit the description, procedure, reference, and asset, then run:")
    print("  python3 scripts/skills.py validate")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create and validate skills in this repo.")
    subcommands = parser.add_subparsers(dest="command", required=True)
    validate = subcommands.add_parser("validate", help="check every published skill")
    validate.set_defaults(func=command_validate)
    create = subcommands.add_parser("new", help="copy the skill template into skills/")
    create.add_argument("name", help="skill name, matching the directory that will hold SKILL.md")
    create.add_argument("--category", help="optional single catalog folder under skills/")
    create.add_argument("--description", help="third-person description of what the skill does and when to use it")
    create.set_defaults(func=command_new)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
