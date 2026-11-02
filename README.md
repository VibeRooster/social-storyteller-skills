# social-storyteller-skills

Agent Skills for producing social media content: scripting, hooks, short-form video, captions, posts, visuals, and HTML publishing.

## Skills
| Skill | Use it when |
|---|---|
| [heit-script](skills/heit-script) | Writing a timed HEIT explainer/demo video script |
| [hook-writing](skills/hook-writing) | Drafting and A/B testing hooks |
| [reel-construction](skills/reel-construction) | Planning, editing, and QA-ing a vertical video series |
| [burned-captions](skills/burned-captions) | Adding karaoke-style burned-in captions |
| [linkedin-post](skills/linkedin-post) | Writing a long-form LinkedIn post |
| [social-captions](skills/social-captions) | Per-platform captions and hashtags |
| [cta-library](skills/cta-library) | Choosing a CTA by funnel stage |
| [proof-points](skills/proof-points) | Sourcing and phrasing stats |
| [voice](skills/voice) | Applying an author's voice guide |
| [publish-html-hatch](skills/publish-html-hatch) | Publishing HTML to a public URL with the Hatch MCP |
| [social-visuals](skills/social-visuals) | Quote cards, carousels, thumbnails, overlays |

## Install
Copy a skill folder into your agent's skills directory:

```bash
git clone https://github.com/VibeRooster/social-storyteller-skills
cp -r social-storyteller-skills/skills/heit-script <your-agent-skills-dir>/
```

Each skill is a folder with a `SKILL.md` (YAML frontmatter `name` + `description`) and an optional `references/` folder.

## Contributing
1. Copy `templates/skill-template/` to `skills/<your-skill-name>/`.
2. Fill in the frontmatter and steps; put long material in `references/`.
3. Keep it generic: no secrets, tokens, personal IDs, or client details.
4. Open a pull request.

### Planned contributions
- _Reserved for Chip's skills._

## License
See [LICENSE](LICENSE).
