# Social Storyteller Skills

This repository publishes [Agent Skills](https://agentskills.io/specification). The same `skills/` catalog is what Cursor, Claude Code, Codex, GitHub Copilot, Gemini CLI, and the other agents behind `npx skills` install. Do not keep a second copy under `.cursor/`, `.claude/`, `.agents/`, or any other agent directory.

## Layout

```text
skills/<role>/<skill-name>/SKILL.md              published skill
skills/<role>/<category>/<skill-name>/SKILL.md
skills/README.md                                 crew catalog, generated
templates/skill-template/                        starter, not published
scripts/skills.py                                create, validate, catalog
```

A skill directory may also contain `references/`, `assets/`, and `scripts/`. The folder that contains `SKILL.md` is the skill. Its name must match the `name` field and be unique across every role. The installers flatten the role folders, so they keep only one skill with a given name.

## Roles

Every skill is labeled with the production role an agent plays when it loads the skill. The roles follow a professional video crew:

| Phase | Roles |
| --- | --- |
| Pre-production | `producer`, `director`, `copywriter` |
| Production | `cinematographer` |
| Post-production | `graphics`, `editor` |
| Distribution | `publisher` |

`python3 scripts/skills.py roles` prints what each role owns. The `ROLES` list in `scripts/skills.py` is the only definition. Add or rename a role there, then run `python3 scripts/skills.py catalog`.

A skill states its role three ways, and validation requires them to agree:

- It sits in the role folder `skills/<role>/`.
- It sets `metadata.role: <role>`.
- It has a `## Role` section that tells the agent which seat it is in, what it receives, and which role gets its deliverable.

Give a skill to the role that would own that deliverable on a real crew. Scripts, captions, and titles go to the Copywriter. Storyboards and shot lists go to the Director. Sets, wardrobe, and lighting go to the Cinematographer. Title design, motion graphics, thumbnails, and caption styling go to Graphics. The grade and the sound mix go to the Editor. A skill that two roles would share belongs to the role that signs off on it. Inside a role folder, you may add one category folder for browsing.

`templates/` is not a discovery path. Keep the template as `SKILL.md.example` so a recursive install search cannot publish it.

## Add a skill

From the repository root:

```bash
python3 scripts/skills.py new <skill-name> --role <role>
python3 scripts/skills.py new <skill-name> --role <role> --category <category> --description "<what it does and when>"
```

Then fill in the `## Role` handoff, the procedure, the reference, and the asset. Run:

```bash
python3 scripts/skills.py catalog
python3 scripts/skills.py validate
```

Validation fails while template markers remain (`your-skill-name`, `your-role`, `Replace this`). It also fails when the role labels disagree or `skills/README.md` is out of date.

## Authoring rules

- `name`: 1–64 characters, lowercase letters, numbers, single hyphens. It must match the directory.
- `description`: third person, at most 1024 characters. Say what the skill does and when to use it, with the words a person would use to ask for the task. This is the only text agents see before deciding to load the skill.
- Keep `SKILL.md` under 500 lines. Put long rules in `references/` and formats in `assets/`.
- Link those files from `SKILL.md` at the step that needs them. Do not link from a reference to another file.
- Prefer instructions. Add a script only when the step is fragile enough that generated code would drift. Tell the agent to execute the script, and do not paste it into `SKILL.md`.
- Set `license: MIT`, `metadata.author: VibeRooster`, and `metadata.role`.
- Leave out `allowed-tools` unless a pre-approved tool is required. Support for that field differs by agent.
- A skill under `skills/` is installable. Set `metadata.internal: "true"` to hide an unfinished skill from default installs, or keep the draft outside `skills/` until it validates.

## Do not

- Put a `SKILL.md` at the repository root or directly under `skills/` without a role folder.
- Edit the generated crew table in `skills/README.md` by hand.
- Duplicate a skill into an agent-specific directory. Installers would see two copies.
- Commit `skills-lock.json` or skills that `npx skills` installed into this checkout.
- Put product secrets, credentials, or private account data in a skill.
