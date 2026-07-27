"""kb-lint v1 test suite — grammar, hashing, secret rules, checks, CLI."""

import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from kblib import frontmatter, kb_checks, secret_rules

FIXTURES = Path(__file__).parent / "fixtures"
TODAY = date(2026, 7, 23)


def make_tree(tmp_path: Path, name: str) -> Path:
    root = tmp_path / name
    shutil.copytree(FIXTURES / name, root)
    return root


def run(root: Path, layout: str, write: bool = False, today: date = TODAY):
    return kb_checks.run_all(root, layout, write=write, today=today)


def kb_dir(root: Path, layout: str) -> Path:
    return kb_checks.kb_dir_for(root, layout)


# --- frontmatter grammar -------------------------------------------------

GOOD_FM = """---
id: b94d27b9934d
status: candidate
source: gate
date: 2026-07-23
topic: a topic with: colons
refs:
  - src/app.py@abc1234
related:
  - umbrella:conventions/x.md
---

body text
"""


def test_parse_accepts_contract_example():
    fm, body = frontmatter.parse(GOOD_FM)
    assert fm["topic"] == "a topic with: colons"
    assert fm["refs"] == ["src/app.py@abc1234"]
    assert fm["related"] == ["umbrella:conventions/x.md"]
    assert body.strip() == "body text"


@pytest.mark.parametrize(
    "text",
    [
        "no frontmatter at all",
        "---\nid: x\n",  # unclosed
        "---\nid: b94d27b9934d\n\nstatus: candidate\n---\nb",  # blank line
        "---\n# comment\n---\nb",  # comment
        "---\nid: a\nid: b\n---\nb",  # duplicate key
        "---\nId: a\n---\nb",  # uppercase key
        "---\nid:  \n---\nb",  # empty value
        "---\nrefs:\n---\nb",  # list head with zero items
        "---\n  - item\n---\nb",  # item without head
        "---\nid:\tx\n---\nb",  # tab
        "---\nrefs:\n    - deep\n---\nb",  # wrong indentation
    ],
)
def test_parse_rejects(text):
    with pytest.raises(frontmatter.FrontmatterError):
        frontmatter.parse(text)


def test_flow_list_parses_as_scalar_and_schema_rejects(tmp_path):
    # `refs: [a, b]` is grammatically a scalar; the schema layer rejects it.
    fm, _ = frontmatter.parse("---\nrefs: [a, b]\n---\nb")
    assert fm["refs"] == "[a, b]"


# --- normalization + id --------------------------------------------------


def test_entry_id_known_digest():
    assert frontmatter.entry_id("hello world") == "b94d27b9934d"


def test_normalization_invariants():
    base = frontmatter.entry_id("line one\nline two")
    assert frontmatter.entry_id("line one\r\nline two\r\n") == base
    assert frontmatter.entry_id("line one  \nline two\t\n\n\n") == base
    assert frontmatter.entry_id("\n\nline one\nline two") == base
    # NFC: e-acute composed vs decomposed
    assert frontmatter.entry_id("café") == frontmatter.entry_id("café")


def test_fixture_ids_match_kblib():
    entry = FIXTURES / "good_hub/knowledge/conventions/20260701-error-handling.md"
    fm, body = frontmatter.parse(entry.read_text(encoding="utf-8"))
    assert fm["id"] == frontmatter.entry_id(body) == "ac74308ae7f3"


# --- secret rules --------------------------------------------------------


@pytest.mark.parametrize(
    "rule_id,line",
    [
        ("KB-SEC-001", "-----BEGIN RSA PRIVATE KEY-----"),
        ("KB-SEC-002", "aws key AKIAIOSFODNN7EXAMPLE here"),
        ("KB-SEC-003", "api_key = sk_live_abcdef1234567890"),
        ("KB-SEC-004", "Authorization: Bearer abcdefgh12345678q"),
        ("KB-SEC-004", "jwt eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.dozjgNryP4J3jVmNHl0w5N"),
        ("KB-SEC-005", "card 4111 1111 1111 1111 leaked"),
        ("KB-SEC-006", "iban DE89370400440532013000 leaked"),
        ("KB-PII-001", "mail me at someone@example.com please"),
    ],
)
def test_secret_rules_fire(rule_id, line):
    assert rule_id in {f.rule_id for f in secret_rules.scan_text(line)}


