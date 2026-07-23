---
id: ac74308ae7f3
status: approved
source: human
date: 2026-07-01
topic: error handling convention
refs:
  - src/main.py
last_verified: 2026-07-20
---

Wrap external calls in try/except and log with context before
re-raising. Never swallow the original exception.
