"""Stop hook: block if Claude's last assistant message opens with a platitude.

Forces Claude to self-correct via {"decision": "block", "reason": "..."}.

Reads `last_assistant_message` directly from the stdin payload — the
transcript file lags the Stop event so reading it yields stale content.
"""
import json
import re
import sys

PLATITUDE_PATTERNS = [
    re.compile(r"^you'?re (absolutely |completely |totally |so )?right",        re.I),
    re.compile(r"^i (completely|totally|absolutely) agree",                     re.I),
    re.compile(r"^(that'?s|what) (a |an )?(great|fantastic|excellent|good|amazing|wonderful|brilliant) (point|question|idea|catch|observation|insight)", re.I),
    re.compile(r"^great (point|question|catch|idea|insight|call)",              re.I),
    re.compile(r"^excellent (point|question|catch|idea|insight)",               re.I),
    re.compile(r"^good (catch|call|point|question|idea)",                       re.I),
    re.compile(r"^well (spotted|put|said|caught)",                              re.I),
    re.compile(r"^perfect[!.]",                                                 re.I),
    re.compile(r"^exactly!",                                                    re.I),
    re.compile(r"^(absolutely|of course|totally|definitely)[!.]",               re.I),
    re.compile(r"^fantastic[!.]",                                               re.I),
    re.compile(r"^amazing[!.]",                                                 re.I),
]


def detect_platitude(text: str):
    """Return matched substring if text opens with a platitude, else None."""
    if not text:
        return None
    stripped = text.lstrip()
    for rx in PLATITUDE_PATTERNS:
        m = rx.match(stripped)
        if m:
            return m.group(0)
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    # Avoid infinite loops: if a previous Stop hook already blocked, don't block again.
    if payload.get("stop_hook_active"):
        return 0

    text = payload.get("last_assistant_message", "")
    hit = detect_platitude(text)
    if not hit:
        return 0

    reason = (
        "Responding with a platitude sacrifices substance for stylistic politeness. "
        "This creates a quiet failure that erodes trust and diminishes utility. "
        "Provide objective and independent assessment without softening or hedging. "
    )

    json.dump({"decision": "block", "reason": reason}, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
