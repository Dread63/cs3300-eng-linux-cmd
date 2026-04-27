"""
explainer.py

Takes a Linux command and returns a beginner-friendly,
structured explanation of what every part does.
"""

import re
from dataclasses import dataclass

@dataclass
class ExplanationResult:
    summary: str          # What this command does overall
    breakdown: list[str]  # One bullet per token/flag/pipe segment
    warning: str          # Non-empty only when there's a real gotcha
    raw_output: str       # Raw model text (for debugging)
    success: bool
    error: str = ""


class CommandExplainer:
    """
    Uses the LLM to explain a Linux command in plain English.
    """

    _SUMMARY_TAG   = "SUMMARY:"
    _BREAKDOWN_TAG = "BREAKDOWN:"
    _WARNING_TAG   = "WARNING:"

    def __init__(self, llm):
        self._llm = llm

    def explain(self, command: str) -> ExplanationResult:
        """
        Explain a Linux command in plain English.
        """
        if not command.strip():
            return ExplanationResult("", [], "", "", False, "Empty command.")

        system_text = (
            "You are a friendly Linux teacher explaining commands to beginners.\n"
            "Reply with EXACTLY three sections. Follow this example format:\n\n"
            "SUMMARY: Searches for files larger than 100 MB anywhere on the system.\n"
            "BREAKDOWN:\n"
            "- find: searches directories recursively for files\n"
            "- /: starts the search from the root directory\n"
            "- -name '*.log': matches files whose name ends in .log\n"
            "- -size +100M: only includes files larger than 100 MB\n"
            "- 2>/dev/null: hides permission error messages\n"
            "WARNING: Searching from / can be slow on large systems.\n\n"
            "Rules:\n"
            "- Plain English only.\n"
            "- One bullet per meaningful part (base command, each flag, pipes, redirects).\n"
            "- Each bullet under 15 words.\n"
            "- No other sections or preamble.\n"
        )

        try:
            # Consistent with ollama_client.py
            response = self._llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": system_text},
                    {"role": "user", "content": f"Explain this command: {command}"}
                ],
                temperature=0.3,
                max_tokens=250,
            )
            raw = response["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            return ExplanationResult("", [], "", "", False, f"LLM error: {exc}")

        return self._parse_response(raw)

    def _parse_response(self, raw: str) -> ExplanationResult:
        """
        Parse the structured model output into an ExplanationResult.
        """
        summary = warning = ""
        bullets: list[str] = []

        # Pull out SUMMARY
        m = re.search(
            rf"{re.escape(self._SUMMARY_TAG)}\s*(.+?)(?={re.escape(self._BREAKDOWN_TAG)}|$)",
            raw, re.DOTALL | re.IGNORECASE,
        )
        if m:
            summary = m.group(1).strip().splitlines()[0].strip()

        # Pull out BREAKDOWN
        m = re.search(
            rf"{re.escape(self._BREAKDOWN_TAG)}\s*(.+?)(?={re.escape(self._WARNING_TAG)}|$)",
            raw, re.DOTALL | re.IGNORECASE,
        )
        if m:
            for line in m.group(1).strip().splitlines():
                line = line.strip().lstrip("-•* ")
                if line:
                    bullets.append(line)

        # Pull out WARNING
        m = re.search(
            rf"{re.escape(self._WARNING_TAG)}\s*(.+?)$",
            raw, re.DOTALL | re.IGNORECASE,
        )
        if m:
            raw_warn = m.group(1).strip().splitlines()[0].strip()
            if raw_warn.lower() not in {"none", "n/a", "none.", "n/a.", ""}:
                warning = raw_warn

        if not summary and not bullets:
            return ExplanationResult(
                summary=raw.strip().splitlines()[0] if raw.strip() else "No explanation returned.",
                breakdown=[],
                warning="",
                raw_output=raw,
                success=False,
                error="Model did not follow the structured format.",
            )

        return ExplanationResult(
            summary=summary,
            breakdown=bullets,
            warning=warning,
            raw_output=raw,
            success=True,
        )