def test_luhn_invalid_card_not_flagged():
    findings = secret_rules.scan_text("number 4111 1111 1111 1112 here")
    assert "KB-SEC-005" not in {f.rule_id for f in findings}


def test_allowlist_suppresses_exact_match():
    line = "contact someone@example.com now"
    assert secret_rules.scan_text(line, frozenset({"someone@example.com"})) == []
    assert secret_rules.scan_text(line, frozenset({"other@example.com"})) != []


# --- run_all on good trees ----------------------------------------------


@pytest.mark.parametrize("name,layout", [("good_hub", "hub"), ("good_project", "project")])
def test_good_tree_exits_0(tmp_path, name, layout):
    findings, code = run(make_tree(tmp_path, name), layout)
    assert (findings, code) == ([], 0)


# --- each failing check --------------------------------------------------


def test_oversized_index_hard_fails(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    index = kb_dir(root, "hub") / "INDEX.md"
    index.write_text(index.read_text() + "filler\n" * 200)
    findings, code = run(root, "hub")
    assert code == 2
    assert any(f.check == "budget" and "INDEX" in f.message for f in findings)


def test_oversized_agents_hard_fails(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    (root / "AGENTS.md").write_text("rule\n" * 150)
    findings, code = run(root, "hub")
    assert code == 2
    assert any(f.check == "budget" and "AGENTS" in f.message for f in findings)


def test_oversized_methodology_hard_fails(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    (root / "methodology").mkdir()
    (root / "methodology" / "big.md").write_text("x\n" * 150)
    findings, code = run(root, "hub")
    assert code == 2
    assert any(f.check == "budget" and "methodology" in f.message for f in findings)


def test_multiline_frontmatter_rejected_cleanly(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    bad = kb_dir(root, "hub") / "patterns" / "20260723-bad.md"
    bad.write_text("---\nid: b94d27b9934d\nnote: >\n  folded\n---\nbody\n")
    findings, code = run(root, "hub")
    assert code == 2
    assert any(f.check == "schema" and "bad.md" in f.path for f in findings)


def test_unknown_key_and_bad_enums_fail(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    entry = kb_dir(root, "hub") / "conventions" / "20260701-error-handling.md"
    text = entry.read_text().replace("status: approved", "status: shiny")
    text = text.replace("source: human", "source: human\ncustom_key: nope")
    entry.write_text(text)
    findings, code = run(root, "hub")
    assert code == 2
    messages = " | ".join(f.message for f in findings)
    assert "bad status: shiny" in messages
    assert "unknown key: custom_key" in messages


def test_id_mismatch_fails(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    entry = kb_dir(root, "hub") / "solutions" / "20260702-retry-timeout.md"
    entry.write_text(entry.read_text() + "drifted body edit\n")
    findings, code = run(root, "hub")
    assert code == 2
    assert any("id mismatch" in f.message for f in findings)


def test_unresolved_ref_warns_exit_1(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    (root / "src" / "app.py").unlink()
    findings, code = run(root, "hub")
    assert code == 1
    assert any(f.check == "refs" and "stale" in f.message for f in findings)


def test_malformed_ref_hard_fails(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    entry = kb_dir(root, "hub") / "conventions" / "20260701-error-handling.md"
    entry.write_text(entry.read_text().replace("  - src/app.py", "  - ../escape.py"))
    findings, code = run(root, "hub")
    assert code == 2
    assert any(f.check == "refs" and "malformed" in f.message for f in findings)


def test_ref_with_at_in_path_and_commit_forms():
    assert kb_checks.split_ref("src/app.py@abc1234") == ("src/app.py", "abc1234")
    assert kb_checks.split_ref("src/we@ird.py") == ("src/we@ird.py", None)
    assert kb_checks.split_ref("a@b@abcdef1") == ("a@b", "abcdef1")


def test_orphan_entry_warns(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    index = kb_dir(root, "hub") / "INDEX.md"
    index.write_text(
        index.read_text().replace(
            "- [retry timeout fix](solutions/20260702-retry-timeout.md) — flaky external APIs\n",
            "",
        )
    )
    findings, code = run(root, "hub")
    assert code == 1
    assert any(f.check == "orphan" and f.severity == "warn" for f in findings)


def test_index_broken_link_hard_fails(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    index = kb_dir(root, "hub") / "INDEX.md"
    index.write_text(index.read_text() + "\n- [ghost](patterns/20990101-ghost.md) — nope\n")
    findings, code = run(root, "hub")
    assert code == 2
    assert any(f.check == "orphan" and "missing file" in f.message for f in findings)


def test_old_gardening_log_warns(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    findings, code = run(root, "hub", today=date(2026, 9, 1))
    assert code == 1
    assert any(f.check == "gardening" and "overdue" in f.message for f in findings)


def test_missing_gardening_log_warns_no_crash(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    (kb_dir(root, "hub") / ".gardening-log").unlink()
    findings, code = run(root, "hub")
    assert code == 1
    assert any("no gardening log" in f.message for f in findings)


def test_candidate_pileup_warns(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    kb = kb_dir(root, "hub")
    index_lines = [kb.joinpath("INDEX.md").read_text()]
    for i in range(26):
        body = f"candidate body number {i}"
        name = f"20260723-cand-{i}.md"
        (kb / "glossary" / name).write_text(
            "---\n"
            f"id: {frontmatter.entry_id(body)}\n"
            "status: candidate\nsource: retro\ndate: 2026-07-23\n"
            f"topic: cand {i}\n---\n\n{body}\n"
        )
        index_lines.append(f"- [cand {i}](glossary/{name}) — filler\n")
    (kb / "INDEX.md").write_text("".join(index_lines))
    findings, code = run(root, "hub")
    assert code == 1
    assert any("run distill" in f.message for f in findings)


def test_secret_in_entry_hard_fails(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    entry = kb_dir(root, "hub") / "solutions" / "20260702-retry-timeout.md"
    body_extra = "leaked AKIAIOSFODNN7EXAMPLE key"
    text = entry.read_text() + body_extra + "\n"
    fm, body = frontmatter.parse(text)
    entry.write_text(text.replace(str(fm["id"]), frontmatter.entry_id(body)))
    findings, code = run(root, "hub")
    assert code == 2
    assert any(f.check == "secret" and "KB-SEC-002" in f.message for f in findings)


def test_project_allowlist_suppresses(tmp_path):
    root = make_tree(tmp_path, "good_project")
    kb = kb_dir(root, "project")
    entry = kb / "solutions" / "20260702-retry-timeout.md"
    body_extra = "ask someone@example.com for access"
    text = entry.read_text() + body_extra + "\n"
    fm, body = frontmatter.parse(text)
    entry.write_text(text.replace(str(fm["id"]), frontmatter.entry_id(body)))
    findings, code = run(root, "project")
    assert code == 2  # fires without allowlist entry
    (kb / ".secret-allowlist").write_text("someone@example.com\n")
    findings, code = run(root, "project")
    assert (findings, code) == ([], 0)


# --- Codex-review regressions (commit after 3d68e3e) ---------------------


def test_list_valued_required_key_fails(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    entry = kb_dir(root, "hub") / "solutions" / "20260702-retry-timeout.md"
    entry.write_text(
        entry.read_text().replace("id: f2de55390bd5", "id:\n  - not-a-hash")
    )
    findings, code = run(root, "hub")
    assert code == 2
    assert any("id must be a scalar" in f.message for f in findings)


def test_secret_in_gardening_log_hard_fails(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    log = kb_dir(root, "hub") / ".gardening-log"
    log.write_text(log.read_text() + "2026-07-23 noted AKIAIOSFODNN7EXAMPLE\n")
    findings, code = run(root, "hub")
    assert code == 2
    assert any(f.check == "secret" and ".gardening-log" in f.path for f in findings)


def test_secret_in_non_md_kb_file_hard_fails(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    (kb_dir(root, "hub") / "patterns" / "notes.txt").write_text(
        "api_key = sk_live_abcdef1234567890\n"
    )
    findings, code = run(root, "hub")
    assert code == 2
    assert any(f.check == "secret" and "notes.txt" in f.path for f in findings)


def test_binary_kb_file_reported_unscannable(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    (kb_dir(root, "hub") / "patterns" / "blob.bin").write_bytes(b"\xff\xfe\x00secret")
    findings, code = run(root, "hub")
    assert code == 1
    assert any("unscannable" in f.message for f in findings)


def test_malformed_gardening_date_warns_no_crash(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    log = kb_dir(root, "hub") / ".gardening-log"
    log.write_text("2026-99-99 broken line\n" + log.read_text())
    findings, code = run(root, "hub")
    assert code == 1
    assert any("malformed dated line" in f.message for f in findings)


def test_write_never_touches_schema_failed_entries(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    entry = kb_dir(root, "hub") / "conventions" / "20260701-error-handling.md"
    # break the id (schema hard fail) while its refs still resolve
    entry.write_text(entry.read_text().replace("id: ac74308ae7f3", "id: 000000000000"))
    before = entry.read_text()
    _, code = run(root, "hub", write=True)
    assert code == 2
    assert entry.read_text() == before


def test_ref_symlink_escape_hard_fails(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "escape.py").write_text("outside repo\n")
    root = make_tree(tmp_path, "good_hub")
    (root / "link").symlink_to(outside)
    entry = kb_dir(root, "hub") / "conventions" / "20260701-error-handling.md"
    entry.write_text(entry.read_text().replace("  - src/app.py", "  - link/escape.py"))
    findings, code = run(root, "hub")
    assert code == 2
    assert any("escapes repo root" in f.message for f in findings)


@pytest.mark.parametrize(
    "line",
    [
        'password = "p@ssw0rd!"',
        "client_secret = abcdefghijklmnop",
        "AWS_SECRET_ACCESS_KEY: wJalrXUtnFEMI/K7MDENG",
        "temp key ASIAIOSFODNN7EXAMPLE here",
    ],
)
def test_broadened_secret_rules_fire(line):
    assert secret_rules.scan_text(line), line


def test_allowlist_file_itself_not_scanned(tmp_path):
    root = make_tree(tmp_path, "good_project")
    (kb_dir(root, "project") / ".secret-allowlist").write_text("someone@example.com\n")
    findings, code = run(root, "project")
    assert (findings, code) == ([], 0)


# --- run modes -----------------------------------------------------------


def test_write_mode_maintains_last_verified(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    entry = kb_dir(root, "hub") / "conventions" / "20260701-error-handling.md"
    _, code = run(root, "hub", write=True)
    assert code == 0
    assert f"last_verified: {TODAY.isoformat()}" in entry.read_text()
    once = entry.read_text()
    run(root, "hub", write=True)
    assert entry.read_text() == once  # idempotent


def test_write_mode_adds_missing_last_verified(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    entry = kb_dir(root, "hub") / "conventions" / "20260701-error-handling.md"
    entry.write_text(entry.read_text().replace("last_verified: 2026-07-20\n", ""))
    run(root, "hub", write=True)
    assert f"last_verified: {TODAY.isoformat()}" in entry.read_text()


def test_read_only_never_mutates(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    entry = kb_dir(root, "hub") / "conventions" / "20260701-error-handling.md"
    before = entry.read_text()
    run(root, "hub")
    (root / "src" / "app.py").unlink()  # make it stale
    run(root, "hub")
    assert entry.read_text() == before


def test_write_skips_stale_entries(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    (root / "src" / "app.py").unlink()
    entry = kb_dir(root, "hub") / "conventions" / "20260701-error-handling.md"
    _, code = run(root, "hub", write=True)
    assert code == 1
    assert "last_verified: 2026-07-20" in entry.read_text()  # unchanged


# --- CLI -----------------------------------------------------------------


def cli(root: Path, *args: str):
    return subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "tools" / "kb_lint.py"),
         "--root", str(root), *args],
        capture_output=True,
        text=True,
    )


def freshen_log(root: Path, layout: str):
    log = kb_dir(root, layout) / ".gardening-log"
    log.write_text(f"{date.today().isoformat()} bootstrap: freshened for CLI test\n")


@pytest.mark.parametrize("name,layout", [("good_hub", "hub"), ("good_project", "project")])
def test_cli_exit_0(tmp_path, name, layout):
    root = make_tree(tmp_path, name)
    freshen_log(root, layout)
    result = cli(root, "--layout", layout)
    assert result.returncode == 0, result.stdout + result.stderr


def test_cli_exit_1_and_2(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    freshen_log(root, "hub")
    (root / "src" / "app.py").unlink()
    result = cli(root, "--layout", "hub")
    assert result.returncode == 1
    assert "stale" in result.stdout
    (root / "AGENTS.md").write_text("rule\n" * 150)
    result = cli(root, "--layout", "hub")
    assert result.returncode == 2
    assert "AGENTS.md" in result.stdout


def test_cli_bad_layout_usage_error(tmp_path):
    root = make_tree(tmp_path, "good_hub")
    result = cli(root, "--layout", "nope")
    assert result.returncode == 2  # argparse usage error
    assert "invalid choice" in result.stderr
