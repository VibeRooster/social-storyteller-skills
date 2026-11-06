# Catalog

Each published skill is a directory with a `SKILL.md` file:

```text
skills/<skill-name>/SKILL.md
skills/<category>/<skill-name>/SKILL.md
```

The folder that contains `SKILL.md` is the skill name. A category folder is only for browsing. Stay within two category levels so installers still find the skill.

Create a skill from the repository root:

```bash
python3 scripts/skills.py new <skill-name>
python3 scripts/skills.py new <skill-name> --category <category>
```

Drafts do not belong here. A `SKILL.md` under `skills/` is discoverable by installers. Hide an unfinished skill with `metadata.internal: true` until it is ready, or keep it outside `skills/` until it validates.
