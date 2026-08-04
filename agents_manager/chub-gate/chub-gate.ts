import type { Plugin } from "@opencode-ai/plugin"

const CHUB_REMINDER = `
## CHUB RULE (structural — survives compaction)
Before writing ANY new external import (one not cited in this turn's Commands run):
  1. chub search "<pkg>"
  2. chub get <id> --lang <ts|js|py|...>
  3. Cite \`chub get <id>\` in your next "Commands run".

Anti-pattern: \`node_modules/<pkg>/types/*.d.ts\` shows type shape, not behavior.
chub-not-installed: \`npm install -g @aisuite/chub\`.
`.trim()

const IMPORT_RE =
  /(?:`'"][^./@\s'`"][^'`"]*[`'"]|(?:from\s+[`'"]|require\()\s*[`'"]@[^'`"\/]+\/[^'`"]+[`'"])/g

function extractImports(content: string): string[] {
  if (!content) return []
  const m = content.match(IMPORT_RE)
  return m ? Array.from(new Set(m)) : []
}

export const ChubGate: Plugin = async ({ client }) => ({
  "experimental.session.compacting": async (_input, output) => {
    output.context.push(CHUB_REMINDER)
  },

  "tool.execute.before": async (input, output) => {
    if (input.tool !== "edit" && input.tool !== "write" && input.tool !== "apply_patch") return
    const args = (output as { args?: any }).args ?? {}
    let content = ""
    if (input.tool === "edit") content = String(args.newString ?? "")
    else if (input.tool === "write") content = String(args.content ?? "")
    else content = String(args.patchText ?? "")
    const matches = extractImports(content)
    if (matches.length === 0) return
    try {
      await (client as any).app.log({
        body: {
          service: "chub-gate",
          level: "info",
          message: `new external import(s) detected: ${matches.join(", ")}. Run \`chub get <id>\` for each before/after this edit. Anti-pattern: .d.ts alone is not validation.`,
        },
      })
    } catch {
      /* best-effort — plugin must never break a write */
    }
  },

  "tool.execute.after": async (input, output) => {
    if (input.tool !== "bash") return
    const args = (input as { args?: any }).args ?? {}
    const cmd = String(args.command ?? "")
    if (!/\bnpm\s+(?:i|install|add)\b/.test(cmd)) return
    const pkgMatches = Array.from(cmd.matchAll(/\bnpm\s+(?:i|install|add)\s+(?:--?\w+\s+)*([@\w][\w@./-]*)/g))
      .map((m) => m[1])
      .filter(Boolean)
    if (pkgMatches.length === 0) return
    try {
      await (client as any).app.log({
        body: {
          service: "chub-gate",
          level: "info",
          message: `npm install detected for ${pkgMatches.join(", ")}. After install, run \`chub get <id>\` for each before using the API.`,
        },
      })
    } catch {
      /* best-effort */
    }
  },
})
