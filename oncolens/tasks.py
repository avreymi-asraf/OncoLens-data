"""The benchmark's tasks: binary questions about a patient, labelled from `outcomes`.

A task turns a record into a prompt (body + question + strict answer format) and into a gold letter.
Each task names the wiki `target` it implements, which is how `wiki.supported_targets` decides what
to run. To add a task, append it to `TASKS`; nothing else changes.
"""

from collections.abc import Callable
from dataclasses import dataclass

from oncolens.records import Outcomes, Record

LETTERS = ("A", "B")
ANSWER_FORMAT = "Answer with a single letter: A or B."


@dataclass(frozen=True)
class Task:
    """Binary task: option B is the positive class, option A the negative one."""

    id: str
    target: str  # the `supports_targets` entry in the wiki dataset page this task implements
    question: str
    negative: str  # option A text
    positive: str  # option B text
    is_positive: Callable[[Outcomes], bool]

    def label(self, record: Record) -> str:
        """Gold letter, derived from the withheld outcomes."""
        return LETTERS[1] if self.is_positive(record.outcomes) else LETTERS[0]

    def prompt(self, record: Record) -> str:
        """Record body, then the same question and answer format for every record (no outcome enters)."""
        return (
            f"{record.prompt_text}\n\n"
            f"Question: {self.question}\n"
            f"A. {self.negative}\n"
            f"B. {self.positive}\n\n"
            f"{ANSWER_FORMAT}"
        )


TASKS = {
    task.id: task
    for task in (
        Task(
            id="overall-survival",
            target="overall-survival",
            question="At the end of follow-up, is this patient deceased?",
            negative="No, the patient is still living.",
            positive="Yes, the patient is deceased.",
            is_positive=lambda outcomes: outcomes.os_status == "DECEASED",
        ),
        Task(
            id="metastasis",
            target="metastasis",
            question="Is the liver among this patient's metastatic sites?",
            negative="No, there is no liver metastasis.",
            positive="Yes, there is liver metastasis.",
            is_positive=lambda outcomes: "Liver" in outcomes.metastatic_sites,
        ),
    )
}


def select_tasks(targets: list[str]) -> tuple[list[Task], list[str]]:
    """Match wiki targets to implemented tasks; returns (tasks, unsupported targets), wiki order kept.

    Unsupported targets are returned, not dropped, so reports can state what the wiki promises
    but the benchmark cannot yet run.
    """
    by_target = {task.target: task for task in TASKS.values()}
    tasks = [by_target[t] for t in targets if t in by_target]
    return tasks, [t for t in targets if t not in by_target]
