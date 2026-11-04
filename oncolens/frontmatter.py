"""Split a Markdown file into its YAML frontmatter and body.

Shared by `records` (patient files) and `wiki` (dataset pages): both use the same
`---`-fenced header, so there is exactly one parser for it.
"""

from typing import Any

import yaml


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Return (frontmatter mapping, body). Raises ValueError if the header is missing or malformed."""
    if not text.startswith("---\n"):
        raise ValueError("file does not start with a '---' frontmatter fence")
    header, fence, body = text[len("---\n") :].partition("\n---\n")
    if not fence:
        raise ValueError("frontmatter is not closed by a '---' fence")
    meta = yaml.safe_load(header)
    if not isinstance(meta, dict):
        raise ValueError("frontmatter is not a YAML mapping")
    return meta, body
