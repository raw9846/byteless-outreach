import os
import shutil
import subprocess


def get_backend() -> str:
    """Which AI CLI to shell out to: 'claude' or 'codex'.

    Configurable via AI_BACKEND env var. If unset, auto-detects whichever
    CLI is installed (prefers claude if both are present).
    """
    configured = os.getenv("AI_BACKEND", "").strip().lower()
    if configured in ("claude", "codex"):
        return configured
    if shutil.which("claude"):
        return "claude"
    if shutil.which("codex"):
        return "codex"
    return "claude"


def cli_installed() -> bool:
    binary = "claude" if get_backend() == "claude" else "codex"
    return shutil.which(binary) is not None


def run_prompt(prompt: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a prompt through the configured AI CLI and return the completed process.

    Both CLIs are used in their non-interactive/scripted mode and print the
    final response to stdout, so callers can treat the two backends the same way.
    """
    if get_backend() == "codex":
        cmd = ["codex", "exec", "--skip-git-repo-check", prompt]
    else:
        cmd = ["claude", "-p", prompt]

    # A stray/placeholder ANTHROPIC_API_KEY in .env (loaded into os.environ by
    # config.py's load_dotenv()) makes the Claude CLI try to auth with that
    # literal value instead of the logged-in `claude login` session, breaking
    # every call. Codex's CODEX_API_KEY is a legitimate supported auth path
    # (see README), so only strip ANTHROPIC_API_KEY.
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}

    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
