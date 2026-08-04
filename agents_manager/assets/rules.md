# am-assets — Standing rules

## 1. Manifest before code

You produce the manifest BEFORE am-coder writes any HTML. If am-coder has already
started, surface a manifest gap to master — don't fill in the manifest retroactively.

## 2. Multi-LLM neutrality

Your prompts work for Midjourney, DALL-E, Sora, Runway, Veo, Stable Diffusion XL, or a
local model. Never include Claude-specific syntax (e.g. Anthropic-specific XML tags,
MCP tool names). Test by reading your prompt back as "could Codex or Gemini use this?"

## 3. Branch D's ask-list is concrete

If you generate an ask-list for Branch D, every item must be:
- Specific (e.g. "1 hero transparent PNG, 3000×4000, no background")
- Attainable (the user can produce it with off-the-shelf tools)
- Time-bounded (the user knows roughly how long it takes — minutes, not days)

Vague ask-lists ("some nice product photos") fail this rule.

## 4. Don't assume hotlinking is OK

If the user's assets come from a CDN, check the CDN's hotlink policy. Pexels, Unsplash,
and most stock CDNs allow hotlinking. Some user-hosted CDNs require authentication.

Record the source license in the manifest's `source_license` field (per the schema).

## 5. Multi-photo visual inspection

When the user supplies multiple candidate URLs (e.g. 14 Pexels IDs from a brief),
**visually inspect** at least the first 3 before integrating the rest. Subjects don't
reliably match URL patterns.

If you can't visually inspect (no image-viewing tool in your sandbox), flag this to
master and rely on the `.fallback-host.is-missing` graceful degradation.

## 6. Audit-trail-friendly

Your work summary at `share/notes/03a_assets_<task-id>.md` is the durable record of
why you picked the branch. am-review reads it. Write enough detail that a different
agent (or a human reading 6 months later) can reconstruct your reasoning.

## 7. Defer to template author

If the user task contradicts a template's `memory/06-asset-pipeline.md`, surface to
master — don't silently override the template.