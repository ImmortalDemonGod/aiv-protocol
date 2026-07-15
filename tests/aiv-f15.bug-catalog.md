# Bug catalog — Finding F15 (SSRF in `LinkValidator._head_check`)

- **Local file disclosure via `file://` scheme.** Symptom: an evidence-link URL of
  `file:///etc/shadow` reaches a real filesystem read. Location:
  `src/aiv/lib/validators/links.py:163-176` (`LinkValidator._head_check`). Wrong behavior:
  `urlopen(Request(url, method="HEAD"))` is invoked unconditionally for any scheme, so a
  `file://` URL is opened against the local filesystem. Correct behavior: the scheme is checked
  against an allowlist (`http`/`https` only) before `urlopen` is ever called, so `urlopen` is
  never reached for `file://` URLs.

- **Cloud metadata endpoint SSRF.** Symptom: an evidence-link URL of
  `http://169.254.169.254/latest/meta-data/` causes a real HTTP HEAD request to the cloud
  instance-metadata service, which can leak instance credentials/tokens. Location:
  `src/aiv/lib/validators/links.py:163-176`. Wrong behavior: `urlopen` is called for any
  syntactically valid `http://` URL regardless of host, including the link-local metadata
  address. Correct behavior: the target host/IP is checked against a private/loopback/
  link-local/reserved-range denylist before `urlopen` is called, so `urlopen` is never reached
  for `169.254.169.254`.

- **Loopback / internal-service SSRF.** Symptom: an evidence-link URL of `http://127.0.0.1/`
  causes a real HTTP HEAD request to services bound to localhost on the machine running the
  validator, allowing internal port/service probing. Location:
  `src/aiv/lib/validators/links.py:163-176`. Wrong behavior: `urlopen` is called for
  `http://127.0.0.1/` exactly as for any other syntactically valid `http://` URL. Correct
  behavior: the loopback address is classified and blocked before `urlopen` is called, so
  `urlopen` is never reached for `127.0.0.1`.

- **Guard must not break legitimate link checking (regression guard).** Symptom: an
  over-broad fix could also block normal external evidence links, silently disabling the
  E021 link-vitality check. Location: `src/aiv/lib/validators/links.py:163-176`. Wrong
  behavior (of a naive/overzealous fix): a normal `https://` URL (e.g. a GitHub blob link)
  never reaches `urlopen`, so link vitality is never actually verified. Correct behavior: a
  normal `https://` URL still results in exactly one `urlopen` HEAD call.
