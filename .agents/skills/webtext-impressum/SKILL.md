---
name: webtext-impressum
description: Generates Impressum text (§ 5 DDG provider identification) for German websites from a filled-out Impressum questionnaire. Use when creating, completing or checking a website Impressum page, or when a Fragebogen for the Impressum is provided.
metadata:
  version: "1.4.1"
---

# Webtext — Impressum

## GOAL

Create the text for a legally structured Impressum from a filled-out questionnaire.

## TASK

Analyze the filled-out `Impressum-Fragebogen.md` in `{{project-directory}}/kontakt/` against the criteria in `+wit/common/conventions/law/Impressum-Matrix.md` and create the Impressum content.

## Steps

1. Read the filled-out `Impressum-Fragebogen.md` — locate it under `{{project-directory}}` (default: `kontakt/`); if absent or unfilled, stop and escalate.
2. Determine the **Rechtsform** from section 1 of the questionnaire and look up the matching column/section of `+wit/common/conventions/law/Impressum-Matrix.md`.
3. Derive the required **Pflichtangaben** (§ 5 Abs. 1 Nr. 1–8 DDG) for that Rechtsform; treat ⚠️ entries as conditional — include only when the questionnaire says the condition applies (register entry, reglementierter Beruf, USt-IdNr., Kapitalangaben, Abwicklung, audiovisuelle Mediendienste, OS-Plattform, § 18 MStV).
4. Check the questionnaire for **gaps and contradictions** (e.g. GmbH without Geschäftsführer, reglementierter Beruf without Kammer, Postfach-only address).
5. Compose the Impressum using the matrix's **Muster-Impressum** for the matching Rechtsform as the skeleton — fill in the questionnaire values verbatim.
6. If step 4 found gaps or contradictions against the conventions, prepend a clearly marked review block at the beginning of the output file (e.g. a `> ⚠️ Zu prüfen:` blockquote) listing each open point — the human resolves and removes it before publishing.
7. Write the result to `{{project-directory}}/kontakt/webtext.md` (or the location given by the task).
8. **Verify:** re-read the questionnaire and the generated file side by side — every required field value (names, addresses, register numbers, IDs) must appear verbatim, every selected questionnaire section must have produced output, and no section for an unselected item may be present. Fix discrepancies before reporting.

## DONE WHEN

- `impressum.md` exists and follows the Muster-Impressum structure for the detected Rechtsform.
- Every § 5 Nr. 1–8 entry marked required for that Rechtsform is either filled from the questionnaire or explicitly listed as missing in the report.
- Conditional entries are included only when applicable — no empty sections, no `{{placeholders}}`, no invented values.
- No Datenschutzerklärung content is mixed in (separate page per the matrix's Abgrenzung).

## RULES

- Output language: German, formal register ("Angaben gemäß § 5 DDG" heading).
- The matrix is the source of truth for required fields and ordering — never skip a required section, never invent data.
- Uncertain or missing questionnaire answers produce a report entry, not a guess.
- Keep the legal-notice structure exactly: no editorial additions, no marketing copy.
- Do not add legal disclaimers beyond what the matrix's Muster-Impressum contains.
- Always include the scope sentence `Dieses Impressum gilt auch für unsere Präsenzen auf anderen Webseiten.` after the provider-identification block.
- Always append the review notice `Dieses Impressum wurde automatisiert erstellt und muss manuell geprüft werden. Bitte löschen Sie diesen Hinweis, nachdem Sie die Angaben geprüft und bestätigt haben.` at the end of the webtext.
- Write the output with the project's default page template — YAML frontmatter `template: default` with `meta_title`/`meta_description` adapted to the page (check existing `webtext.md` files in the project for the convention).

## REPORT

- Output file path.
- Detected Rechtsform and which conditional sections were included/excluded (with reasons).
- Missing or contradictory questionnaire entries that block legal completeness.
