---
name: product-design
description: Use when Hafiz asks Codex to brainstorm, redesign, create a PRD, clarify requirements, turn a PRD into UX, or create build prompts for a Sifututor feature/module before implementation. Must follow docs/agent-playbooks/product-design.md.
---

# Product Design

Use this skill for design-first product work before code.

## Core Rule

Read and follow:

```text
docs/agent-playbooks/product-design.md
```

This is the Codex-readable equivalent of Claude's product workflow:

```text
/lite-prd -> /prd-clarifier -> /prd-to-ux -> /ux-to-prompts
```

For billing, invoices, payments, auth, commissions, migrations, deployment, and
mobile API contracts, stay in design/diagnosis until Hafiz explicitly approves
implementation.

## Human-Facing Alias

When explaining this to Hafiz, describe it as:

```text
Claude: /lite-prd, /prd-clarifier, /prd-to-ux, /ux-to-prompts
Codex: $product-design
```
