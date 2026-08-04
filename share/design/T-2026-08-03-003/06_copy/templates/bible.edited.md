# Book Bible — [Working Title]

Cumulative, append-only (in commit order, even across parallel chapters). Every writer agent reads this before drafting.

## Established facts / claims (nonfiction)
- [fact] — introduced in ch-0X

## Terminology

<!-- REQUIRED: keep this exact section available even when there are no entries. build_exports.py projects ### entries from here to glossary.md. -->
- [term]: [definition/usage rule] — introduced in ch-0X

## Voice rules (quick reference — full detail in style-guide.md)
- [rule]

## Characters (fiction/hybrid only)

<!-- REQUIRED: keep the Characters section available even when this is a nonfiction book. build_exports.py reads ### names from here for index projection. -->
### [Character name]
- Established traits: [...]
- Introduced: ch-0X
- Known so far by reader: [...]

## Plot threads (fiction/hybrid only)
- [thread]: opened ch-0X, [status: open/resolved]

## Timeline (fiction/hybrid only)
- [event] — ch-0X, [in-story time reference]

## POV (fiction/hybrid only)
- [confirmed POV/tense, cross-reference style-guide.md]

## Updated through ch-NN

Required footer. Replace `ch-NN` with the highest chapter number present anywhere in the project after each chapter update. Do not leave a lower chapter number after a later chapter is drafted or revised.

## Mechanical gates

- **`build_exports.py` — Phase 5 export gate:** reads `## Terminology` for glossary projection and `## Characters` (plus terminology names) for index projection.
- **`book_check.py` — Phase 6 staleness gate:** reads the `Updated through ch-NN` footer by project contract and warns when it does not match the highest chapter. The checked-in PR-1 implementation currently does not parse this footer; master should track that as a follow-up gap rather than treating the warning as active.
- The `## Terminology` and `## Characters` headers are mandatory even when their entry lists are empty.

## Open questions

1. Should the footer record the highest chapter file or the highest chapter with an approved status?
2. Should `build_exports.py` include character names in the index when the book category is nonfiction?
3. Should a stale footer fail the gate or remain a warning once the parser is added?
