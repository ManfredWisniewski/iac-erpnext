---
name: research-item
description: Research products and vendors for requisition research items — turns a "Research items" row in `requisitions/open.md` into an item record with requirements and a ranked sources table. Use when the shopping list contains items that need product/vendor research before purchase, when a row links a reference product to replace (e.g. AliExpress URL → German-available equivalent), or when an item file's sources are stale. Agents propose; humans buy.
compatibility: WIT repositories with `items/` + `requisitions/` (business/family type). Requires network access for vendor/product lookup; never put personal data in queries.
metadata:
  domain: business
  version: "0.1"
---

# Research item

Turn requisition rows that need research into sourced item records. Output lives in the item file — `items/<domain>/<slug>.md` — not in a separate report.

## Inputs

- `queue` (default): `requisitions/open.md`, section `## Research items` — work top-down, or a single row the owner names.
- `items/` (required): item records per `items/README.md`; domain folders and tags per `items/taxonomy.md`; record format per `items/_item-tpl.md`.
- `constraints` (optional): budget cap, deadline, preferred/blocked vendors from the row's Notes or the owner.

## Procedure

1. **Read the queue.** For each row take: item description, who needs it (`Needed by`), `Notes` (the real requirements — treat them as binding), reference URLs.
2. **Create or update the item record.** Slug from the description; domain folder per `items/taxonomy.md` (lowercase, no umlauts). Fill `Requirements`: Notes become *Must*; preferences ("good", "nice", "long-lasting") become *Should*; reference URLs go into *Notes* verbatim. Link the requisition's Item cell to the record.
3. **Research sources.** Web-search vendors that can actually deliver to the buyer's location. Per candidate record: vendor, exact product name, price, today as `Last checked`. At most 3 ranked options; rank by requirements-fit first, price second. Earlier `## Source history` rows inform the ranking — note price movements instead of treating every run as fresh.
4. **Alternatives.** When the row asks for "a cheap offer or alternative" or names a foreign-marketplace URL: find the closest equivalent sold by a German/EU-available shop, name it explicitly, and note what was traded off (brand, feature, warranty).
5. **Write back.** Replace `Sources (ranked)` with the latest best and append the full run — all candidates — to `## Source history` with vendors, prices and today's `Date`; earlier rows stay untouched. `Status: open` in the item file. Do not touch `## Open items`/`## Bought`; the human moves lines.

## Sourcing defaults (unless the row says otherwise)

- Vendor must ship to / be reachable from Germany; prefer established EU retailers over marketplace imports.
- No no-name knockoffs when a branded original exists — cheap is fine, counterfeit-adjacent is not; say which it is.
- Consumables get price-per-unit noted (pack size), replacements/compatibles are welcome when originals are poor value — flag compatibility claims as `likely` unless documented.
- Facts are looked up, not guessed: prices and availability carry `Last checked`; anything unverifiable is labelled.

## Rules

- Agents propose, humans buy — never mark anything bought, never order.
- No personal data in queries or records; `Needed by` stays role-level (`adult male`, `Kind 1`).
- Notes are binding requirements — an option that violates a *Must* is not listed, or is listed explicitly as failing it.
- Keep it to the ranked table: no review essays, no affiliate links — the Product cell links to the researched product page: `[product](url)`.

## Completion criteria

Every handled row: item record exists and is linked from the requisition line, requirements reflect the Notes, `Sources (ranked)` refreshed, the run appended to `## Source history` with vendors, prices and date, `Status` updated.
