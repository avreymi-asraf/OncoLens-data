#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Run a command from this repository on a Google Colab runtime and bring the result home.

The runner is deliberately generic: it ships the *committed* files of this repo (``git archive``,
so no ``.env``, no venv, no stray edits), runs one shell command detached on the VM, waits for it,
then replays the command's stdout and stderr locally and exits with its exit code. That makes a
Colab run indistinguishable from a local one to the lab harness, which parses the last JSON line
of stdout.

    uv run scripts/run_on_colab.py --gpu T4 -- python -m oncolens.bench --model Qwen/Qwen2.5-3B-Instruct

Auth is the one-time browser login of the Colab CLI (`colab whoami`); see the colab-cli skill.
"""

from __future__ import annotations

import argparse
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REMOTE_CODE = "/content/code"
POLL_SECONDS = 15


def colab(*args: str, stdin: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Call the Colab CLI. Its status chatter goes to stderr, program output to stdout."""
    return subprocess.run(["colab", *args], input=stdin, text=True, capture_output=True, check=check)


def run_remote_python(session: str, code: str, timeout: int = 60) -> str:
    """Execute a snippet on the session's kernel and return what it printed.

    The CLI mixes its own `[colab] ...` notices (e.g. "new version available") into stdout; drop them.
    """
    stdout = colab("exec", "-s", session, "--timeout", str(timeout), stdin=code).stdout
    return "\n".join(line for line in stdout.splitlines() if not line.startswith("[colab]"))


def ship(session: str, paths: list[str]) -> None:
    """Upload the committed state of `paths` (default: the whole repo) and unpack it under REMOTE_CODE."""
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "code.tgz"
        subprocess.run(["git", "-C", str(REPO), "archive", "-o", str(archive), "HEAD", "--", *(paths or ["."])], check=True)
        colab("upload", "-s", session, str(archive), "/content/code.tgz")
    run_remote_python(
        session,
        f"import subprocess; subprocess.run('mkdir -p {REMOTE_CODE} && tar xzf /content/code.tgz -C {REMOTE_CODE}',"
        " shell=True, check=True)",
    )


def install_extra(session: str, extra: str) -> None:
    """Install the repo's optional dependency group on the VM (Colab already ships torch; extras must not repeat it)."""
    run_remote_python(
        session,
        f"import subprocess; subprocess.run('uv pip install --system -q \"{REMOTE_CODE}[{extra}]\"', shell=True, check=True)",
        timeout=900,
    )


def launch(session: str, command: str) -> None:
    """Start `command` detached from the kernel; it leaves run.out, run.err and run.exit behind."""
    shell = (
        f"cd {REMOTE_CODE} && PYTHONPATH={REMOTE_CODE} {command} > /content/run.out 2> /content/run.err;"
        " echo $? > /content/run.exit"
    )
    run_remote_python(session, f"import subprocess; subprocess.Popen({shell!r}, shell=True, start_new_session=True)")


def wait_for_exit(session: str, timeout: int) -> int:
    """Poll until the detached command writes its exit code; infra failure if it never does."""
    probe = "import os; p='/content/run.exit'; print(open(p).read().strip() if os.path.exists(p) else 'RUNNING')"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        state = run_remote_python(session, probe).strip()
        if state != "RUNNING":
            return int(state)
        time.sleep(POLL_SECONDS)
    raise TimeoutError(f"command still running after {timeout}s on session {session}")


def bring_home(session: str, out: Path) -> tuple[str, str]:
    """Download the command's stdout and stderr; return both texts."""
    out.mkdir(parents=True, exist_ok=True)
    for name in ("run.out", "run.err"):
        colab("download", "-s", session, f"/content/{name}", str(out / name))
    return (out / "run.out").read_text(), (out / "run.err").read_text()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--gpu", help="T4, L4, G4, A100 or H100; omit for a CPU runtime")
    parser.add_argument("--session", default=f"oncolens-{int(time.time())}", help="Colab session name")
    parser.add_argument("--paths", nargs="+", default=[], help="committed repo paths to ship (default: everything)")
    parser.add_argument("--extra", help="optional dependency group of pyproject.toml to install on the VM first")
    parser.add_argument("--timeout", type=int, default=3600, help="seconds to wait for the command")
    parser.add_argument("--out", type=Path, help="where to keep run.out / run.err (default: temp dir)")
    parser.add_argument("--keep", action="store_true", help="leave the session running afterwards")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="after `--`: the command to run on the VM")
    args = parser.parse_args()

    command = shlex.join(args.command[1:] if args.command[:1] == ["--"] else args.command)
    if not command:
        parser.error("no command given (put it after `--`)")
    if shutil.which("colab") is None:
        sys.exit("colab CLI not found; see the colab-cli skill")

    out = args.out or Path(tempfile.mkdtemp(prefix="colab-run-"))
    colab("new", "-s", args.session, *(["--gpu", args.gpu] if args.gpu else []))
    try:
        print(f"[colab] session {args.session} ({args.gpu or 'cpu'}) up; shipping {args.paths or 'whole repo'}", file=sys.stderr)
        ship(args.session, args.paths)
        if args.extra:
            install_extra(args.session, args.extra)
        launch(args.session, command)
        exit_code = wait_for_exit(args.session, args.timeout)
        stdout, stderr = bring_home(args.session, out)
    finally:
        if not args.keep:
            colab("stop", "-s", args.session, check=False)

    sys.stderr.write(stderr)
    print(f"[colab] exit code {exit_code}; logs in {out}", file=sys.stderr)
    sys.stdout.write(stdout)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
