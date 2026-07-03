---
id: HUE-087
title: Suggestion service — anchor family pre-filter and scheme oversample
type: bug
status: todo
milestone: 14
batch: services
layer: services
depends_on: [HUE-081, HUE-082]
implements: [FR-45]
tests_required: true
estimate: 2
---

## In plain English
Anchoring on a colour family (e.g. Black) sometimes returns outfits and sometimes
returns "No outfits matched" with no changes to the wardrobe or settings. The same bug
means a wardrobe with a clearly black shirt, black jeans, and black boots won't reliably
surface an all-black outfit when Black is chosen.

## Root cause
`_matches_anchor()` post-filters `rank()` output. Because `rank()` only generates
`count` combinations (default 3) from a randomly shuffled wardrobe, whether any of those
3 happen to include a Black-family garment in an anchor slot is down to luck.  Pins avoid
this problem by pre-filtering the wardrobe *before* `rank()` runs (`_apply_pins`); the
family anchor should follow the same pattern.

The scheme anchor (`anchor_scheme`) cannot be pre-filtered because scheme is a property
of a combination, not of an individual garment — it still needs post-filtering, but with
a larger candidate pool.

## Fix

### 1. Family anchor — pre-filter (mirrors `_apply_pins`)
Add `_apply_anchor_family_filter(wardrobe, anchor_family)` alongside `_apply_pins`.
For each garment in an anchor slot, keep it only if the requested family appears in its
colours.  Garments in echo/minor slots are kept unchanged.  Apply this filter immediately
after `_apply_pins` in `suggest()`:

```python
wardrobe = _apply_pins(wardrobe, pin_garments)
if anchor_family is not None:
    wardrobe = _apply_anchor_family_filter(wardrobe, anchor_family)
```

`rank()` then receives a wardrobe where anchor-slot garments are already narrowed to the
requested family — every combination it generates will satisfy the family condition.
Post-filtering by family is no longer needed.

### 2. Scheme anchor — oversample
Scheme is a combination property; `rank()` must still be called first.  When
`anchor_scheme` is set, ask `rank()` for `min(count * 10, 100)` candidates, apply the
scheme filter, then trim to `count`:

```python
rank_count = min(count * 10, 100) if anchor_scheme else count
results = rank(wardrobe, requested_slots, rng, count=rank_count)
...
results = [r for r in results if _matches_anchor(r, None, anchor_scheme)]
results = results[:count]
```

When both family and scheme are set: the pre-filter narrows the wardrobe (family), then
oversample + trim handles the scheme.

## Acceptance criteria
- Calling `suggest()` with the same wardrobe, same `anchor_family`, and any RNG seed
  always either returns combinations or returns zero-result — never alternates between
  the two.
- A wardrobe containing black shirt, black jeans, and black boots returns combinations
  featuring those garments whenever `anchor_family="Black"` is requested.
- `anchor_scheme` is consistent across multiple calls on the same wardrobe.
- The `EmptySlotsError` path is still reached when the pre-filter removes all garments
  from a mandatory slot (i.e. no anchor-slot garments of the requested family exist).
- `anchor_family` + `anchor_scheme` combined: pre-filter applies first, then oversample
  + scheme trim.
- All existing anchor tests continue to pass; new determinism tests added.

## Tests
`backend/tests/services/test_suggestion_service.py` — extend `TestAnchor`:
- `test_anchor_family_is_deterministic` — same wardrobe + family + N different RNG seeds
  all return the same set of combination ids.
- `test_anchor_family_surfaces_matching_garment` — wardrobe with one black shirt, no
  other shirts; `anchor_family="Black"` always returns that shirt in the mid/shirt slot.
- `test_anchor_scheme_is_deterministic` — same wardrobe + scheme, N seeds → consistent
  results.
- `test_empty_slots_when_no_anchor_family_garments` — wardrobe with no Black-family
  anchor garments + `anchor_family="Black"` → `EmptySlotsError` (or zero result if no
  mandatory slot is affected).

## Definition of done
- [ ] Acceptance criteria met
- [ ] Tests added per §12.2 and passing in `make test`
- [ ] `make test-perf` passes (suggestion-touching ticket)
- [ ] Ticket status + notes updated in the same commit

## Notes
- 2026-07-02 — created. Discovered during manual testing of HUE-083 anchor controls.
  Same-wardrobe + same-anchor sometimes returned results, sometimes returned the zero
  explanation. Root cause: `_matches_anchor` post-filters a randomly sampled pool of
  `count` combinations; the fix mirrors `_apply_pins` for family anchors and oversamples
  for scheme anchors.
