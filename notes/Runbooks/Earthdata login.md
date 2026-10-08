---
tags:
  - ops
---

# Runbook: Earthdata login

## When to use

- First-time NASA Earthdata access
- Searching or downloading NISAR / Sentinel-1 via `earthaccess`

## Steps

1. Create an account at https://urs.earthdata.nasa.gov/ (free).
2. Authorize the relevant applications if Earthdata/ASF asks (common for downloads).
3. Locally, run `earthaccess.login()` and store credentials in the **user** netrc / earthaccess cache — never in this repo.
4. Confirm search works with the snippet in [[docs/Complete plan]].
5. Record product name, region, and granule counts in [[research/NISAR data access]].

## If it fails

- Empty search: confirm exact `short_name` in Earthdata Search / ASF Vertex, then try Sentinel-1 as a placeholder.
- Auth errors: re-login locally; do not paste passwords into notes or chat.
- If a password or token was pasted in chat, change it and revoke the token. Local auth is `~/.netrc` only.

## Related

- [[research/NISAR data access]]
- [[Runbooks]]
