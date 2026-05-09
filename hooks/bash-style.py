"""PreToolUse hook on Bash: enforce ~/CLAUDE.md command-style rules.

Reads tool input from stdin as JSON, blocks risky/style-violating
commands, and emits a rule-specific violation label + correction
text as the permissionDecisionReason.
"""
import json
import re
import shlex
import sys


def _tokenize(cmd, posix=True):
    """Return shlex tokens, or None if quoting is malformed."""
    try:
        return shlex.split(cmd, posix=posix)
    except ValueError:
        return None


def _kw(target):
    """Matcher: target appears as a standalone token."""
    return lambda tokens: tokens is not None and target in tokens


def _sub(s):
    """Matcher: s appears as a substring of any token."""
    return lambda tokens: tokens is not None and any(s in t for t in tokens)


# (matcher, violation_label, correction) — matchers receive posix=True tokens
GIT_C_RULE = (
    lambda tokens: tokens is not None and len(tokens) >= 2 and tokens[0] == "git" and "-C" in tokens,
    "git -C flag",
    "Navigate to the target directory, then run git without -C.",
)

# (matcher, violation_label, correction) — matchers receive posix=True tokens
COMPOUND_RULES = [
    # Keyword constructs first — more informative than punctuation rules.
    (_kw("if"),    "if conditional",
     "Express the conditional across separate Bash calls: run the test, read the result, then issue the next call based on its outcome."),
    (_kw("for"),   "for loop",
     "Iterate in the agent loop: list items first, then issue one Bash call per item."),
    (_kw("while"), "while loop",
     "Iterate in the agent loop: run one Bash call per iteration, check the condition, decide whether to continue."),
    (_kw("until"), "until loop",
     "Iterate in the agent loop: run one Bash call per iteration, check the condition, decide whether to continue."),
    (_kw("case"),  "case conditional",
     "Capture the discriminant in one Bash call, then dispatch via separate calls in the agent loop."),
    (_sub("$("),   "command substitution $(...)",
     "Run the inner command as its own Bash call, capture the output, then use the result in your next call."),
    (_sub("`"),    "backtick command substitution",
     "Run the inner command as its own Bash call, capture the output, then use the result in your next call."),
    (_kw("&&"),    "logical AND (&&)",
     "Issue each command as a separate Bash tool call. The harness evaluates one command at a time."),
    (_kw("||"),    "logical OR (||)",
     "Issue each command as a separate Bash tool call and branch on the first call's exit code."),
    (_kw("|"),     "pipe (|)",
     "Run each pipeline stage as a separate Bash call, or replace the pipeline with a dedicated tool (Read/Grep/Glob)."),
    (_sub(";"),    "command separator (;)",
     "Issue each command as a separate Bash tool call."),
]

# head -> (violation_label, correction)
#
# SUSPENDED: find / ls / grep / rg redirect to Glob and Grep, which are absent
# from the tool registry due to anthropics/claude-code#52121. Restore by
# uncommenting once those tools are available again (verify availability with
# ToolSearch select:Glob,Grep on a fresh session, or by direct invocation).
FILE_OP_RULES = {
    # "find": ("file operation via Bash (find)",
    #          "Use the Glob for dedicated file-discovery."),
    # "ls":   ("file operation via Bash (ls)",
    #          "Use the Glob for dedicated file-discovery."),
    # "grep": ("file operation via Bash (grep)",
    #          "Use the Grep for dedicated content-search."),
    # "rg":   ("file operation via Bash (rg)",
    #          "Use the Grep for dedicated content-search."),
    "cat":  ("file operation via Bash (cat)",
             "Use the Read for dedicated file-reading."),
    "head": ("file operation via Bash (head)",
             "Use the Read for dedicated file-reading."),
    "tail": ("file operation via Bash (tail)",
             "Use the Read for dedicated file-reading."),
    "sed":  ("file operation via Bash (sed)",
             "Use the Edit for dedicated file-editing."),
    "awk":  ("file operation via Bash (awk)",
             "Use the Edit for dedicated file-editing."),
}

ECHO_REDIR_RULE = (
    re.compile(r"^\s*echo\b.*\s>>?\s"),
    "file writing via echo redirection",
    "Use the Write tool — the dedicated file-writing tool per CLAUDE.md.",
)


# SUSPENDED: SHELL_GLOB_LIST_RULE redirects to Glob, which is absent due to
# anthropics/claude-code#52121. Restore by uncommenting the helper, the rule
# constant, AND the invocation in detect() once Glob is registered again.
# The matcher uses posix=False shlex tokenization so a token starting with '
# or " came from a quoted region and the * is a literal, not a shell glob.
#
# def _is_unquoted_glob_in_echo_args(tokens_quoted):
#     if not tokens_quoted or len(tokens_quoted) < 2:
#         return False
#     if tokens_quoted[0] not in ("echo", "printf"):
#         return False
#     for tok in tokens_quoted[1:]:
#         if "*" in tok and not (tok.startswith("'") or tok.startswith('"')):
#             return True
#     return False
#
#
# SHELL_GLOB_LIST_RULE = (
#     _is_unquoted_glob_in_echo_args,
#     "file listing via shell glob",
#     "Use the Glob tool for dedicated file-discovery.",
# )


def first_token(cmd: str) -> str:
    # Strip leading FOO=bar style env-var assignments so the head resolves to the actual command.
    cmd = re.sub(r"^(?:[A-Z_][A-Z0-9_]*=\S+\s+)+", "", cmd.strip())
    parts = cmd.split(None, 1)
    return parts[0] if parts else ""


def detect(cmd: str):
    """Return (violation_label, correction) or None."""
    tokens = _tokenize(cmd, posix=True)

    matcher, label, correction = GIT_C_RULE
    if matcher(tokens):
        return (label, correction)

    head = first_token(cmd)
    if head in FILE_OP_RULES:
        return FILE_OP_RULES[head]

    rx, label, correction = ECHO_REDIR_RULE
    if rx.search(cmd):
        return (label, correction)

    # SUSPENDED — see SHELL_GLOB_LIST_RULE above. Restore in unison:
    # matcher, label, correction = SHELL_GLOB_LIST_RULE
    # if matcher(_tokenize(cmd, posix=False)):
    #     return (label, correction)

    for matcher, label, correction in COMPOUND_RULES:
        if matcher(tokens):
            return (label, correction)

    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    if payload.get("tool_name") != "Bash":
        return 0

    cmd = (payload.get("tool_input") or {}).get("command", "")
    if not cmd:
        return 0

    hit = detect(cmd)
    if not hit:
        return 0

    label, correction = hit
    reason = f"Command Style Violation (see `~/CLAUDE.md`): {label} - {correction}"

    json.dump({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
