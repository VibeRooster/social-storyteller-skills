# Social Storyteller Skills

This repository publishes [Agent Skills](https://agentskills.io/specification). The same `skills/` catalog is what Cursor, Claude Code, Codex, GitHub Copilot, Gemini CLI, and the other agents behind `npx skills` install. Do not keep a second copy under `.cursor/`, `.claude/`, `.agents/`, or any other agent directory.

## Layout

```text
skills/<skill-name>/SKILL.md          published skill
skills/<category>/<skill-name>/SKILL.md
templates/skill-template/             starter, not published
scripts/skills.py                     create and validate
```

A skill directory may also contain `references/`, `assets/`, and `scripts/`. The folder that contains `SKILL.md` is the skill. Its name must match the `name` field. Category folders are for people browsing the repo. Use at most two levels of categories.

`templates/` is not a discovery path. Keep the template as `SKILL.md.example` so a recursive install search cannot publish it.

## Add a skill

From the repository root:

```bash
python3 scripts/skills.py new <skill-name>
python3 scripts/skills.py new <skill-name> --category <category> --description "<what it does and when>"
```

Then replace the procedure, the reference, and the asset. Run:

```bash
python3 scripts/skills.py validate
```

Validation fails while template markers remain (`your-skill-name`, `Replace this`).

## Authoring rules

- `name`: 1–64 characters, lowercase letters, numbers, single hyphens. It must match the directory.
- `description`: third person, at most 1024 characters. Say what the skill does and when to use it, with the words a person would use to ask for the task. This is the only text agents see before deciding to load the skill.
- Keep `SKILL.md` under 500 lines. Put long rules in `references/` and formats in `assets/`.
- Link those files from `SKILL.md` at the step that needs them. Do not link from a reference to another file.
- Prefer instructions. Add a script only when the step is fragile enough that generated code would drift. Tell the agent to execute the script, and do not paste it into `SKILL.md`.
- Set `license: MIT` and `metadata.author: VibeRooster`.
- Leave out `allowed-tools` unless a pre-approved tool is required. Support for that field differs by agent.
- A skill under `skills/` is installable. Set `metadata.internal: "true"` to hide an unfinished skill from default installs, or keep the draft outside `skills/` until it validates.

## Do not

- Put a `SKILL.md` at the repository root.
- Duplicate a skill into an agent-specific directory. Installers would see two copies.
- Commit `skills-lock.json` or skills that `npx skills` installed into this checkout.
- Put product secrets, credentials, or private account data in a skill.
