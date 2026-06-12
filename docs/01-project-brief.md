# Project Brief: Wardrobe Colour-Matching Application

| | |
|---|---|
| **Document** | Project Brief (Milestone 1) |
| **Status** | Draft for approval |
| **Date** | 12 June 2026 |
| **Author** | Generated via Claude Chat interview |

---

## 1. Overview

A single-user web application that builds a digital inventory of the owner's wardrobe from photographs, automatically identifies the colours present in each garment, and uses colour science (colour wheel harmony rules, plus the concepts of neutrals and accent pieces) to suggest cohesive outfits on request.

This project has a deliberate **meta-goal**: to document and develop a small software project end to end using Claude Chat, Claude Cowork, and Claude Code, including a bespoke Markdown-based ticketing system in place of Jira. The process is as much a deliverable as the product.

## 2. Problem Statement

Choosing clothes that genuinely work together by colour is a skill, not a given. The owner wants a tool that removes the guesswork: photograph each garment once, then ask the application "what goes with what?" and receive combinations grounded in colour theory rather than habit.

## 3. Users

One user: the owner. No accounts, no authentication, no multi-tenancy. The application runs locally on the owner's machine.

## 4. Goals (MVP)

1. **Inventory building.** Upload a photograph of an individual garment (laid flat or a retailer product image). The application automatically detects the colour(s) present, including multi-colour garments, with the *proportion* of each colour. The user confirms or corrects the detected colours, then tags the garment with its type (e.g. shirt, trousers, jersey, jacket, socks, shoes, hat, accessory).
2. **Browsable wardrobe.** View the inventory filtered by garment type and by colour.
3. **Outfit suggestion.** Request an outfit, specifying which optional slots to include. The application returns one or more combinations that are harmonious according to colour theory, with a plain-language explanation of *why* each combination works (e.g. "analogous scheme: navy top, teal accent in the socks").
4. **Local-first.** Runs entirely on the owner's machine with no internet dependency at runtime.

## 5. Outfit Structure

An outfit always contains:

- Top
- Bottom
- Socks
- Shoes

Optional slots, chosen at request time:

- Jersey
- Jacket (jersey and jacket may both be present)
- Hat
- Accessories

## 6. Colour-Matching Approach

- **Colour wheel harmony rules**: complementary, analogous, triadic, monochromatic, and neutral-based schemes.
- **Neutrals** (black, white, grey, navy, beige/tan, denim) are recognised as compatible with most colours and do not count against a harmony scheme.
- **Proportion-aware matching**: a garment's primary colour drives matching. Minor colours (small proportions, e.g. a thin stripe or logo) must not disqualify an otherwise harmonious garment. They may, however, be used positively — e.g. echoing a minor colour elsewhere in the outfit.
- **Role-aware slots**: slots may play different roles where it makes sense. For example, socks and accessories typically *echo* an accent colour already present in the outfit rather than introduce a new dominant colour. Exact role rules to be defined in the requirements document.

## 7. Colour Detection Approach

- Automatic extraction of dominant colours and their proportions from a photograph (anticipated approach: pixel clustering, e.g. k-means, with background removal/segmentation to isolate the garment).
- A **confirm-and-correct step**: the application proposes the detected palette; the user approves it or adjusts before the garment is saved. Detection should be good enough that approval is the common case.

## 8. Technical Direction

| Layer | Choice | Rationale |
|---|---|---|
| Backend | **Python + FastAPI** | Python has best-in-class libraries for image processing (Pillow, OpenCV), clustering (scikit-learn), and colour science (colour-science, colormath). FastAPI gives a clean, documented API contract. |
| Frontend | **React SPA** | Image-heavy UI (galleries, swatches, palette confirmation) suits a component model; a genuine API contract between front and back end is a better workout for the documentation and ticketing workflow. |
| Storage | **SQLite + local image files** | Single user, local-first; zero-administration persistence. |
| Hosting | None for MVP | Runs locally; hosting is a possible future concern. |

Final architecture, including the API contract, will be defined in a dedicated architecture document (later milestone).

## 9. Out of Scope (MVP)

- User accounts and authentication
- Mobile application
- Weather-based suggestion adjustment
- Outfit wear tracking / history
- Automatic garment-type recognition (type is tagged manually; only colour detection is automated)
- Pattern-clash logic (e.g. "two loud patterns") — colour logic only for MVP
- Hosting / deployment beyond the local machine

## 10. Future Roadmap (post-MVP, not committed)

1. Weather-aware suggestions (adjust for temperature and conditions)
2. Outfit tracking: record what was worn and when; avoid repetition
3. Possible hosting for access away from the local machine

## 11. Success Criteria

The MVP is done when the owner can:

1. Upload a garment photo and have the application propose its colour(s) with proportions, then confirm or correct them and save the garment with a type tag.
2. Browse the wardrobe filtered by type and colour.
3. Request an outfit with chosen optional slots and receive at least one harmonious combination, each with an explanation of the colour reasoning.
4. Do all of the above locally, offline, with the application started by a simple command.

Additionally, for the meta-goal:

5. Every milestone is documented in Markdown and checked into the repository.
6. Requirements are tracked as one Markdown file per ticket with structured frontmatter, and tickets are updated as work completes.

## 12. Risks and Open Questions

| Risk | Notes / Mitigation |
|---|---|
| Colour extraction quality on phone photos (lighting, shadows, bed linen background) | Confirm-and-correct flow is the safety net; consider simple background-removal techniques; recommend photographing on a plain, contrasting surface. |
| Defining "harmonious" precisely enough to test | Harmony rules and role rules must be specified concretely in the requirements document so the matcher is unit-testable. |
| Combinatorial explosion in suggestion generation | With a small personal wardrobe this is unlikely to matter; cap and rank results if it does. |
| Colour perception vs. measurement | Detected RGB must be mapped to human-meaningful colour names/families; needs a defined palette taxonomy. |
| Scope creep towards roadmap features | Out-of-scope list above is the contract; roadmap items require their own briefs. |

## 13. Repository Strategy

A **single repository** containing:

```
/docs        – all project documentation (this brief, requirements, architecture, test strategy…)
/tickets     – one Markdown file per ticket, with YAML frontmatter (ID, status, milestone, dependencies, acceptance criteria)
/backend     – FastAPI application
/frontend    – React application
```

Tickets live beside the code they describe so they stay honest and can be updated in the same commits as the work itself. A second repository will only be introduced if a genuine need emerges (e.g. separate deployment).

---

*Approval of this brief closes Milestone 1.*
