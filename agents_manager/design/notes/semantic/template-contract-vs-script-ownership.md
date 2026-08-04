# Template contract vs. script ownership

When a template documents a mechanical gate, distinguish three layers explicitly: the script's parsed sections, the script's emitted metrics, and the orchestrator's append/update step. Do not claim that a script mutates a ledger unless its source writes that ledger. Surface parser gaps (for example, a documented footer with no current parser) in the handoff rather than silently treating the contract as active.
