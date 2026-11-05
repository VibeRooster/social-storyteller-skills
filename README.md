# Social Storyteller Skills

Agent skills for social storytelling, packaged with the [Agent Skills](https://agentskills.io/specification) format. One catalog installs into Cursor, Claude Code, Codex, GitHub Copilot, Gemini CLI, and the rest of the agents supported by the [skills CLI](https://github.com/vercel-labs/skills).

Published skills live in [`skills/`](skills/). None are published yet. Add one with `python3 scripts/skills.py new <skill-name>`, then install from this repository:

```bash
npx skills add VibeRooster/social-storyteller-skills
```

Install one skill for one agent:

```bash
npx skills add VibeRooster/social-storyteller-skills --skill <skill-name> -a cursor
```

Use `-g` to install for every project. Agent names and install paths are listed in the [skills CLI agent table](https://github.com/vercel-labs/skills/blob/main/docs/agents.md).

## Repository layout

```text
skills/<skill-name>/SKILL.md     the catalog installers discover
templates/skill-template/         copy source for a new skill
scripts/skills.py                 create and validate skills
AGENTS.md                         rules for agents editing this repo
```

Each skill is a directory. `SKILL.md` holds the instructions. Optional `references/`, `assets/`, and `scripts/` sit beside it and are loaded only when the instructions point at them.

Check the catalog locally:

```bash
python3 scripts/skills.py validate
```

See [AGENTS.md](AGENTS.md) for the authoring rules.
