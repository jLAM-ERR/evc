"""kblib — stdlib-only library behind kb-lint and the evc-plugins tooling.

Normative reference: CONTRACT.md in the evc repo root. Vendored copies of
this package must be byte-identical to their SOURCE-marked evc commit.
"""

from kblib.frontmatter import (  # noqa: F401
    FrontmatterError,
    entry_id,
    normalize_body,
    parse,
    split,
)
from kblib.secret_rules import Finding as SecretFinding  # noqa: F401
from kblib.secret_rules import load_allowlist, scan_text  # noqa: F401
