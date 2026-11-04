"""Read dataset-page frontmatter from the lab wiki (`wiki-llm/datasets/<name>.md`).

This is the wiki-to-code connection: the wiki states which targets a dataset supports, and the
benchmark runs those (via `tasks.select_tasks`) instead of hard-coding a task list.
"""

from pathlib import Path
from typing import Any

from oncolens.frontmatter import split_frontmatter

REFERENCE_DATASET = "msk-chord"  # the real dataset whose page governs the tasks; synthetic-chord is its twin


def dataset_frontmatter(wiki_dir: Path, name: str) -> dict[str, Any]:
    """Frontmatter of `datasets/<name>.md`; raises FileNotFoundError if the page does not exist."""
    meta, _ = split_frontmatter((wiki_dir / "datasets" / f"{name}.md").read_text(encoding="utf-8"))
    return meta


def supported_targets(wiki_dir: Path, name: str = REFERENCE_DATASET) -> list[str]:
    """The page's `supports_targets` list; raises ValueError when absent or not a list of strings."""
    targets = dataset_frontmatter(wiki_dir, name).get("supports_targets")
    if not isinstance(targets, list) or not all(isinstance(t, str) for t in targets):
        raise ValueError(f"datasets/{name}.md: supports_targets must be a list of strings")
    return targets
