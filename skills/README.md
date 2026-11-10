# Catalog

Skills are grouped by the production role an agent plays when it loads them. A role works like a seat on a video crew. The Director sets the vision, the Copywriter writes the words, Graphics designs the type and overlays, and the Editor builds the cut. Each skill sits in one role folder:

```text
skills/<role>/<skill-name>/SKILL.md
skills/<role>/<category>/<skill-name>/SKILL.md
```

The folder that contains `SKILL.md` is the skill name. Skill names must be unique across all roles because installers flatten the folders. A role folder may hold one category folder for browsing, and no deeper folders.

The role is labeled in three places, and validation keeps them in agreement:

- the role folder;
- `metadata.role` in the frontmatter;
- a `## Role` section that tells the agent which seat it is in and who receives its work.

List the roles and create a skill from the repository root:

```bash
python3 scripts/skills.py roles
python3 scripts/skills.py new <skill-name> --role <role>
python3 scripts/skills.py new <skill-name> --role <role> --category <category>
```

Drafts do not belong here. A `SKILL.md` under `skills/` is discoverable by installers. Hide an unfinished skill with `metadata.internal: "true"` until it is ready, or keep it outside `skills/` until it validates.

## Crew

`python3 scripts/skills.py catalog` generates this section. Do not edit it by hand.

<!-- catalog:start -->

### Pre-production

| Role | Owns | Skills |
| --- | --- | --- |
| Producer | Owns the brief: the goal, audience, platforms, budget, schedule, and sign-off, and keeps a series on strategy. | — |
| Director | Sets the creative vision: the concept, treatment, tone, story beats, storyboards, shot lists, and notes to talent. | — |
| Copywriter | Writes every word, heard or read: hooks, scripts, voiceover, dialogue, titles, captions, on-screen text, thumbnail text, descriptions, and calls to action. | — |

### Production

| Role | Owns | Skills |
| --- | --- | --- |
| Cinematographer | Designs the image: locations, sets, props, wardrobe, framing, camera movement, lenses, lighting, and prompts for generated footage. | — |

### Post-production

| Role | Owns | Skills |
| --- | --- | --- |
| Graphics | Designs the graphic elements: title design, animated type, lower thirds, end cards, motion graphics, thumbnails, cover frames, caption styling, logo bugs, and overlays. | — |
| Editor | Builds the finished cut: selects, structure, pacing, color grade, music, sound effects, the mix, cutdowns, and versions for each aspect ratio. | — |

### Distribution

| Role | Owns | Skills |
| --- | --- | --- |
| Publisher | Ships the finished piece: export specs, platform delivery, posting schedule, and performance review. | — |

<!-- catalog:end -->
