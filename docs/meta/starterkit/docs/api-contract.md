# <PROJECT> — Interface Contract

| | |
|---|---|
| **Document** | Interface contract (HTTP API / CLI / library surface) |
| **Repository location** | `docs/api-contract.md` |
| **Status** | Binding specification — **authoritative for interface shapes** |

> **Purpose.** This document is the authoritative description of the project's external surface — the
> exact request/response shapes, status codes, and error envelope. **Where code and this contract
> disagree, the contract wins.** Because the contract is fixed here, the client/frontend can be
> built against it *independently* of the backend, and reconciled only at end-to-end assembly.
>
> This template assumes an HTTP API. For a CLI, replace "endpoints" with "commands, flags, exit
> codes, stdout/stderr shapes"; for a library, with "public functions, signatures, return types,
> raised errors". The discipline — exact, versioned, testable shapes — is the same.

---

## 1. Conventions

> Base path, content types, versioning approach, authentication (if any), pagination style, date/
> number formats. State once here so each endpoint need not repeat it.

### 1.1 Shared object shapes

> Objects that appear in multiple responses, defined once. Example:

```json
{
  "<object>": {
    "<field>": "<type — and any constraint>"
  }
}
```

### 1.2 Error envelope and status codes

> The single shape every error response takes, and the status codes in use. Example:

```json
{ "error": { "code": "<MACHINE_CODE>", "message": "<human-readable>" } }
```

| Status | When |
|--------|------|
| 200 / 201 | <…> |
| 400 | <validation failure — body shape> |
| 404 | <not found> |
| 409 | <conflict> |
| 422 | <semantic validation> |

---

## 2. Endpoints

> One sub-section per endpoint. For each: method + path, purpose, the FR ids it serves, the request
> shape (path/query/body), the response shape, and the error cases. Keep examples concrete and
> valid — they double as fixtures.

### 2.1 `GET /api/health`

Liveness check. Returns `200` with `{ "status": "ok" }`. Implements <NFR-n>.

### 2.2 `<METHOD> /api/<resource>` — <purpose>  (FR-n, FR-m)

**Request**

```json
{ "<field>": "<type>" }
```

**Response — `2xx`**

```json
{ "<field>": "<type>" }
```

**Errors:** <which codes from §1.2 apply, and the condition for each>.

<!-- Repeat 2.x per endpoint. When a later version adds or changes an endpoint, annotate it in place,
     e.g. "### 2.10a PATCH /api/<resource> — <purpose> (new — vX.Y, FR-nn)". -->

---

## 3. Traceability

> A table mapping each endpoint to the FR/NFR ids it realises, so the contract, the requirements,
> and the tickets stay in agreement.

| Endpoint | Implements |
|----------|------------|
| `<METHOD> /api/<resource>` | FR-n, FR-m |
