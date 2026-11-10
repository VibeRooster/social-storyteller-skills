#!/usr/bin/env python3
"""Create and validate Agent Skills in this repository.

Usage:
  python3 scripts/skills.py validate
  python3 scripts/skills.py roles
  python3 scripts/skills.py catalog
  python3 scripts/skills.py new <skill-name> --role <role> [--category <category>] [--description <text>]
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
CATALOG_FILE = SKILLS_DIR / "README.md"
CATALOG_START = "<!-- catalog:start -->"
CATALOG_END = "<!-- catalog:end -->"
TEMPLATE_DIR = ROOT / "templates" / "skill-template"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PLACEHOLDER_MARKERS = ("your-skill-name", "your-role", "Replace this")


@dataclass(frozen=True)
class Role:
    slug: str
    title: str
    phase: str
    owns: str


PHASES = ("Pre-production", "Production", "Post-production", "Distribution")
ROLES = (
    Role(
        "producer",
        "Producer",
        "Pre-production",
        "owns the brief: the goal, audience, platforms, budget, schedule, and sign-off, "
        "and keeps a series on strategy",
    ),
    Role(
        "director",
        "Director",
        "Pre-production",
        "sets the creative vision: the concept, treatment, tone, story beats, storyboards, "
        "shot lists, and notes to talent",
    ),
    Role(
        "copywriter",
        "Copywriter",
        "Pre-production",
        "writes every word, heard or read: hooks, scripts, voiceover, dialogue, titles, captions, "
        "on-screen text, thumbnail text, descriptions, and calls to action",
    ),
    Role(
        "cinematographer",
        "Cinematographer",
        "Production",
        "designs the image: locations, sets, props, wardrobe, framing, camera movement, lenses, "
        "lighting, and prompts for generated footage",
    ),
    Role(
        "graphics",
        "Graphics",
        "Post-production",
        "designs the graphic elements: title design, animated type, lower thirds, end cards, "
        "motion graphics, thumbnails, cover frames, caption styling, logo bugs, and overlays",
    ),
    Role(
        "editor",
        "Editor",
        "Post-production",
        "builds the finished cut: selects, structure, pacing, color grade, music, sound effects, "
        "the mix, cutdowns, and versions for each aspect ratio",
    ),
    Role(
        "publisher",
        "Publisher",
        "Distribution",
        "ships the finished piece: export specs, platform delivery, posting schedule, and "
        "performance review",
    ),
)
ROLE_BY_SLUG = {role.slug: role for role in ROLES}
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


def folder_role(skill_file: Path) -> str:
    parts = skill_file.relative_to(SKILLS_DIR).parts
    return parts[0] if len(parts) > 2 else ""


def metadata_role(data: dict) -> str:
    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        return ""
    return str(metadata.get("role", "")).strip()


def check_role(skill_file: Path, data: dict, body: str) -> list[str]:
    errors: list[str] = []
    folder = folder_role(skill_file)
    role = metadata_role(data)
    if not folder:
        errors.append("must sit in a role folder: skills/<role>/<skill-name>/SKILL.md")
    elif folder not in ROLE_BY_SLUG:
        errors.append(
            f"folder {folder!r} is not a role; run `python3 scripts/skills.py roles`"
        )
    if not role:
        errors.append("metadata.role is required")
    elif role not in ROLE_BY_SLUG:
        errors.append(f"metadata.role {role!r} is not a role; run `python3 scripts/skills.py roles`")
    elif folder in ROLE_BY_SLUG and role != folder:
        errors.append(f"metadata.role {role!r} must match the role folder {folder!r}")
    if not re.search(r"^## Role\s*$", body, flags=re.MULTILINE):
        errors.append("add a `## Role` section that tells the agent which role it plays")
    return errors


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
    errors.extend(f"{relative}: {issue}" for issue in check_role(skill_file, data, body))
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


def skills_by_role() -> dict[str, list[tuple[str, Path]]]:
    grouped: dict[str, list[tuple[str, Path]]] = {role.slug: [] for role in ROLES}
    for skill_file in iter_skills():
        try:
            frontmatter, _ = split_frontmatter(skill_file.read_text(encoding="utf-8"), skill_file)
            data = parse_frontmatter(frontmatter, skill_file)
        except SkillFormatError:
            continue
        role = folder_role(skill_file)
        if role in grouped:
            name = str(data.get("name", "")).strip() or skill_file.parent.name
            grouped[role].append((name, skill_file.parent.relative_to(SKILLS_DIR)))
    return grouped


def render_catalog() -> str:
    grouped = skills_by_role()
    lines = [CATALOG_START, ""]
    for phase in PHASES:
        lines += [f"### {phase}", "", "| Role | Owns | Skills |", "| --- | --- | --- |"]
        for role in ROLES:
            if role.phase != phase:
                continue
            entries = sorted(grouped[role.slug])
            title = f"[{role.title}]({role.slug}/)" if entries else role.title
            skills = ", ".join(f"[`{name}`]({path.as_posix()}/)" for name, path in entries)
            owns = role.owns[0].upper() + role.owns[1:]
            lines.append(f"| {title} | {owns}. | {skills or '—'} |")
        lines.append("")
    lines.append(CATALOG_END)
    return "\n".join(lines)


def catalog_text() -> str:
    text = CATALOG_FILE.read_text(encoding="utf-8")
    start = text.find(CATALOG_START)
    end = text.find(CATALOG_END)
    if start == -1 or end == -1 or end < start:
        fail(f"{CATALOG_FILE.relative_to(ROOT)} needs {CATALOG_START} and {CATALOG_END} markers")
    return text[:start] + render_catalog() + text[end + len(CATALOG_END) :]


def command_catalog(_: argparse.Namespace) -> None:
    CATALOG_FILE.write_text(catalog_text(), encoding="utf-8")
    print(f"Updated {CATALOG_FILE.relative_to(ROOT)}")


def command_roles(_: argparse.Namespace) -> None:
    for phase in PHASES:
        print(phase)
        for role in ROLES:
            if role.phase == phase:
                print(f"  {role.slug:<20} {role.title} {role.owns}")


def command_validate(_: argparse.Namespace) -> None:
    skills = iter_skills()
    errors: list[str] = []
    warnings: list[str] = []
    seen_names: dict[str, Path] = {}
    for skill in skills:
        skill_errors, skill_warnings = validate_skill(skill)
        errors.extend(skill_errors)
        warnings.extend(skill_warnings)
        name = skill.parent.name
        if name in seen_names:
            errors.append(
                f"{skill.relative_to(ROOT)}: skill name {name!r} is also used by "
                f"{seen_names[name].relative_to(ROOT)}; installers keep only one"
            )
        else:
            seen_names[name] = skill
    if CATALOG_FILE.read_text(encoding="utf-8") != catalog_text():
        errors.append(
            f"{CATALOG_FILE.relative_to(ROOT)} is out of date; run `python3 scripts/skills.py catalog`"
        )
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
    role = ROLE_BY_SLUG[args.role]
    destination = SKILLS_DIR / role.slug
    category = args.category
    if category:
        category_errors = check_name(category, "category")
        if category_errors:
            fail("; ".join(category_errors))
        destination /= category
    destination /= args.name
    if destination.exists():
        fail(f"{destination.relative_to(ROOT)} already exists")
    existing = [skill for skill in iter_skills() if skill.parent.name == args.name]
    if existing:
        fail(f"skill name {args.name!r} is already used by {existing[0].relative_to(ROOT)}")
    if not TEMPLATE_DIR.is_dir():
        fail(f"missing template: {TEMPLATE_DIR.relative_to(ROOT)}")
    shutil.copytree(TEMPLATE_DIR, destination)
    example = destination / "SKILL.md.example"
    skill_file = destination / "SKILL.md"
    text = example.read_text(encoding="utf-8")
    text = text.replace("name: your-skill-name", f"name: {args.name}", 1)
    text = text.replace("role: your-role", f"role: {role.slug}", 1)
    text = text.replace(
        "Work as the Your Role.",
        f"Work as the {role.title}. The {role.title} {role.owns}.",
        1,
    )
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
    CATALOG_FILE.write_text(catalog_text(), encoding="utf-8")
    print(f"Created {skill_file.relative_to(ROOT)}")
    print("Edit the description, procedure, reference, and asset, then run:")
    print("  python3 scripts/skills.py validate")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create and validate skills in this repo.")
    subcommands = parser.add_subparsers(dest="command", required=True)
    validate = subcommands.add_parser("validate", help="check every published skill")
    validate.set_defaults(func=command_validate)
    roles = subcommands.add_parser("roles", help="list the production roles a skill can play")
    roles.set_defaults(func=command_roles)
    catalog = subcommands.add_parser("catalog", help="regenerate the role catalog in skills/README.md")
    catalog.set_defaults(func=command_catalog)
    create = subcommands.add_parser("new", help="copy the skill template into skills/<role>/")
    create.add_argument("name", help="skill name, matching the directory that will hold SKILL.md")
    create.add_argument(
        "--role",
        required=True,
        choices=list(ROLE_BY_SLUG),
        help="production role the agent plays when it loads the skill",
    )
    create.add_argument("--category", help="optional folder inside the role folder")
    create.add_argument("--description", help="third-person description of what the skill does and when to use it")
    create.set_defaults(func=command_new)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
