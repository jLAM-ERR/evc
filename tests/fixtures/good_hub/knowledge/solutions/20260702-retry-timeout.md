---
id: f2de55390bd5
status: candidate
source: gate
date: 2026-07-02
topic: retry timeout fix
related:
  - umbrella:conventions/20260701-error-handling.md
---

We hit flaky timeouts on the payments API; fixed by retrying three
times with exponential backoff and a 2s cap.
