---
name: webtext-datenschutz
description: Generates a Datenschutzerklärung (privacy notice, Art. 13/14 DSGVO + § 25 TDDDG) for German websites from a filled-out questionnaire and the deployed external services. Use when creating, completing or checking a website privacy/Datenschutz page, or when a Fragebogen for Datenschutz is provided.
metadata:
  version: "1.3.1"
---

# Webtext — Datenschutzerklärung

## GOAL

Create the text for a legally structured Datenschutzerklärung from a filled-out questionnaire.

## TASK

Analyze the filled-out `Datenschutz-Fragebogen.md` in `{{project-directory}}/kontakt/` against the criteria in `+wit/common/conventions/law/Datenschutz-Matrix.md` and create the privacy-notice content.

## Steps

1. Read the filled-out `Datenschutz-Fragebogen.md` — locate it under `{{project-directory}}` (default: `kontakt/`); if absent or unfilled, stop and escalate.
2. Identify which **Verarbeitungsprozesse** (matrix §4) and **external services** (matrix §5) are actually in use — only those produce sections.
3. Derive the mandatory **Art. 13 DSGVO** entries (matrix §2): Verantwortlicher, Zwecke + Rechtsgrundlagen, Empfänger, Speicherdauer, Betroffenenrechte, Beschwerderecht, Widerruf; conditional entries (DSB, Art. 14 sources, automated decisions) only when the questionnaire says they apply.
4. For each deployed external service: take Rechtsgrundlage, TDDDG consent status, Drittland/DPF flag and Datenschutzrolle (AV/EV/GV) from matrix §5 — mark entries where the matrix says *anbieterabhängig* as needs-verification.
5. Check for **gaps and contradictions** (e.g. Google Analytics in use but no consent management, US service without DPF/SCC note, tracking without TDDDG consent mechanism).
6. Compose the Datenschutzerklärung following the matrix's **Muster-Struktur** (§10) — include only the sections that apply.
7. If step 5 found gaps or contradictions against the conventions, prepend a clearly marked review block at the beginning of the output file (e.g. a `> ⚠️ Zu prüfen:` blockquote) listing each open point — the human resolves and removes it before publishing.
8. Write the result to `{{project-directory}}/kontakt/datenschutz/webtext.md` (or the location given by the task).
9. **Verify:** re-read the questionnaire and the generated file side by side — every field value must appear verbatim, every deployed service/Verarbeitungsprozess must have produced a section, and no section for a non-deployed service may be present. Fix discrepancies before reporting.

## DONE WHEN

- `datenschutz/webtext.md` exists and follows the matrix's Muster-Struktur ordering.
- Every mandatory Art. 13 entry is filled from the questionnaire or explicitly listed as missing in the report.
- Only actually deployed services appear — no boilerplate for unused tools, no `{{placeholders}}`, no invented values.
- Each service section names Zweck, Rechtsgrundlage, Empfänger/Datenschutzrolle, Drittlandtransfer (with DPF/SCC where applicable) and Speicherdauer; provider-dependent values are flagged for verification rather than asserted.
- No Impressum content is mixed in (separate page per the matrix's Abgrenzung).

## RULES

- Output language: German, formal register.
- The matrix is the source of truth for structure, legal bases and service facts — never assert storage durations, DPF status or roles the matrix marks *anbieterabhängig*.
- Uncertain or missing questionnaire answers produce a report entry, not a guess.
- Keep § 25 TDDDG consent logic consistent: consent-required services must not be described as running before consent.
- Do not add legal disclaimers or editorial content beyond the Muster-Struktur.
- Always append the review notice `Diese Datenschutzerklärung wurde automatisiert erstellt und muss manuell geprüft werden. Bitte löschen Sie diesen Hinweis, nachdem Sie die Angaben geprüft und bestätigt haben.` at the end of the webtext.
- Write the output with the project's default page template — YAML frontmatter `template: default` with `meta_title`/`meta_description` adapted to the page (check existing `webtext.md` files in the project for the convention).

## REPORT

- Output file path.
- Verarbeitungsprozesse and external services included/excluded (with reasons).
- Entries flagged *anbieterabhängig / verify* (Speicherdauer, DPF-Zertifizierung, AV vs. EV/GV).
- Missing or contradictory questionnaire entries that block legal completeness.
