# Social Storyteller Skills

Agent skills for social storytelling, packaged with the [Agent Skills](https://agentskills.io/specification) format. One catalog installs into Cursor, Claude Code, Codex, GitHub Copilot, Gemini CLI, and the rest of the agents supported by the [skills CLI](https://github.com/vercel-labs/skills).

Each skill is labeled with the role an agent plays when it loads the skill. The roles come from a professional video crew: Producer, Director, Copywriter, Cinematographer, Graphics, Editor, and Publisher. The [crew catalog](skills/README.md) lists what each role owns and the skills for that role.

Published skills live in [`skills/`](skills/), one folder per role. None are published yet. Add one with `python3 scripts/skills.py new <skill-name> --role <role>`, then install from this repository:

```bash
npx skills add VibeRooster/social-storyteller-skills
```

Install one skill for one agent:

```bash
npx skills add VibeRooster/social-storyteller-skills --skill <skill-name> -a cursor
```

Install every skill for one role:

```bash
npx skills add https://github.com/VibeRooster/social-storyteller-skills/tree/main/skills/editor
```

Use `-g` to install for every project. Agent names and install paths are listed in the [skills CLI agent table](https://github.com/vercel-labs/skills/blob/main/docs/agents.md).

## Repository layout

```text
skills/<role>/<skill-name>/SKILL.md   the catalog installers discover
skills/README.md                       crew catalog, generated
templates/skill-template/              copy source for a new skill
scripts/skills.py                      create, validate, and catalog skills
AGENTS.md                              rules for agents editing this repo
```

Each skill is a directory. `SKILL.md` holds the instructions, `metadata.role` labels the role, and a `## Role` section tells the agent which seat it is in. Optional `references/`, `assets/`, and `scripts/` sit beside it and are loaded only when the instructions point at them.

Check the catalog locally:

```bash
python3 scripts/skills.py roles
python3 scripts/skills.py catalog
python3 scripts/skills.py validate
```

See [AGENTS.md](AGENTS.md) for the authoring rules.
