#!/usr/bin/env python3
"""Block tool commands that can print complete credentials before execution.

The guard intentionally reports only a generic reason. It never reflects the
submitted command because the command itself may contain a credential.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import bisect
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import sys
import time
from typing import Any


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str = ""


_LEGACY_BLOCKS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"\bpm2\s+(?:jlist|prettylist|env|show|describe)\b", re.I),
        "Use an approved PM2 status wrapper; raw PM2 environment output is blocked.",
    ),
    (
        re.compile(r"/proc/(?:\d+|\$\{?[^/\s}]+\}?)/(?:environ|cmdline)\b", re.I),
        "Direct process environment and command-line reads are blocked.",
    ),
    (
        re.compile(r"\b(?:printenv|export\s+-p)(?:\s|[;&|'\"\)`]|$)", re.I),
        "Whole-environment output is blocked; request only a non-secret status field.",
    ),
    (
        # Not the member access in process.env or ENV.env: only a bare env command.
        re.compile(r"(?<![.$-])\benv\s*(?:[;&|'\"\)`]|$)", re.I),
        "Whole-environment output is blocked; use env only to launch a scoped command.",
    ),
    (
        re.compile(r"(?:^|[;&|]\s*)set\s*(?:[;&|]|$)", re.I),
        "Shell state output is blocked because it may contain exported credentials.",
    ),
    (
        re.compile(r"\bsystemctl\s+(?:show-environment|show\b[^;&|]*(?:--property|-p)[=\s]*Environment\b)", re.I),
        "System service environment output is blocked.",
    ),
    (
        re.compile(r"\bsystemctl\s+show\b(?![^;&|]*(?:--property|-p)(?:=|\s))", re.I),
        "Raw system service inspection is blocked; request one approved non-secret property.",
    ),
    (
        re.compile(r"\b(?:ps\s+(?:aux(?:ww)?|-[a-z]*[ef][a-z]*)|pgrep\s+-[a-z]*[af][a-z]*)\b", re.I),
        "Broad process argument output is blocked; request only PID, user, and executable fields.",
    ),
    (
        re.compile(
            r"(?:^|[;&|\n\r]\s*|['\"]\s*)(?:history|fc\s+-l)(?:\s|['\";&|]|$)|"
            r"(?:^|[/\s])\.(?:bash|zsh)_history\b",
            re.I,
        ),
        "Shell history output is blocked because commands may contain credentials.",
    ),
    (
        re.compile(
            r"(?:console\.log|print|json\.dumps|var_dump|print_r)\s*\([^)]*"
            r"(?:os\.environ|process\.env|\$_ENV|\$_SERVER)|"
            r"\b(?:node|python3?)\b[^\n;&|]*\s-[p]\s+[^\n;&|]*"
            r"(?:os\.environ|process\.env)",
            re.I,
        ),
        "Programming-language environment dumps are blocked.",
    ),
    (
        re.compile(r"\blaunchctl\s+(?:print|export|getenv)\b", re.I),
        "Raw launch service output is blocked because it may include environment values.",
    ),
    (
        re.compile(r"\bdocker\s+compose\s+config\b", re.I),
        "Rendered container configuration is blocked because interpolation may reveal credentials.",
    ),
    (
        re.compile(r"\bkubectl\s+(?:get|describe|edit)\s+secrets?\b", re.I),
        "Raw Kubernetes secret inspection is blocked.",
    ),
    (
        re.compile(r"\baws\s+secretsmanager\s+get-secret-value\b", re.I),
        "Secret-store value retrieval must use an approved non-printing wrapper.",
    ),
    (
        re.compile(r"\bgcloud\s+secrets\s+versions\s+access\b", re.I),
        "Secret-store value retrieval must use an approved non-printing wrapper.",
    ),
    (
        re.compile(r"\bvault\s+kv\s+get\b", re.I),
        "Secret-store value retrieval must use an approved non-printing wrapper.",
    ),
    (
        re.compile(r"\b(?:vercel\s+env\s+pull|heroku\s+config(?:\s|$)|doppler\s+secrets(?:\s|$))", re.I),
        "Provider environment export is blocked; use scoped owner entry or a non-printing wrapper.",
    ),
    (
        re.compile(
            r"\b(?:security\s+find-generic-password\b[^;&|]*\s-w\b|"
            r"op\s+read\s+op://|pass\s+show\b)",
            re.I,
        ),
        "Password-store value retrieval must use an owner-only or non-printing wrapper.",
    ),
    (
        re.compile(
            r"\b(?:cat|head|tail|less|more|sed|awk|grep|rg|jq|cut|tr|base64|xxd|strings|perl|python3?|node)\b"
            r"[^\n;&|]*(?:(?<!process)\.env(?:\b|[._-])|\.config/sifututor/[^\s'\"]*"
            r"(?:\.conf|\.env)|credentials(?:\.json)?|id_(?:rsa|ed25519))",
            re.I,
        ),
        "Direct output from a credential-bearing file is blocked; use an approved wrapper.",
    ),
    (
        re.compile(
            r"\b(?:echo|printf)\b[^\n;&|]*\$\{?[A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASS|CREDENTIAL)[A-Z0-9_]*\}?",
            re.I,
        ),
        "Printing a credential-shaped environment variable is blocked.",
    ),
    (
        re.compile(r"(?:^|[;&|]\s*)(?:set\s+-x|(?:bash|sh|zsh)\s+-x)\b", re.I),
        "Shell tracing is blocked for agent commands because expanded secrets may be logged.",
    ),
    (
        re.compile(r"\bcurl\b[^\n;&|]*(?:-v\b|--verbose\b)[^\n]*(?:authorization|bearer|api[_-]?key|token|secret)", re.I),
        "Verbose authenticated HTTP output is blocked because request headers may be exposed.",
    ),
)


def _safe_inspect_formats(command: str) -> bool:
    """Accept only literal scalar status templates, never whole inspect objects.

    This is a deliberately narrow command recognizer, not a shell interpreter.
    Unknown/dynamic templates need a reviewed non-printing wrapper.
    """
    for docker in re.finditer(r"\bdocker\b([^;\n\r&|#]*)", command, re.I):
        tail = docker.group(1)
        if tail.rstrip().endswith("\\"):
            return False
        if not re.search(r"\binspect\b", tail, re.I):
            continue
        inspect = re.match(r"\s+(?:container\s+)?inspect\b(.*)", tail, re.I)
        if inspect is None:
            # Global options/unknown command forms require a reviewed wrapper.
            return False
        arguments = inspect.group(1)
        # Tokenize only this bounded simple segment. A format-looking string
        # inside one quoted positional argument is not a Docker option.
        try:
            tokens = shlex.split(arguments)
        except ValueError:
            return False
        if any(any(c in token for c in "$`<>()") for token in tokens):
            return False
        templates = []
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token == "--":
                break
            if token in {"--format", "-f"}:
                index += 1
                if index >= len(tokens):
                    return False
                templates.append(tokens[index])
            elif token.startswith("--format="):
                templates.append(token[len("--format="):])
            elif token.startswith("-f"):
                templates.append(token[2:].removeprefix("="))
            index += 1
        if not templates:
            return False
        for template in templates:
            if not template:
                return False
            if not re.fullmatch(
                r"\{\{\s*(?:json\s+)?\.(?:State\.(?:Status|Running|Restarting|Paused|Dead|ExitCode|Health\.Status)|RestartCount|Id)\s*\}\}",
                template,
            ):
                return False
    return True


def _strip_quoted(command: str) -> str:
    """Drop quoted spans so a pipe inside a search pattern is not a shell pipe.

    Substitutions and newlines are rejected by the caller on the raw text. An
    unbalanced quote stays in the result, which keeps the check conservative.
    """
    return re.sub(r"'[^']*'|\"(?:\\.|[^\"\\])*\"", "", command)


def _legacy_evaluate_command(command: str) -> Decision:
    """Word-matching rules kept as the conservative fallback.

    Used only when a command cannot be parsed. Also the frozen baseline that the
    regression tests compare the operation-based rules against.
    """

    # Newlines delimit shell commands; flattening them lets a following command
    # lend its harmless-looking format to a preceding raw inspect command.
    compact = str(command).strip()
    if not compact:
        return Decision(True)
    if re.fullmatch(
        r"\s*(?:python3\s+)?(?:\S*/)?worktree-lifecycle\.py\s+attach-local-env"
        r"(?:\s+[^;&|`$\r\n]+)+\s*",
        compact,
    ):
        return Decision(True)
    if (
        re.match(r"^\s*(?:rg|grep)\b", compact, re.I)
        and not re.search(r"(?:\$|<)\(|`|[\n\r]", compact)
        and not re.search(r"[;&|]", _strip_quoted(compact))
        and not re.search(
            r"(?:(?<!process)\.env(?:\b|[._-])|\.config/sifututor/[^\s'\"]*(?:\.conf|\.env)|"
            r"credentials(?:\.json)?|id_(?:rsa|ed25519))",
            compact,
            re.I,
        )
    ):
        return Decision(True)
    if not _safe_inspect_formats(compact):
        return Decision(False, "Container inspection requires a literal approved non-secret status field; use a reviewed wrapper for other output.")
    for pattern, reason in _LEGACY_BLOCKS:
        if pattern.search(compact):
            return Decision(False, reason)
    return Decision(True)


# ---------------------------------------------------------------------------
# Operation-based command inspection (issue #321)
#
# The legacy rules above match WORDS anywhere in the command text, so a grep
# pattern, a heredoc body, a commit message or an argument such as
# `artisan env` was blocked just for containing a trigger word. The engine
# below parses the command into simple commands and decides on the dangerous
# OPERATION: a reader whose target is a secret file and whose output reaches
# the terminal, a bare environment dump, a full process-argument listing, an
# echo of a secret variable, a language-level environment dump.
#
# It is a seatbelt against accidental disclosure by a well-meaning agent, not
# a sandbox. Anything the parser cannot understand falls back to the legacy
# word rules, so an unparseable command is never treated more loosely than
# before.
# ---------------------------------------------------------------------------

_MAX_DEPTH = 8


class _ParseFail(Exception):
    """The command is not understood well enough to inspect structurally."""


@dataclass
class _Word:
    text: str = ""
    quoted: bool = False
    expands: list[str] = field(default_factory=list)


@dataclass
class _Heredoc:
    expand: bool
    strip_tabs: bool
    body: str = ""


@dataclass
class _Cmd:
    words: list[_Word] = field(default_factory=list)
    redirs: list[tuple[str, _Word]] = field(default_factory=list)
    heredocs: list[_Heredoc] = field(default_factory=list)
    herestrings: list[_Word] = field(default_factory=list)
    subs: list[list["_Cmd"]] = field(default_factory=list)
    raw: str = ""
    piped: bool = False
    tail: list["_Cmd"] = field(default_factory=list)


_NAME_AT_START = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\+?=")
_WORD_BREAK = frozenset(" \t\r\n;&|()<>")


class _Parser:
    """A small shell reader: quotes, substitutions, heredocs, redirects.

    It records what a security check needs (words, redirect targets, heredoc
    bodies, nested substitutions) and refuses anything it does not model.
    """

    def __init__(self, text: str) -> None:
        self.t = text
        self.n = len(text)
        self.i = 0

    # -- words -----------------------------------------------------------
    def _word(self, cmd: _Cmd) -> _Word:
        t, n = self.t, self.n
        word = _Word()
        parts: list[str] = []
        while self.i < n:
            c = t[self.i]
            if c in _WORD_BREAK:
                break
            if c == "\\":
                if self.i + 1 < n and t[self.i + 1] == "\n":
                    self.i += 2
                    continue
                if self.i + 1 < n:
                    parts.append(t[self.i + 1])
                    word.quoted = True
                    self.i += 2
                    continue
                self.i += 1
                continue
            if c == "'":
                end = t.find("'", self.i + 1)
                if end < 0:
                    raise _ParseFail
                parts.append(t[self.i + 1:end])
                word.quoted = True
                self.i = end + 1
                continue
            if c == '"':
                self._double_quoted(word, parts, cmd)
                continue
            if c == "$":
                self._dollar(word, parts, cmd, in_double=False)
                continue
            if c == "`":
                self._backtick(parts, cmd)
                continue
            parts.append(c)
            self.i += 1
        word.text = "".join(parts)
        return word

    def _double_quoted(self, word: _Word, parts: list[str], cmd: _Cmd) -> None:
        t, n = self.t, self.n
        word.quoted = True
        self.i += 1
        while self.i < n:
            c = t[self.i]
            if c == '"':
                self.i += 1
                return
            if c == "\\" and self.i + 1 < n:
                nxt = t[self.i + 1]
                if nxt == "\n":
                    self.i += 2
                    continue
                if nxt in '$`"\\':
                    parts.append(nxt)
                else:
                    parts.append("\\" + nxt)
                self.i += 2
                continue
            if c == "$":
                self._dollar(word, parts, cmd, in_double=True)
                continue
            if c == "`":
                self._backtick(parts, cmd)
                continue
            parts.append(c)
            self.i += 1
        raise _ParseFail

    def _dollar(self, word: _Word, parts: list[str], cmd: _Cmd, *, in_double: bool) -> None:
        t, n = self.t, self.n
        nxt = t[self.i + 1] if self.i + 1 < n else ""
        if nxt == "(":
            if t[self.i + 2:self.i + 3] == "(":
                end = self._matching(self.i + 1, "(", ")")
                parts.append(t[self.i:end + 1])
                self.i = end + 1
                return
            self.i += 2
            cmd.subs.append(self._list(nested=True))
            parts.append("$(...)")
            return
        if nxt == "{":
            end = self._matching(self.i + 1, "{", "}")
            inner = t[self.i + 2:end]
            if not inner.startswith("#"):
                match = _NAME_AT_START.match(inner.lstrip("!"))
                if match:
                    word.expands.append(match.group(0))
            cmd.subs.extend(_embedded_substitutions(inner))
            parts.append(t[self.i:end + 1])
            self.i = end + 1
            return
        if nxt == "'" and not in_double:
            end = self.i + 2
            while end < n and t[end] != "'":
                end += 2 if t[end] == "\\" else 1
            if end >= n:
                raise _ParseFail
            parts.append(t[self.i + 2:end])
            word.quoted = True
            self.i = end + 1
            return
        match = _NAME_AT_START.match(t, self.i + 1)
        if match:
            word.expands.append(match.group(0))
            parts.append("$" + match.group(0))
            self.i = match.end()
            return
        parts.append("$")
        self.i += 1
        if nxt and nxt in "@*#?$!-0123456789":
            parts.append(nxt)
            self.i += 1

    def _backtick(self, parts: list[str], cmd: _Cmd) -> None:
        t, n = self.t, self.n
        end = self.i + 1
        while end < n and t[end] != "`":
            end += 2 if t[end] == "\\" else 1
        if end >= n:
            raise _ParseFail
        inner = t[self.i + 1:end].replace("\\`", "`")
        cmd.subs.append(_Parser(inner)._list(nested=False))
        parts.append("`...`")
        self.i = end + 1

    def _matching(self, open_index: int, opener: str, closer: str) -> int:
        depth = 0
        j = open_index
        while j < self.n:
            ch = self.t[j]
            if ch == "\\":
                j += 2
                continue
            if ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    return j
            j += 1
        raise _ParseFail

    # -- commands --------------------------------------------------------
    def _list(self, *, nested: bool) -> list[_Cmd]:
        t, n = self.t, self.n
        out: list[_Cmd] = []
        cur = _Cmd()
        start: int | None = None
        pending: list[tuple[_Heredoc, str]] = []

        def finish(position: int) -> None:
            nonlocal cur, start
            if cur.words or cur.redirs or cur.subs or cur.heredocs or cur.herestrings:
                cur.raw = t[start if start is not None else position:position].strip()
                out.append(cur)
            cur = _Cmd()
            start = None

        while self.i < n:
            c = t[self.i]
            if c in " \t":
                self.i += 1
                continue
            if c == "\\" and t[self.i + 1:self.i + 2] == "\n":
                self.i += 2
                continue
            if c in "\n\r":
                finish(self.i)
                self.i += 2 if t[self.i:self.i + 2] == "\r\n" else 1
                if pending:
                    self._read_heredoc_bodies(pending)
                    pending = []
                continue
            if c == "#":
                while self.i < n and t[self.i] not in "\n\r":
                    self.i += 1
                continue
            if c == ";":
                finish(self.i)
                self.i += 1
                if t[self.i:self.i + 1] in (";", "&"):
                    self.i += 1
                continue
            if c == "&" and t[self.i + 1:self.i + 2] != ">":
                finish(self.i)
                self.i += 2 if t[self.i + 1:self.i + 2] == "&" else 1
                continue
            if c == "|":
                before_count = len(out)
                finish(self.i)
                if len(out) > before_count:
                    out[-1].piped = True
                self.i += 2 if t[self.i + 1:self.i + 2] in ("|", "&") else 1
                continue
            if c == "(":
                if t[self.i + 1:self.i + 2] == "(":
                    self.i = self._matching(self.i, "(", ")") + 1
                    continue
                finish(self.i)
                self.i += 1
                group = _Cmd()
                group.subs.append(self._list(nested=True))
                out.append(group)
                continue
            if c == ")":
                if not nested:
                    raise _ParseFail
                finish(self.i)
                self.i += 1
                if pending:
                    self._read_heredoc_bodies(pending)
                return out
            if c in "<>&":
                if start is None:
                    start = self.i
                if t.startswith("<(", self.i) or t.startswith(">(", self.i):
                    self.i += 2
                    cur.subs.append(self._list(nested=True))
                    cur.words.append(_Word(text="<(...)"))
                    continue
                op = self._redirect_operator()
                while self.i < n and t[self.i] in " \t":
                    self.i += 1
                target = self._word(cur)
                if not target.text and not target.quoted:
                    raise _ParseFail
                if op in ("<<", "<<-"):
                    heredoc = _Heredoc(expand=not target.quoted, strip_tabs=op == "<<-")
                    cur.heredocs.append(heredoc)
                    pending.append((heredoc, target.text))
                elif op == "<<<":
                    cur.herestrings.append(target)
                else:
                    cur.redirs.append((op, target))
                continue
            if start is None:
                start = self.i
            before = self.i
            word = self._word(cur)
            if (
                word.text.isdigit()
                and not word.quoted
                and self.i < n
                and t[self.i] in "<>"
            ):
                continue
            if self.i == before:
                raise _ParseFail
            if not word.text and not word.quoted:
                continue
            cur.words.append(word)
        if nested:
            raise _ParseFail
        finish(self.i)
        return out

    def _redirect_operator(self) -> str:
        t = self.t
        for op in ("<<<", "<<-", "&>>", "<<", ">>", "&>", "<&", ">&", ">|", "<>", "<", ">"):
            if t.startswith(op, self.i):
                self.i += len(op)
                return op
        raise _ParseFail

    def _read_heredoc_bodies(self, pending: list[tuple[_Heredoc, str]]) -> None:
        t, n = self.t, self.n
        for heredoc, delimiter in pending:
            lines: list[str] = []
            while self.i < n:
                end = t.find("\n", self.i)
                if end < 0:
                    end = n
                line = t[self.i:end].rstrip("\r")
                self.i = min(end + 1, n)
                if (line.lstrip("\t") if heredoc.strip_tabs else line) == delimiter:
                    break
                lines.append(line)
            heredoc.body = "\n".join(lines)


def _embedded_substitutions(text: str) -> list[list[_Cmd]]:
    """Find $(...) and `...` inside text that the shell would expand."""

    found: list[list[_Cmd]] = []
    position = 0
    while position < len(text):
        index = text.find("$(", position)
        if index < 0 or text[index + 2:index + 3] == "(":
            position = index + 2 if index >= 0 else len(text)
            continue
        parser = _Parser(text)
        parser.i = index + 2
        try:
            found.append(parser._list(nested=True))
        except _ParseFail:
            position = index + 2
            continue
        position = parser.i
    for match in re.finditer(r"`([^`\\]*(?:\\.[^`\\]*)*)`", text):
        try:
            found.append(_Parser(match.group(1))._list(nested=False))
        except _ParseFail:
            continue
    return found


# -- vocabulary ---------------------------------------------------------------

_KEYWORDS = frozenset(
    {"if", "then", "else", "elif", "fi", "while", "until", "do", "done", "for",
     "select", "case", "esac", "function", "{", "}", "!"}
)

# command -> (flags that take a value, number of leading positionals to skip)
_WRAPPERS: dict[str, tuple[frozenset[str], int]] = {
    "sudo": (frozenset("-u -g -h -p -C -r -t -D -R -U -T".split()), 0),
    "doas": (frozenset({"-u", "-C"}), 0),
    "nohup": (frozenset(), 0),
    "time": (frozenset({"-f", "-o"}), 0),
    "command": (frozenset(), 0),
    "builtin": (frozenset(), 0),
    "exec": (frozenset({"-a"}), 0),
    "nice": (frozenset({"-n"}), 0),
    "ionice": (frozenset({"-c", "-n", "-p"}), 0),
    "timeout": (frozenset({"-k", "-s"}), 1),
    "stdbuf": (frozenset({"-i", "-o", "-e"}), 0),
    "setsid": (frozenset(), 0),
    "caffeinate": (frozenset({"-t", "-w"}), 0),
    "xargs": (frozenset("-n -I -L -P -d -E -s -a -J".split()), 0),
    "watch": (frozenset({"-n", "-d"}), 0),
    "unbuffer": (frozenset(), 0),
    "flock": (frozenset({"-w", "-E"}), 1),
    "eval": (frozenset(), 0),
}

_SHELLS = frozenset({"bash", "sh", "zsh", "dash", "ksh", "ash", "su"})
_INTERPRETER_NAME = re.compile(r"^(?:python[\d.]*|node(?:js)?|bun|deno|tsx|php[\d.]*|ruby|perl)$")

_PRINT_READERS = frozenset(
    "cat tac head tail less more most bat batcat nl od xxd hexdump strings base64 base32 "
    "cut tr sort uniq paste fold rev column expand unexpand fmt pr join comm diff sdiff "
    "sed awk gawk mawk nawk jq yq grep egrep fgrep rg ag ack".split()
)
_PROGRAM_POSITIONAL = frozenset(
    "grep egrep fgrep rg ag ack sed awk gawk mawk nawk jq yq".split()
)
_SEARCHERS = frozenset("grep egrep fgrep rg ag ack".split())
_TRANSFER_TOOLS = frozenset({"curl", "wget", "http", "https", "nc", "ncat", "netcat", "socat"})
_METADATA_TOOLS = frozenset(
    "ls stat wc file test [ [[ readlink realpath du df md5 md5sum shasum sha1sum sha256sum cksum "
    "touch chmod chown mkdir rm mv ln open basename dirname which type whereis".split()
)

_SECRET_NAME_SEGMENT_END = re.compile(
    r"(?:KEYS?|TOKENS?|SECRETS?|PASS(?:WORD|WD)?|CREDENTIALS?)$"
)
_SECRET_NAME_SEGMENT_START = re.compile(r"^(?:TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL)")

_DOC_OR_CODE_SUFFIXES = (
    ".md", ".mdx", ".rst", ".py", ".ts", ".tsx", ".js", ".mjs", ".php", ".sh", ".example",
    ".sample", ".template", ".yml-template",
)
_NOT_ENV_FILE_OWNERS = frozenset(
    {"process", "import.meta", "os", "app", "config", "deno", "settings", "window",
     "global", "self", "rails", "this", "req", "ctx", "context", "module", "bun"}
)


def _base(path: str) -> str:
    return path.rsplit("/", 1)[-1]


def _secret_name(name: str) -> bool:
    return any(
        _SECRET_NAME_SEGMENT_END.search(segment) or _SECRET_NAME_SEGMENT_START.match(segment)
        for segment in name.upper().split("_")
    )


def _is_secret_path(token: str) -> bool:
    """True when the token names a file that holds credentials or history."""

    if not token or len(token) > 1024:
        return False
    pieces = [token]
    for separator in ("=", ":", "@"):
        if separator in token:
            pieces.extend(piece for piece in token.split(separator) if piece)
    return any(_secret_path_piece(piece) for piece in pieces)


def _private_config_file(relative: str, path: str) -> bool:
    """Files in ~/.config/sifututor that hold credentials (not data exports or docs)."""

    base = _base(relative.rstrip("/")).lower()
    if path.endswith(_DOC_OR_CODE_SUFFIXES) or base.endswith(".example"):
        return False
    if relative.startswith("agent-access/runtime/"):
        return False
    if relative.startswith("agent-access/") and base:
        return True
    if re.search(r"\.(?:conf|env|key|pem)(?:\.|$)", base):
        return True
    if re.search(r"token|passphrase|secret|credential|password", base):
        return True
    # everything in the directory at once
    return base == "*"


def _secret_path_piece(piece: str) -> bool:
    path = piece.strip().strip("\"'")
    if not path:
        return False
    config_dir = re.search(r"(?:^|/)\.config/sifututor(?:/|$)(.*)", path)
    if config_dir:
        return _private_config_file(config_dir.group(1), path)
    if path.startswith(("live/", "./live/")) or "/Sifututor/live/" in path:
        return True
    base = _base(path.rstrip("/"))
    if not base:
        return False
    if re.fullmatch(r"\.env\S*\.(?:example|sample|template|dist|tpl)", base):
        # Committed templates hold placeholders, not values.
        return False
    if re.fullmatch(r"\.env(?:[._-].*|[*?\[].*)?", base):
        return True
    env_owner = re.fullmatch(r"([\w.-]+)\.env", base)
    if env_owner and env_owner.group(1).lower() not in _NOT_ENV_FILE_OWNERS:
        return True
    lowered = base.lower()
    if "credentials" in lowered and not lowered.endswith(_DOC_OR_CODE_SUFFIXES):
        return True
    if re.fullmatch(r"id_(?:rsa|ed25519|ecdsa|dsa)", base):
        return True
    if re.fullmatch(r"\.(?:bash|zsh)_history", base):
        return True
    return False


def _resolve(text: str, scope: dict[str, str]) -> str:
    if "$" not in text or not scope:
        return text

    def substitute(match: re.Match[str]) -> str:
        name = match.group(1) or match.group(2)
        return scope.get(name, match.group(0))

    return re.sub(r"\$(?:\{([A-Za-z_][A-Za-z0-9_]*)\}|([A-Za-z_][A-Za-z0-9_]*))", substitute, text)


@dataclass
class _Ctx:
    exe: str
    args: list[str]
    argv: list[str]
    cmd: _Cmd
    scope: dict[str, str]
    depth: int
    codes: list[tuple[str, str, bool]] = field(default_factory=list)


def _flag_cluster(token: str) -> str:
    return token[1:] if re.fullmatch(r"-[A-Za-z]+", token) else ""


def _positionals(args: list[str], value_flags: frozenset[str] = frozenset()) -> list[str]:
    result: list[str] = []
    skip = False
    for token in args:
        if skip:
            skip = False
            continue
        if token == "--":
            continue
        if token.startswith("-") and token != "-":
            if token in value_flags:
                skip = True
            continue
        result.append(token)
    return result


_SEARCH_VALUE_FLAGS = frozenset(
    {"-A", "-B", "-C", "-m", "-g", "-t", "-T", "--include", "--exclude", "--glob",
     "--max-count", "--type", "--context", "--after-context", "--before-context",
     "--exclude-dir", "-d", "-D", "-j", "--threads"}
)


def _program_flags_present(args: list[str]) -> bool:
    for index, token in enumerate(args):
        if token in ("-e", "-f", "--regexp", "--file", "--expression") or token.startswith(
            ("--regexp=", "--file=", "--expression=")
        ):
            return True
        cluster = _flag_cluster(token)
        if cluster and cluster[-1] in "ef":
            return True
    return False


def _without_exclusions(exe: str, args: list[str]) -> list[str]:
    """`--exclude .env*`, `diff -x '.env*'` name files to SKIP, not files to read."""

    kept: list[str] = []
    skip = False
    for token in args:
        if skip:
            skip = False
            continue
        if token in ("--exclude", "--exclude-dir", "--ignore", "--ignore-file") or (
            exe in ("diff", "sdiff") and token == "-x"
        ):
            skip = True
            continue
        if token.startswith(("--exclude=", "--exclude-dir=", "--ignore=")):
            continue
        kept.append(token)
    return kept


def _file_candidates(exe: str, args: list[str]) -> list[str]:
    """Arguments that are files for the command, not its search pattern or script."""

    args = _without_exclusions(exe, args)
    if exe in _PROGRAM_POSITIONAL:
        if _program_flags_present(args):
            # -e PATTERN / --regexp=PATTERN are patterns, not files.
            kept: list[str] = []
            skip = False
            for token in args:
                if skip:
                    skip = False
                    continue
                if token in ("-e", "--regexp", "--expression"):
                    skip = True
                    continue
                if token.startswith(("--regexp=", "--expression=")):
                    continue
                kept.append(token)
            return kept
        flags = _SEARCH_VALUE_FLAGS if exe in _SEARCHERS else frozenset()
        positional = _positionals(args, flags)
        candidates = [token for token in args if token.startswith("-")]
        if len(positional) >= 2:
            candidates.extend(positional[1:])
        return candidates
    return list(args)


_NAMES_ONLY_PATTERN = re.compile(r"[\^A-Za-z0-9_|()\[\]\-+*?\\ ]*=")


def _names_only(exe: str, args: list[str]) -> bool:
    """grep -o 'NAME=': prints the variable names and stops before the value."""

    if exe not in _SEARCHERS:
        return False
    only_matching = any(
        token == "--only-matching" or ("o" in _flag_cluster(token))
        for token in args
    )
    if not only_matching:
        return False
    positional = _positionals(args, _SEARCH_VALUE_FLAGS)
    pattern = positional[0] if positional else ""
    return bool(pattern) and bool(_NAMES_ONLY_PATTERN.fullmatch(pattern))


_REDACTING_SED = re.compile(r"^s([/#|,])[^\n]*?=\.\*\$?\1")


def _values_removed(exe: str, args: list[str]) -> bool:
    """sed/awk/cut forms that print only the variable names, never the values."""

    positional = _positionals(args, frozenset({"-F", "-d", "-f", "-e"}))
    if exe == "sed" and positional and not any(t.startswith("-i") for t in args):
        return bool(_REDACTING_SED.match(positional[0]))
    if exe in ("awk", "gawk", "mawk") and positional:
        has_separator = any(t in ("-F=", "-F", "--field-separator=") or t.startswith("-F=") for t in args)
        return has_separator and bool(re.fullmatch(r"\{\s*print\s+\$1\s*\}", positional[0]))
    if exe == "cut":
        return "-s" in args and "-d=" in args and "-f1" in args
    return False


def _count_only(exe: str, args: list[str]) -> bool:
    """grep/rg modes that print a number, a boolean exit code or file names only."""

    if exe not in _SEARCHERS:
        return False
    if _names_only(exe, args):
        return True
    for token in args:
        if token in ("--count", "--count-matches", "--quiet", "--silent",
                     "--files-with-matches", "--files-without-match", "--files"):
            return True
        cluster = _flag_cluster(token)
        if cluster and any(letter in cluster for letter in "cqlL"):
            return True
    return False


# -- peeling wrappers -----------------------------------------------------------

def _env_rest(argv: list[str]) -> list[str]:
    index = 1
    while index < len(argv):
        token = argv[index]
        if token == "--":
            index += 1
            break
        if token in ("-u", "-C", "-P"):
            index += 2
        elif token == "-S" and index + 1 < len(argv):
            try:
                return shlex.split(argv[index + 1]) + argv[index + 2:]
            except ValueError:
                return argv[index + 2:]
        elif token.startswith("-") and token != "-":
            index += 1
        elif _ASSIGNMENT.match(token):
            index += 1
        else:
            break
    return argv[index:]


def _peel(argv: list[str]) -> tuple[list[str], bool]:
    """Strip env/sudo/xargs-style prefixes. Returns (command, is_bare_env)."""

    for _ in range(_MAX_DEPTH):
        if not argv:
            return [], False
        exe = _base(argv[0])
        if exe == "env":
            rest = _env_rest(argv)
            if not rest:
                return ["env"], True
            argv = rest
            continue
        spec = _WRAPPERS.get(exe)
        if spec is None:
            return argv, False
        if exe == "command" and any(token in ("-v", "-V") for token in argv[1:3]):
            return [], False
        value_flags, skip_positionals = spec
        index = 1
        while index < len(argv) and argv[index].startswith("-") and argv[index] != "-":
            if argv[index] == "--":
                index += 1
                break
            index += 2 if argv[index] in value_flags else 1
        index += skip_positionals
        rest = argv[index:]
        if not rest:
            return [], False
        if exe == "eval" or (exe in ("xargs", "watch") and len(rest) == 1 and " " in rest[0]):
            return ["sh", "-c", " ".join(rest)], False
        argv = rest
    return argv, False


# -- container and ssh helpers -----------------------------------------------------

_SSH_VALUE_FLAGS = frozenset("-p -i -l -o -F -J -L -R -D -b -c -E -e -I -m -O -Q -S -W -w".split())
_CONTAINER_VALUE_FLAGS = frozenset(
    "-e --env -u --user -w --workdir --env-file --detach-keys -v --volume -p --publish --name "
    "--network --entrypoint -l --label --mount --platform --hostname -h --cap-add --device "
    "--memory -m --cpus --restart -f --file -H --host --context -c --config --log-level "
    "-p --project-name --profile --project-directory".split()
)


def _ssh_remote(args: list[str]) -> list[str] | None:
    index = 0
    while index < len(args):
        token = args[index]
        if token.startswith("-") and token != "-":
            index += 2 if token in _SSH_VALUE_FLAGS else 1
            continue
        return args[index + 1:]
    return None


def _container_command(exe: str, args: list[str]) -> list[str] | None:
    """The command a container exec/run will launch, or None if not an exec/run."""

    if exe == "kubectl" or exe == "oc":
        if "exec" not in args:
            return None
        rest = args[args.index("exec") + 1:]
        if "--" in rest:
            return rest[rest.index("--") + 1:]
        positional = _positionals(rest, _CONTAINER_VALUE_FLAGS)
        return positional[1:] if positional else []
    index = 0
    sub_seen = False
    while index < len(args):
        token = args[index]
        if token.startswith("-"):
            index += 2 if token in _CONTAINER_VALUE_FLAGS else 1
            continue
        if token in ("compose", "container", "service") and not sub_seen:
            index += 1
            continue
        if token in ("exec", "run"):
            sub_seen = True
            index += 1
            break
        return None
    if not sub_seen:
        return None
    rest = args[index:]
    skip = False
    positionals: list[str] = []
    cut = len(rest)
    for position, token in enumerate(rest):
        if skip:
            skip = False
            continue
        if token.startswith("-") and token != "-":
            if token in _CONTAINER_VALUE_FLAGS:
                skip = True
            continue
        positionals.append(token)
        if len(positionals) == 1:
            cut = position + 1
            break
    return rest[cut:] if positionals else []


# -- the rules -----------------------------------------------------------------------

_PIPE_FILTERS = frozenset(
    "grep egrep fgrep rg awk sed cut tr sort uniq head tail rev nl column fold".split()
)


def _output_is_swallowed(ctx: "_Ctx") -> bool:
    """True when the command's output only feeds a quiet or counting consumer.

    `ps -u deploy -o args= | grep -q worker` prints nothing; the arguments never
    reach the terminal. Anything that can print at the end of the pipe keeps the
    command blocked.
    """

    tail = ctx.cmd.tail
    if not tail or ctx.cmd.redirs and any(op.startswith(">") for op, _w in ctx.cmd.redirs):
        return False
    for follower in tail[:-1]:
        words = [w.text for w in follower.words]
        if not words or _base(words[0]) not in _PIPE_FILTERS:
            return False
    words = [word.text for word in tail[-1].words]
    if not words:
        return False
    exe, args = _base(words[0]), words[1:]
    if tail[-1].redirs and any(op.startswith(">") and not _w.text.startswith("/dev/null") for op, _w in tail[-1].redirs):
        return False
    if exe == "wc":
        return True
    return _count_only(exe, args)


def _rule_pm2(ctx: _Ctx) -> str | None:
    if ctx.exe == "pm2" and ctx.args and ctx.args[0] in ("jlist", "prettylist", "env", "show", "describe"):
        return "Use an approved PM2 status wrapper; raw PM2 environment output is blocked."
    return None


_PROC_ENV = re.compile(r"^/proc/(?:\d+|self|thread-self|\*|\$\{?[^/\s}]+\}?)/(?:environ|cmdline)$")


def _rule_proc_environ(ctx: _Ctx) -> str | None:
    if ctx.exe in _METADATA_TOOLS or _count_only(ctx.exe, ctx.args):
        return None
    targets = _file_candidates(ctx.exe, ctx.args)
    targets += [_resolve(word.text, ctx.scope) for op, word in ctx.cmd.redirs if op.startswith("<")]
    if any(_PROC_ENV.match(token) for token in targets):
        return "Direct process environment and command-line reads are blocked."
    return None


def _rule_env_dump(ctx: _Ctx) -> str | None:
    exe, args = ctx.exe, ctx.args
    if exe == "env":
        return "Whole-environment output is blocked; use env only to launch a scoped command."
    if exe == "printenv":
        names = [token for token in args if not token.startswith("-")]
        if not names or any(_secret_name(name) for name in names):
            return "Whole-environment output is blocked; request only a non-secret status field."
        return None
    if exe == "export":
        positional = [token for token in args if not token.startswith("-")]
        if "-p" in args or (not positional and not args):
            return "Whole-environment output is blocked; request only a non-secret status field."
        return None
    if exe in ("declare", "typeset"):
        positional = [token for token in args if not token.startswith("-")]
        flags = "".join(token[1:] for token in args if re.fullmatch(r"-[A-Za-z]+", token))
        if not positional and ("p" in flags or "x" in flags):
            return "Whole-environment output is blocked; request only a non-secret status field."
    return None


def _rule_shell_state(ctx: _Ctx) -> str | None:
    if ctx.exe in ("set", "declare", "typeset") and not ctx.args:
        return "Shell state output is blocked because it may contain exported credentials."
    return None


def _rule_systemctl(ctx: _Ctx) -> str | None:
    if ctx.exe != "systemctl":
        return None
    positional = _positionals(ctx.args, frozenset({"-p", "--property", "-H", "-M", "-t"}))
    sub = positional[0] if positional else ""
    if sub == "show-environment":
        return "System service environment output is blocked."
    if sub == "show":
        properties: list[str] = []
        for index, token in enumerate(ctx.args):
            if token.startswith("--property="):
                properties.append(token.split("=", 1)[1])
            elif token.startswith("-p") and len(token) > 2 and token != "--property":
                properties.append(token[2:].lstrip("="))
            elif token in ("-p", "--property") and index + 1 < len(ctx.args):
                properties.append(ctx.args[index + 1])
        if not properties:
            return "Raw system service inspection is blocked; request one approved non-secret property."
        if any(re.search(r"Environment", value, re.I) for value in properties):
            return "System service environment output is blocked."
    return None


_PS_SAFE_COLUMNS = re.compile(r"^(?:comm|ucomm|pid|ppid|user|uid|gid|pgid|sid|tty|etime|etimes|time|stat|state|pcpu|pmem|%cpu|%mem|rss|vsz|nlwp|nice|ni|pri|start|lstart|euser|ruser|group|fname|s|c|cputime|wchan|command_name)$", re.I)


def _rule_process_args(ctx: _Ctx) -> str | None:
    exe, args = ctx.exe, ctx.args
    reason = "Broad process argument output is blocked; request only PID, user, and executable fields."
    if _output_is_swallowed(ctx):
        return None
    if exe == "pgrep":
        for token in args:
            if token == "--list-full":
                return reason
            cluster = _flag_cluster(token)
            if cluster and "a" in cluster:
                return reason
        return None
    if exe != "ps":
        return None
    columns: list[str] = []
    has_output_spec = False
    flags_seen = ""
    bsd_words: list[str] = []
    index = 0
    while index < len(args):
        token = args[index]
        spec = None
        if token in ("-o", "-O", "--format", "o", "O"):
            spec = args[index + 1] if index + 1 < len(args) else ""
            index += 1
        elif token.startswith("--format="):
            spec = token.split("=", 1)[1]
        elif re.fullmatch(r"-?[A-Za-z]*[oO]", token) and token not in ("-o", "-O") and index + 1 < len(args):
            # clustered form such as -eo or axo with the column list next
            spec = args[index + 1]
            flags_seen += token.lstrip("-")[:-1]
            index += 1
        elif token.startswith(("-o", "-O")) and len(token) > 2:
            spec = token[2:]
        elif token.startswith("-") and re.fullmatch(r"-[A-Za-z]+", token):
            flags_seen += token[1:]
        elif token.startswith("-"):
            pass
        elif re.fullmatch(r"[A-Za-z]+", token):
            bsd_words.append(token)
        index += 1
        if spec is not None:
            has_output_spec = True
            for column in re.split(r"[,\s]+", spec):
                name = column.split("=", 1)[0].strip()
                if name:
                    columns.append(name)
    if has_output_spec:
        if any(not _PS_SAFE_COLUMNS.match(column) for column in columns):
            return reason
        return None
    # No explicit column list: only a pid or name selector is a narrow request.
    if set(flags_seen) & set("efFaAxwW") or any(not word.isdigit() for word in bsd_words):
        return reason
    return None


def _rule_shell_history(ctx: _Ctx) -> str | None:
    if ctx.exe == "history" or (ctx.exe == "fc" and any("l" in _flag_cluster(t) for t in ctx.args)):
        return "Shell history output is blocked because commands may contain credentials."
    return None


def _rule_launchctl(ctx: _Ctx) -> str | None:
    if ctx.exe == "launchctl" and ctx.args and ctx.args[0] in ("print", "export", "getenv"):
        return "Raw launch service output is blocked because it may include environment values."
    return None


def _rule_compose_config(ctx: _Ctx) -> str | None:
    if ctx.exe == "docker-compose":
        words = _positionals(ctx.args, _CONTAINER_VALUE_FLAGS)
    elif ctx.exe == "docker" and "compose" in ctx.args:
        words = _positionals(ctx.args[ctx.args.index("compose") + 1:], _CONTAINER_VALUE_FLAGS)
    else:
        return None
    if words and words[0] == "config":
        return "Rendered container configuration is blocked because interpolation may reveal credentials."
    return None


def _rule_k8s_secrets(ctx: _Ctx) -> str | None:
    if ctx.exe not in ("kubectl", "oc"):
        return None
    words = _positionals(ctx.args, _CONTAINER_VALUE_FLAGS)
    if len(words) >= 2 and words[0] in ("get", "describe", "edit") and re.match(r"^secrets?(?:$|[/,])", words[1]):
        return "Raw Kubernetes secret inspection is blocked."
    return None


def _rule_secret_stores(ctx: _Ctx) -> str | None:
    exe, args = ctx.exe, ctx.args
    reason = "Secret-store value retrieval must use an approved non-printing wrapper."
    if exe == "aws" and args[:2] == ["secretsmanager", "get-secret-value"]:
        return reason
    if exe == "gcloud" and args[:3] == ["secrets", "versions", "access"]:
        return reason
    if exe == "vault" and args[:2] == ["kv", "get"]:
        return reason
    pw_reason = "Password-store value retrieval must use an owner-only or non-printing wrapper."
    if exe == "security" and args and args[0] == "find-generic-password" and "-w" in args:
        return pw_reason
    if exe == "op" and len(args) >= 2 and args[0] == "read" and args[1].startswith("op://"):
        return pw_reason
    if exe == "pass" and args and args[0] == "show":
        return pw_reason
    return None


def _rule_provider_env_export(ctx: _Ctx) -> str | None:
    exe, args = ctx.exe, ctx.args
    if (
        (exe == "vercel" and args[:2] == ["env", "pull"])
        or (exe == "heroku" and args[:1] == ["config"])
        or (exe == "doppler" and args[:1] == ["secrets"])
    ):
        return "Provider environment export is blocked; use scoped owner entry or a non-printing wrapper."
    return None


_SECRET_FILE_REASON = (
    "Direct output from a credential-bearing file is blocked; use an approved wrapper. "
    "Metadata (ls, stat, wc), counts (grep -c, grep -q) and names only (grep -o '^NAME=') are allowed."
)


def _rule_secret_file_reader(ctx: _Ctx) -> str | None:
    exe, args = ctx.exe, ctx.args
    if exe in _PRINT_READERS and (_output_is_swallowed(ctx) or _values_removed(exe, args)):
        return None
    stdin_secret = any(
        op == "<" and _is_secret_path(_resolve(word.text, ctx.scope)) for op, word in ctx.cmd.redirs
    )
    if exe in _PRINT_READERS:
        if _count_only(exe, args):
            return None
        if stdin_secret or any(_is_secret_path(token) for token in _file_candidates(exe, args)):
            return _SECRET_FILE_REASON
        return None
    if _INTERPRETER_NAME.match(exe):
        if stdin_secret:
            return _SECRET_FILE_REASON
        has_inline = bool(_inline_code(exe, args))
        positional = _positionals(args, frozenset({"-m", "-W", "-X", "-I"}))
        if re.match(r"^(?:perl|ruby)$", exe) and any(
            re.fullmatch(r"-[A-Za-z]*[np][A-Za-z]*", t) for t in args
        ) and any(_is_secret_path(t) for t in args):
            return _SECRET_FILE_REASON
        if not has_inline and positional:
            if _is_secret_path(positional[0]):
                return _SECRET_FILE_REASON
            if "-m" in args and any(_is_secret_path(t) for t in args):
                return _SECRET_FILE_REASON
        return None
    if exe in _TRANSFER_TOOLS or exe in ("ssh", "docker", "kubectl", "bash", "sh", "zsh"):
        if stdin_secret:
            return _SECRET_FILE_REASON
    return None


_UPLOAD_PATH_FLAGS = frozenset({"-T", "--upload-file", "--post-file", "--body-file", "-K", "--config"})
_UPLOAD_DATA_FLAGS = frozenset(
    {"-d", "--data", "--data-binary", "--data-raw", "--data-urlencode", "-F", "--form", "--json"}
)


def _rule_secret_file_transfer(ctx: _Ctx) -> str | None:
    if ctx.exe not in _TRANSFER_TOOLS:
        return None
    args = ctx.args
    for index, token in enumerate(args):
        candidates = [token]
        if token in (_UPLOAD_PATH_FLAGS | _UPLOAD_DATA_FLAGS) and index + 1 < len(args):
            candidates.append(args[index + 1])
        for value in candidates:
            path = ""
            if value.startswith("@"):
                path = value[1:]
            elif "=@" in value:
                path = value.split("=@", 1)[1]
            elif token in _UPLOAD_PATH_FLAGS and value is not token:
                path = value
            elif token.startswith(("--post-file=", "--upload-file=", "--body-file=")):
                path = token.split("=", 1)[1]
            if path and _is_secret_path(path.split(";", 1)[0]):
                return _SECRET_FILE_REASON
    return None


def _rule_echo_secret_variable(ctx: _Ctx) -> str | None:
    if ctx.exe in ("echo", "printf", "print"):
        names = [name for word in ctx.cmd.words for name in word.expands]
        if any(_secret_name(name) for name in names):
            return "Printing a credential-shaped environment variable is blocked."
    if ctx.exe in _PRINT_READERS and ctx.cmd.herestrings:
        names = [name for word in ctx.cmd.herestrings for name in word.expands]
        if any(_secret_name(name) for name in names):
            return "Printing a credential-shaped environment variable is blocked."
    return None


def _rule_shell_trace(ctx: _Ctx) -> str | None:
    reason = "Shell tracing is blocked for agent commands because expanded secrets may be logged."
    if ctx.exe == "set":
        if "-x" in ctx.args:
            return reason
        for index, token in enumerate(ctx.args[:-1]):
            if token == "-o" and ctx.args[index + 1] == "xtrace":
                return reason
    if ctx.exe in ("bash", "sh", "zsh") and "-x" in ctx.args:
        return reason
    return None


def _rule_curl_verbose(ctx: _Ctx) -> str | None:
    if ctx.exe != "curl":
        return None
    verbose = any(
        token == "--verbose" or (re.fullmatch(r"-[A-Za-z]+", token) and "v" in token[1:])
        for token in ctx.args
    )
    if verbose and re.search(r"authorization|bearer|api[_-]?key|token|secret", " ".join(ctx.argv), re.I):
        return "Verbose authenticated HTTP output is blocked because request headers may be exposed."
    return None


def _rule_container_inspect(ctx: _Ctx) -> str | None:
    if ctx.exe != "docker":
        return None
    if not _safe_inspect_formats(shlex.join(["docker", *ctx.args])):
        return "Container inspection requires a literal approved non-secret status field; use a reviewed wrapper for other output."
    return None


# -- language code ---------------------------------------------------------------------

def _language_of(exe: str) -> str:
    if exe.startswith("python"):
        return "python"
    if exe.startswith("php"):
        return "php"
    if exe == "ruby":
        return "ruby"
    if exe == "perl":
        return "perl"
    return "js"


def _inline_code(exe: str, args: list[str]) -> list[tuple[str, str, bool]]:
    """Code passed on the command line: (code, language, prints_result)."""

    if not _INTERPRETER_NAME.match(exe):
        return []
    lang = _language_of(exe)
    found: list[tuple[str, str, bool]] = []
    for index, token in enumerate(args):
        following = args[index + 1] if index + 1 < len(args) else None
        if token.startswith("--eval=") or token.startswith("--print="):
            found.append((token.split("=", 1)[1], lang, token.startswith("--print=")))
            continue
        if following is None:
            continue
        cluster = _flag_cluster(token)
        if lang == "python" and cluster.endswith("c"):
            found.append((following, lang, False))
        elif lang == "js" and (token in ("-e", "--eval", "-p", "--print", "-pe", "-ep")):
            found.append((following, lang, token in ("-p", "--print", "-pe", "-ep")))
        elif lang == "php" and token == "-r":
            found.append((following, lang, False))
        elif lang in ("ruby", "perl") and cluster and cluster[-1] in "eE":
            found.append((following, lang, False))
    return found


_SINK = re.compile(
    r"(?<![\w.$>])(?P<name>console\.(?:log|info|warn|error|debug|dir|table)|"
    r"process\.std(?:out|err)\.write|sys\.std(?:out|err)\.write|logging\.\w+|pprint|"
    r"print_r|var_dump|var_export|error_log|printf|print|echo|puts|say|pp|p)\b"
)
_RUBY_ONLY_SINKS = frozenset({"p", "pp"})


def _balanced(code: str, open_index: int) -> int:
    depth = 0
    quote = ""
    index = open_index
    while index < len(code):
        ch = code[index]
        if quote:
            if ch == "\\":
                index += 2
                continue
            if ch == quote:
                quote = ""
        elif ch in "'\"`":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return len(code)


def _sink_arguments(code: str, lang: str) -> list[str]:
    return [argument for _offset, argument in _sink_calls(code, lang)]


def _sink_calls(code: str, lang: str) -> list[tuple[int, str]]:
    arguments: list[tuple[int, str]] = []
    for match in _SINK.finditer(code):
        if match.group("name") in _RUBY_ONLY_SINKS and lang != "ruby":
            continue
        position = match.end()
        while position < len(code) and code[position] in " \t":
            position += 1
        if position < len(code) and code[position] == "(":
            end = _balanced(code, position)
            arguments.append((match.start(), code[position + 1:end]))
        else:
            end = position
            while end < len(code) and code[end] not in ";\n":
                end += 1
            arguments.append((match.start(), code[position:end]))
    return arguments


_ENV_WHOLE: dict[str, tuple[re.Pattern[str], ...]] = {
    "python": (re.compile(r"os\.environb?(?!\s*\[)(?!\s*\.\s*(?:get|setdefault|pop|__getitem__|__contains__)\b)"),),
    "js": (
        re.compile(r"process\.env(?!\s*\??\.\s*[A-Za-z_$])(?!\s*\??\.?\s*\[)"),
        re.compile(r"import\.meta\.env(?!\s*\.\s*[A-Za-z_$])(?!\s*\[)"),
        re.compile(r"Deno\.env\.toObject\s*\("),
    ),
    "php": (
        re.compile(r"\$_(?:ENV|SERVER)(?!\s*\[)"),
        re.compile(r"\bgetenv\s*\(\s*\)"),
    ),
    "ruby": (re.compile(r"\bENV\b(?!\s*\[)(?!\s*\.\s*(?:fetch|key\?|dig|include\?|has_key\?)\b)"),),
    "perl": (re.compile(r"%ENV\b"),),
}
_ENV_KEYED: dict[str, tuple[re.Pattern[str], ...]] = {
    "python": (
        re.compile(r"os\.environ\s*\[\s*['\"](\w+)['\"]"),
        re.compile(r"os\.environ\s*\.\s*(?:get|pop|setdefault)\s*\(\s*['\"](\w+)"),
        re.compile(r"os\.getenv\s*\(\s*['\"](\w+)"),
    ),
    "js": (
        re.compile(r"process\.env\s*\??\.\s*([A-Za-z_]\w*)"),
        re.compile(r"process\.env\s*\[\s*['\"`](\w+)"),
        re.compile(r"import\.meta\.env\.(\w+)"),
    ),
    "php": (
        re.compile(r"\$_(?:ENV|SERVER)\s*\[\s*['\"](\w+)"),
        re.compile(r"\bgetenv\s*\(\s*['\"](\w+)"),
    ),
    "ruby": (
        re.compile(r"\bENV\s*\[\s*['\"](\w+)"),
        re.compile(r"\bENV\.fetch\s*\(\s*['\"](\w+)"),
    ),
    "perl": (re.compile(r"\$ENV\{\s*['\"]?(\w+)"),),
}
_ENV_ENUMERATION: dict[str, re.Pattern[str]] = {
    "python": re.compile(
        r"os\.environ\s*\.\s*(?:items|keys|values|copy)\s*\(|dict\s*\(\s*os\.environ|"
        r"\bfor\s+[\w\s,()]+\s+in\s+os\.environ"
    ),
    "js": re.compile(
        r"Object\.(?:entries|keys|values|assign)\s*\([^)]*process\.env|\.\.\.\s*process\.env|"
        r"\bfor\s*\(?[\w\s,()]+\s+(?:in|of)\s+(?:process\.env|Object\.\w+\(process\.env)"
    ),
    "ruby": re.compile(r"ENV\s*\.\s*(?:each|to_h|to_a|keys|values|map|select|inspect|to_s)"),
    "perl": re.compile(r"(?:keys|values|each)\s*\(?\s*%ENV"),
}
_ENV_DUMP_REASON = "Programming-language environment dumps are blocked."


def _env_dump_in_text(text: str, lang: str) -> bool:
    if any(pattern.search(text) for pattern in _ENV_WHOLE.get(lang, ())):
        return True
    return any(
        _secret_name(match.group(1))
        for pattern in _ENV_KEYED.get(lang, ())
        for match in pattern.finditer(text)
    )


def _without_embedded_text(code: str) -> str:
    """Blank triple-quoted and very long literals: they hold documents, not code."""

    out: list[str] = []
    last = 0
    for start, end, _prefix, quote, body in _scan_literals(code):
        if len(quote) == 3 or len(body) >= 120:
            out.append(code[last:start])
            out.append(" ")
            last = end
    out.append(code[last:])
    return "".join(out)


def _rule_language_env_dump(ctx: _Ctx) -> str | None:
    for raw_code, lang, prints_result in ctx.codes:
        code = _without_embedded_text(raw_code)
        if prints_result and _env_dump_in_text(code, lang):
            return _ENV_DUMP_REASON
        sinks = _sink_arguments(code, lang)
        if any(_env_dump_in_text(argument, lang) for argument in sinks):
            return _ENV_DUMP_REASON
        enumeration = _ENV_ENUMERATION.get(lang)
        if sinks and enumeration is not None and enumeration.search(code):
            return _ENV_DUMP_REASON
    return None


_SHELL_OUT = re.compile(
    r"\bsubprocess\b|\bos\.(?:system|popen|exec\w*)\b|child_process|\bexecSync\b|\bspawn(?:Sync)?\b|"
    r"\bshell_exec\b|\bpassthru\b|\bproc_open\b|\bpopen\b|\bsystem\s*\(|\bOpen3\b|%x\{|`[^`]*`"
)
_SHELL_READER_NAMES = frozenset(
    "cat head tail less more sed awk grep rg strings xxd base64 cut od jq tac nl".split()
)
_SHELL_READER_LITERAL = re.compile(
    r"""(?:subprocess\.\w+|check_output|Popen|os\.system|os\.popen|execSync|spawnSync|spawn|exec|"""
    r"""shell_exec|passthru|system)\s*\(\s*\[?\s*[rbf]?['"`](?:cat|head|tail|less|more|sed|awk|grep|rg|"""
    r"""strings|xxd|base64|cut|od|jq|echo|printf|tee|nl|tac)\b|"""
    r"""`\s*(?:cat|head|tail|less|more|sed|awk|grep|rg|strings|xxd|base64|cut|od|jq|tac)\b"""
)
_PREFIX_CHARS = frozenset("fFrRbBuU")


def _scan_literals(code: str) -> list[tuple[int, int, str, str, str]]:
    """Quoted literals as (start, end, prefix, quote, body), found in one linear pass.

    Single and double quoted literals end at the line end if unterminated, so an
    apostrophe inside prose cannot swallow the rest of the code.
    """

    found: list[tuple[int, int, str, str, str]] = []
    n = len(code)
    index = 0
    while index < n:
        ch = code[index]
        if ch not in "'\"`":
            index += 1
            continue
        start = index
        while start > 0 and code[start - 1] in _PREFIX_CHARS and index - start < 2:
            start -= 1
        prefix = code[start:index]
        if code.startswith(ch * 3, index) and ch != "`":
            end = code.find(ch * 3, index + 3)
            end = n if end < 0 else end + 3
            found.append((start, end, prefix, ch * 3, code[index + 3:max(index + 3, end - 3)]))
            index = end
            continue
        cursor = index + 1
        while cursor < n:
            if code[cursor] == "\\":
                cursor += 2
                continue
            if code[cursor] == ch:
                break
            if code[cursor] == "\n" and ch != "`":
                break
            cursor += 1
        body = code[index + 1:min(cursor, n)]
        end = min(cursor + 1, n) if cursor < n and code[cursor] == ch else min(cursor, n)
        found.append((start, end, prefix, ch, body))
        index = max(end, index + 1)
    return found


def _replace_literals(code: str, replacement) -> str:
    out: list[str] = []
    last = 0
    for start, end, prefix, quote, body in _scan_literals(code):
        out.append(code[last:start])
        out.append(replacement(prefix, quote, body))
        last = end
    out.append(code[last:])
    return "".join(out)


_SAFE_FUNCTION = re.compile(
    r"\b(?:len|sum|bool|int|float|round|any|all|count|strlen|mb_strlen|sizeof|file_exists|is_file|"
    r"is_readable|exists|isfile|isdir|getsize|stat|lstat|abs|number_format|sha1|sha256|sha512|md5|crc32)\s*\("
)
_SAFE_METHOD = re.compile(r"\.(?:count|startswith|endswith|exists|is_file|is_dir|isdigit)\s*\(")
_SAFE_PROPERTY = re.compile(r"\.(?:length|size|st_size|st_mode|st_mtime)\b(?!\s*\()")
def _strip_call(text: str, start: int, open_index: int) -> str:
    end = _balanced(text, open_index)
    return text[:start] + " " + text[end + 1:]


def _receiver_start(text: str, dot_index: int) -> int:
    index = dot_index
    while index > 0:
        ch = text[index - 1]
        if ch in ")]":
            opener = "(" if ch == ")" else "["
            depth = 0
            while index > 0:
                index -= 1
                if text[index] == ch:
                    depth += 1
                elif text[index] == opener:
                    depth -= 1
                    if depth == 0:
                        break
            continue
        if ch.isalnum() or ch in "_.$":
            index -= 1
            continue
        break
    return index


_SECRET_MARK = " __SECRETPATH__ "


def _strip_derived(expression: str) -> tuple[str, list[str]]:
    """Drop counting calls and string literals.

    Returns (remainder, f-string expressions). A literal that names a secret file
    is replaced by a marker so the caller still knows the expression mentions it.
    """

    text = expression
    for _ in range(40):
        match = _SAFE_METHOD.search(text)
        if match:
            open_index = match.end() - 1
            start = _receiver_start(text, match.start())
            text = _strip_call(text, start, open_index)
            continue
        match = _SAFE_FUNCTION.search(text)
        if match:
            text = _strip_call(text, match.start(), match.end() - 1)
            continue
        match = _SAFE_PROPERTY.search(text)
        if match:
            start = _receiver_start(text, match.start())
            text = text[:start] + " " + text[match.end():]
            continue
        break
    placeholders: list[str] = []

    def keep_placeholders(prefix: str, quote: str, body: str) -> str:
        marker = _SECRET_MARK if _literal_names_secret_file(body) else " "
        if quote == "'" and "f" not in prefix.lower():
            return marker
        placeholders.extend(m.group(1) for m in re.finditer(r"\$?\{([^{}]*)\}", body))
        placeholders.extend(m.group(1) for m in re.finditer(r"\$([A-Za-z_]\w*)", body))
        return marker

    return _replace_literals(text, keep_placeholders), placeholders


def _literal_names_secret_file(literal: str) -> bool:
    if re.search(r"\s", literal):
        # A backtick command such as `cat .env` is a command line, not prose.
        words = literal.split()
        if words and words[0] in _SHELL_READER_NAMES:
            return any(_is_secret_path(word) for word in words[1:])
        return False
    # "agent-access" alone is how a path built piece by piece names the lane directory.
    return _is_secret_path(literal) or literal == "agent-access"


_BOOLEAN_RHS = re.compile(
    r"^(?:(?!\bif\b|\belse\b|\bfor\b|\?|\bor\b|\band\b|[\[{]|\blambda\b).)*?"
    r"(?:\bnot\s+in\b|\bin\b|===|!==|==|!=)"
    r"(?:(?!\bif\b|\belse\b|\bfor\b|\?|\bor\b|\band\b|[\[{]|\blambda\b).)*$"
)
_READ_TOKEN = re.compile(
    r"\bopen\s*\(|\.read|readFile|file_get_contents|\bfopen\b|\bload\s*\(|dotenv|\bFile\.|\bIO\.|\bcat\b"
)
_EXTERNAL_RESULT = re.compile(
    r"subprocess\.|os\.popen|\brequests\.|urllib|urlopen|\bfetch\s*\(|\bhttp\.|curl_exec|"
    r"\.execute\s*\(|\.query\s*\(|pymysql|psycopg|mysql|\bconnect\s*\(|execSync|spawnSync|shell_exec"
)
_ASSIGN_STATEMENT = re.compile(
    r"^\s*(?:(?:const|let|var)\s+)?\(?\s*(\$?[A-Za-z_]\w*(?:\s*,\s*\$?[A-Za-z_]\w*)*)\s*\)?\s*"
    r"(?:[+\-*/]|\|\|)?=(?!=)\s*(.+?);?\s*$"
)
_WITH_AS = re.compile(r"\bwith\s+(.+?)\s+as\s+(\w+)")
_FOR_IN = re.compile(
    r"\bfor\s+\(?\s*(?:(?:const|let|var)\s+)?([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*)\s*\)?\s+(?:in|of)\s+"
    r"([^\n:\]\)}]+?)(?=\s*(?:\)|:|\]|}|\n|$|\bif\b))"
)
_FOREACH = re.compile(r"foreach\s*\(\s*(.+?)\s+as\s+(\$?\w+)(?:\s*=>\s*(\$?\w+))?\s*\)")


class _SecretFlow:
    """Follows file content from a secret file to a print call, by name, in order.

    A name is tainted when it holds what a read of a secret file returned. The
    result of an external call (subprocess, HTTP, database) is not file content,
    even when the secret was passed into it, and assigning a clean value clears
    the taint. The model is deliberately linear and approximate.
    """

    def __init__(self, argv_secret: bool) -> None:
        self.argv_secret = argv_secret
        self.path_names: set[str] = set()
        self.tainted: set[str] = set()

    def _mentions_secret(self, text: str) -> bool:
        if "__SECRETPATH__" in text:
            return True
        if self.argv_secret and re.search(r"\bargv\b|\bARGV\b", text):
            return True
        return any(ident in self.path_names for ident in re.findall(r"[A-Za-z_$][\w$]*", text))

    def _references_taint(self, text: str) -> bool:
        return any(ident.lstrip("$") in self.tainted for ident in re.findall(r"[A-Za-z_$][\w$]*", text))

    def expression_tainted(self, expression: str) -> bool:
        if _EXTERNAL_RESULT.search(expression):
            return False
        remainder, placeholders = _strip_derived(expression)
        if any(self.expression_tainted(item) for item in placeholders):
            return True
        if "," not in remainder and _BOOLEAN_RHS.match(remainder.strip()):
            return False
        if self._mentions_secret(remainder) and _READ_TOKEN.search(remainder):
            return True
        return self._references_taint(remainder)

    def _is_path_expression(self, expression: str) -> bool:
        if _EXTERNAL_RESULT.search(expression):
            return False
        remainder, placeholders = _strip_derived(expression)
        text = remainder + " " + " ".join(placeholders)
        return self._mentions_secret(text) and not _READ_TOKEN.search(text) and not self._references_taint(text)

    def assign(self, targets: list[str], expression: str) -> None:
        tainted = self.expression_tainted(expression)
        is_path = (not tainted) and self._is_path_expression(expression)
        names_half = bool(_NAME_INDEX_ZERO.search(expression))
        unpacked_pair = len(targets) >= 2 and bool(_NAME_HALF.search(expression))
        for position, target in enumerate(targets):
            # `key, value = line.split('=', 1)`: the key is a variable NAME.
            clean = names_half or (unpacked_pair and position == 0)
            hold = tainted and not clean
            (self.tainted.add if hold else self.tainted.discard)(target)
            (self.path_names.add if is_path else self.path_names.discard)(target)


def _split_top_level(text: str) -> list[str]:
    """Split call arguments on commas that are not inside brackets or quotes."""

    pieces: list[str] = []
    depth = 0
    quote = ""
    current: list[str] = []
    index = 0
    while index < len(text):
        ch = text[index]
        if quote:
            current.append(ch)
            if ch == "\\" and index + 1 < len(text):
                current.append(text[index + 1])
                index += 1
            elif ch == quote:
                quote = ""
        elif ch in "'\"`":
            quote = ch
            current.append(ch)
        elif ch in "([{":
            depth += 1
            current.append(ch)
        elif ch in ")]}":
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0:
            pieces.append("".join(current))
            current = []
        else:
            current.append(ch)
        index += 1
    pieces.append("".join(current))
    return [piece for piece in pieces if piece.strip()]


_NAME_HALF = re.compile(r"\.(?:split|rsplit|partition)\(\s*['\"]=['\"]")
_NAME_INDEX_ZERO = re.compile(r"\.(?:split|rsplit|partition)\(\s*['\"]=['\"][^)]*\)\s*\[\s*0\s*\]")


def _split_statements(code: str) -> list[tuple[int, str]]:
    """Statements split on ; and newlines outside quotes and brackets: (offset, text)."""

    inside = bytearray(len(code))
    for start, end, _prefix, _quote, _body in _scan_literals(code):
        for position in range(start, min(end, len(code))):
            inside[position] = 1
    statements: list[tuple[int, str]] = []
    depth = 0
    start = 0
    for index, ch in enumerate(code):
        if inside[index]:
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        elif ch in ";\n" and depth == 0:
            statements.append((start, code[start:index]))
            start = index + 1
    statements.append((start, code[start:]))
    return [(offset, text) for offset, text in statements if text.strip()]


def _secret_print_in_code(code: str, lang: str, argv_secret: bool) -> bool:
    """True if the code prints what it read from a secret file."""

    statements = _split_statements(code)
    starts = [offset for offset, _text in statements]

    def statement_of(offset: int) -> int:
        return max(0, bisect.bisect_right(starts, offset) - 1)

    events: list[tuple[int, int, int, str, object, str]] = []
    for position, (offset, text) in enumerate(statements):
        match = _ASSIGN_STATEMENT.match(text.strip())
        if match:
            targets = [t.strip().lstrip("$") for t in match.group(1).split(",")]
            events.append((position, 1, offset, "assign", targets, match.group(2)))
    for match in _WITH_AS.finditer(code):
        events.append((statement_of(match.start()), 0, match.start(), "assign", [match.group(2)], match.group(1)))
    for match in _FOR_IN.finditer(code):
        targets = [t.strip() for t in match.group(1).split(",")]
        events.append((statement_of(match.start()), 0, match.start(), "assign", targets, match.group(2)))
    for match in _FOREACH.finditer(code):
        targets = [t.lstrip("$") for t in match.groups()[1:] if t]
        events.append((statement_of(match.start()), 0, match.start(), "assign", targets, match.group(1)))
    for sink_offset, argument in _sink_calls(code, lang):
        for piece in _split_top_level(argument):
            events.append((statement_of(sink_offset), 2, sink_offset, "sink", [], piece))
    flow = _SecretFlow(argv_secret)
    for _position, _priority, _offset, kind, targets, expression in sorted(events, key=lambda e: e[:3]):
        if kind == "assign":
            flow.assign(targets, expression)  # type: ignore[arg-type]
        elif flow.expression_tainted(expression):
            return True
    return False


def _code_names_secret_file(code: str, argv_secret: bool) -> bool:
    if argv_secret and re.search(r"sys\.argv|process\.argv|\$argv|ARGV|\$_SERVER\s*\[\s*['\"]argv", code):
        return True
    return any(_literal_names_secret_file(body) for _s, _e, _p, _q, body in _scan_literals(code))


def _rule_language_secret_file_print(ctx: _Ctx) -> str | None:
    argv_secret = any(_is_secret_path(token) for token in ctx.args)
    for code, lang, _prints in ctx.codes:
        if not _code_names_secret_file(code, argv_secret):
            continue
        if _SHELL_OUT.search(code) and _SHELL_READER_LITERAL.search(code):
            return _SECRET_FILE_REASON
        if _secret_print_in_code(code, lang, argv_secret):
            return _SECRET_FILE_REASON
    return None


_RULES: tuple[tuple[str, Any], ...] = (
    ("pm2", _rule_pm2),
    ("proc-environ", _rule_proc_environ),
    ("env-dump", _rule_env_dump),
    ("shell-state", _rule_shell_state),
    ("systemctl", _rule_systemctl),
    ("process-args", _rule_process_args),
    ("shell-history", _rule_shell_history),
    ("launchctl", _rule_launchctl),
    ("compose-config", _rule_compose_config),
    ("k8s-secrets", _rule_k8s_secrets),
    ("secret-stores", _rule_secret_stores),
    ("provider-env-export", _rule_provider_env_export),
    ("secret-file-reader", _rule_secret_file_reader),
    ("secret-file-transfer", _rule_secret_file_transfer),
    ("echo-secret-variable", _rule_echo_secret_variable),
    ("shell-trace", _rule_shell_trace),
    ("curl-verbose", _rule_curl_verbose),
    ("container-inspect", _rule_container_inspect),
    ("language-env-dump", _rule_language_env_dump),
    ("language-secret-file-print", _rule_language_secret_file_print),
)


# -- evaluation -------------------------------------------------------------------------

def _run_rules(ctx: _Ctx) -> Decision | None:
    for _rule_id, rule in _RULES:
        reason = rule(ctx)
        if reason:
            return Decision(False, reason)
    return None


def _check_script_text(text: str, scope: dict[str, str], depth: int) -> Decision | None:
    if depth > _MAX_DEPTH:
        return Decision(False, "Command nesting is too deep to inspect; use a reviewed wrapper.")
    try:
        commands = _Parser(text)._list(nested=False)
    except _ParseFail:
        legacy = _legacy_evaluate_command(text)
        return None if legacy.allowed else legacy
    return _check_cmds(commands, scope, depth)


def _check_cmds(commands: list[_Cmd], scope: dict[str, str], depth: int) -> Decision | None:
    for position, cmd in enumerate(commands):
        cmd.tail = []
        following = position
        while commands[following].piped and following + 1 < len(commands):
            following += 1
            cmd.tail.append(commands[following])
        for nested in cmd.subs:
            result = _check_cmds(nested, scope, depth)
            if result is not None:
                return result
        result = _check_cmd(cmd, scope, depth)
        if result is not None:
            return result
    return None


def _check_cmd(cmd: _Cmd, scope: dict[str, str], depth: int) -> Decision | None:
    if depth > _MAX_DEPTH:
        return Decision(False, "Command nesting is too deep to inspect; use a reviewed wrapper.")
    words = list(cmd.words)
    if (
        len(words) >= 4
        and words[0].text in ("for", "select")
        and words[2].text == "in"
        and _NAME_AT_START.fullmatch(words[1].text)
    ):
        # `for f in a b; do cat "$f"` : remember the value a later `$f` may hold,
        # preferring a secret path so the reader inside the loop is judged on it.
        values = [_resolve(word.text, scope) for word in words[3:]]
        scope[words[1].text] = next((v for v in values if _is_secret_path(v)), values[0])
    while words and not words[0].quoted and words[0].text in _KEYWORDS:
        words.pop(0)
    index = 0
    while index < len(words) and not words[index].quoted and _ASSIGNMENT.match(words[index].text):
        index += 1
    if index == len(words):
        for word in words:
            name, _, value = word.text.partition("=")
            scope[name.rstrip("+")] = _resolve(value, scope)
        return _check_stdin_bodies(None, cmd, scope, depth)
    argv = [_resolve(word.text, scope) for word in words[index:]]
    return _check_argv(argv, cmd, scope, depth)


def _check_argv(argv: list[str], cmd: _Cmd, scope: dict[str, str], depth: int) -> Decision | None:
    if depth > _MAX_DEPTH:
        return Decision(False, "Command nesting is too deep to inspect; use a reviewed wrapper.")
    effective, bare_env = _peel(argv)
    if not effective:
        # e.g. `xargs -0 < file`: no inner command, so judge the wrapper itself.
        effective = argv
    exe = _base(effective[0])
    if ("$" in effective[0] or "`" in effective[0]) and any(_is_secret_path(t) for t in effective[1:]):
        # A computed command name (`$(echo cat) .env`) cannot be judged: refuse.
        return Decision(False, _SECRET_FILE_REASON)
    ctx = _Ctx(exe=exe, args=effective[1:], argv=effective, cmd=cmd, scope=scope, depth=depth)
    ctx.codes = _inline_code(exe, ctx.args)
    result = _recurse(ctx)
    if result is not None:
        return result
    result = _run_rules(ctx)
    if result is not None:
        return result
    return _check_stdin_bodies(ctx, cmd, scope, depth)


def _shell_script_argument(args: list[str]) -> str | None:
    for index, token in enumerate(args):
        cluster = _flag_cluster(token)
        if cluster and "c" in cluster and index + 1 < len(args):
            return args[index + 1]
        if not token.startswith("-"):
            return None
    return None


def _recurse(ctx: _Ctx) -> Decision | None:
    exe, args, depth = ctx.exe, ctx.args, ctx.depth + 1
    if exe in _SHELLS:
        script = _shell_script_argument(args)
        if script is not None:
            return _check_script_text(script, dict(ctx.scope), depth)
        return None
    if exe == "ssh":
        remote = _ssh_remote(args)
        if remote:
            return _check_script_text(" ".join(remote), dict(ctx.scope), depth)
        return None
    if exe in ("docker", "podman", "nerdctl", "kubectl", "oc", "docker-compose"):
        inner = _container_command(exe if exe != "docker-compose" else "docker", args)
        if inner:
            return _check_argv(inner, ctx.cmd, ctx.scope, depth)
        return None
    if exe == "find":
        for keyword in ("-exec", "-execdir", "-ok", "-okdir"):
            if keyword in args:
                start = args.index(keyword) + 1
                end = start
                while end < len(args) and args[end] not in (";", "+", "\\;"):
                    end += 1
                inner = args[start:end]
                others = args[:start - 1] + args[end + 1:]
                if inner:
                    inner_exe = _base(inner[0])
                    if inner_exe in _PRINT_READERS and any(_is_secret_path(token) for token in others):
                        return Decision(False, _SECRET_FILE_REASON)
                    result = _check_argv(inner, ctx.cmd, ctx.scope, depth)
                    if result is not None:
                        return result
    return None


def _consumer_kind(argv: list[str], depth: int = 0) -> tuple[str, str]:
    """What reads a heredoc: ('shell'|'code'|'data', language)."""

    effective, bare_env = _peel(argv)
    if not effective or depth > 3:
        return "data", ""
    exe = _base(effective[0])
    args = effective[1:]
    if exe in _SHELLS:
        return ("data", "") if _shell_script_argument(args) is not None else ("shell", "")
    if _INTERPRETER_NAME.match(exe):
        if _inline_code(exe, args):
            return "data", ""
        positional = _positionals(args, frozenset({"-m", "-W", "-X", "-I"}))
        if not positional or positional[0] == "-":
            return "code", _language_of(exe)
        return "data", ""
    if exe == "ssh":
        remote = _ssh_remote(args)
        if remote is None or not remote:
            return "shell", ""
        try:
            parsed = _Parser(" ".join(remote))._list(nested=False)
        except _ParseFail:
            return "data", ""
        for cmd in reversed(parsed):
            tokens = [word.text for word in cmd.words]
            while tokens and _ASSIGNMENT.match(tokens[0]):
                tokens.pop(0)
            if tokens:
                return _consumer_kind(tokens, depth + 1)
        return "data", ""
    if exe in ("docker", "podman", "nerdctl", "kubectl", "oc"):
        inner = _container_command(exe, args)
        if inner:
            return _consumer_kind(inner, depth + 1)
    return "data", ""


def _check_stdin_bodies(ctx: _Ctx | None, cmd: _Cmd, scope: dict[str, str], depth: int) -> Decision | None:
    bodies = [(heredoc.body, heredoc.expand) for heredoc in cmd.heredocs]
    bodies += [(word.text, True) for word in cmd.herestrings]
    if not bodies:
        return None
    kind, lang = ("data", "")
    if ctx is not None:
        kind, lang = _consumer_kind(ctx.argv)
    for body, expands in bodies:
        if kind == "shell":
            result = _check_script_text(body, dict(scope), depth + 1)
            if result is not None:
                return result
            continue
        if expands:
            for nested in _embedded_substitutions(body):
                result = _check_cmds(nested, dict(scope), depth + 1)
                if result is not None:
                    return result
        if kind == "code":
            code_ctx = _Ctx(
                exe=ctx.exe if ctx else "", args=[], argv=[], cmd=cmd, scope=scope, depth=depth,
                codes=[(body, lang, False)],
            )
            code_ctx.args = ctx.args if ctx else []
            result = _run_rules(code_ctx)
            if result is not None:
                return result
    return None


def evaluate_command(command: str, *, word_rules: bool = False) -> Decision:
    """Return a safe decision without including submitted command text.

    `word_rules=True` selects the conservative legacy word matching, used for
    payloads that cannot be told apart from prose.
    """

    compact = str(command).strip()
    if not compact:
        return Decision(True)
    if word_rules:
        return _legacy_evaluate_command(compact)
    if re.fullmatch(
        r"\s*(?:python3\s+)?(?:\S*/)?worktree-lifecycle\.py\s+attach-local-env"
        r"(?:\s+[^;&|`$\r\n]+)+\s*",
        compact,
    ):
        return Decision(True)
    result = _check_script_text(compact, {}, 0)
    return result if result is not None else Decision(True)


def prompt_requests_secret_reveal(prompt: str) -> bool:
    """Detect requests to visually expose a complete provider credential."""

    normalized = " ".join(str(prompt).lower().split())
    reveal = re.search(
        r"\b(?:screenshot|snapshot|capture|photograph|record|dump|download|inspect|view|show|read|copy|extract)\b",
        normalized,
    )
    secret = re.search(r"\b(?:api[ _-]?key|token|credential|secret|password|private key)\b", normalized)
    surface = re.search(r"\b(?:page|dashboard|provider|console|accessibility|ax tree|developer portal)\b", normalized)
    if not (reveal and secret):
        return False
    complete = re.search(
        r"\b(?:full|complete|entire|unmasked|revealed|plain[ -]?text)\b",
        normalized,
    )
    if complete:
        return True
    if not surface:
        return False
    safe_display = re.search(
        r"\b(?:redacted|masked|hidden|concealed|last four|last 4|prefix only|not visible|no longer visible)\b",
        normalized,
    )
    return not bool(safe_display)


def prompt_clears_secret_visual_boundary(prompt: str) -> bool:
    """Recognize an explicit statement that the credential surface is closed."""

    normalized = " ".join(str(prompt).lower().split())
    if re.search(r"\b(?:do not|don't|never)\s+(?:clear|reset)\s+(?:the\s+)?visual guard\b", normalized):
        return False
    if "clear the visual guard" in normalized or "reset the visual guard" in normalized:
        return True
    secret = re.search(r"\b(?:api[ _-]?key|token|credential|secret|password|private key)\b", normalized)
    safe_state = re.search(
        r"\b(?:is|page is|screen is|now)\s+(?:closed|hidden|masked|concealed)\b|"
        r"\b(?:closed|left|exited|navigated away from)\s+(?:the\s+)?(?:provider|credential|key|secret)\b",
        normalized,
    )
    return bool(secret and safe_state)


def _visual_scope(payload: dict[str, Any]) -> str:
    for key in ("session_id", "sessionId", "conversation_id", "conversationId"):
        value = str(payload.get(key) or "").strip()
        if value:
            return f"session:{value}"
    cwd = str(payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or "").strip()
    return f"cwd:{cwd}" if cwd else ""


def _visual_state_root(state_dir: Path | None = None) -> Path:
    if state_dir is not None:
        return Path(state_dir)
    configured = os.environ.get("SIFUTUTOR_SECRET_GUARD_STATE_DIR", "").strip()
    if configured:
        return Path(configured)
    return Path.home() / ".cache" / "sifututor-agent-os" / "secret-visual-guard"


def _visual_marker(payload: dict[str, Any], state_dir: Path | None = None) -> Path | None:
    scope = _visual_scope(payload)
    if not scope:
        return None
    digest = hashlib.sha256(scope.encode("utf-8")).hexdigest()
    return _visual_state_root(state_dir) / f"{digest}.active"


def mark_secret_visual_boundary(
    payload: dict[str, Any], *, state_dir: Path | None = None, now: float | None = None
) -> bool:
    """Create a short-lived metadata-only marker for a credential reveal surface."""

    marker = _visual_marker(payload, state_dir)
    if marker is None:
        return False
    marker.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        marker.parent.chmod(0o700)
    except OSError:
        pass
    marker.write_text("active\n", encoding="utf-8")
    try:
        marker.chmod(0o600)
    except OSError:
        pass
    timestamp = time.time() if now is None else now
    os.utime(marker, (timestamp, timestamp))
    return True


def clear_secret_visual_boundary(
    payload: dict[str, Any], *, state_dir: Path | None = None
) -> None:
    marker = _visual_marker(payload, state_dir)
    if marker is not None:
        marker.unlink(missing_ok=True)


def secret_visual_boundary_active(
    payload: dict[str, Any], *, state_dir: Path | None = None, now: float | None = None
) -> bool:
    marker = _visual_marker(payload, state_dir)
    return bool(marker is not None and marker.is_file())


def sync_secret_visual_boundary(
    payload: dict[str, Any],
    prompt: str,
    *,
    state_dir: Path | None = None,
    now: float | None = None,
) -> bool:
    """Update the marker from a prompt and return the resulting active state."""

    if prompt_requests_secret_reveal(prompt):
        mark_secret_visual_boundary(payload, state_dir=state_dir, now=now)
    elif prompt_clears_secret_visual_boundary(prompt):
        clear_secret_visual_boundary(payload, state_dir=state_dir)
    return secret_visual_boundary_active(payload, state_dir=state_dir, now=now)


def _direct_patch_data(tool_name: str, tool_input: Any) -> bool:
    """Recognize inert direct editor payloads, never executable wrappers."""
    if tool_name in {"Edit", "Write", "edit", "write"}:
        return True
    if tool_name not in {"apply_patch", "functions.apply_patch"}:
        return False
    value = tool_input
    if isinstance(value, dict):
        if set(value) not in ({"input"}, {"patch"}, {"command"}):
            return False
        value = next(iter(value.values()))
    return (
        isinstance(value, str)
        and value.startswith("*** Begin Patch\n")
        and value.rstrip().endswith("\n*** End Patch")
    )


def _visual_capture_request(tool_name: str, tool_input: Any) -> bool:
    """Return True only for tools capable of capturing a visible credential."""

    normalized_name = tool_name.lower()
    if any(marker in normalized_name for marker in ("cua", "computer_use", "view_image", "screenshot")):
        return True
    if normalized_name in {"web__run", "web.run"}:
        return "screenshot" in json.dumps(tool_input).lower()
    if normalized_name in {"functions.exec", "exec", "exec_command", "bash"}:
        source = json.dumps(tool_input).lower()
        return any(marker in source for marker in (
            "cua.", "getstate", "screenshot", "screencapture", "view_image", "emitimage",
        ))
    return False


def evaluate_tool_request(
    tool_name: str,
    tool_input: Any,
    payload: dict[str, Any],
    *,
    state_dir: Path | None = None,
    now: float | None = None,
) -> Decision:
    """Block visual capture during a credential reveal, then check commands."""

    if (
        secret_visual_boundary_active(payload, state_dir=state_dir, now=now)
        and _visual_capture_request(tool_name, tool_input)
    ):
        return Decision(
            False,
            "Visual capture is blocked while a complete credential may be visible. Hide or leave the credential page before capturing it.",
        )
    # Direct editor contents are inert data, not shell invocations. Native
    # path permissions and the separate secret-artifact scan remain responsible
    # for writes. Execution wrappers retain command inspection.
    if _direct_patch_data(tool_name, tool_input):
        return Decision(True)
    # A malformed, mixed or unrecognised apply_patch payload cannot be told apart
    # from a command, so it keeps the conservative word rules.
    legacy_text_rules = "apply_patch" in tool_name.lower()
    for command in _command_texts_for_tool(tool_name, tool_input):
        decision = evaluate_command(command, word_rules=legacy_text_rules)
        if not decision.allowed:
            return decision
    return Decision(True)


def safe_command_label(command: str) -> str:
    """Return only a coarse executable label suitable for a failure log."""

    normalized = " ".join(str(command).split()).lower()
    allowed_labels = (
        "git",
        "gh",
        "rg",
        "python",
        "python3",
        "node",
        "npm",
        "pnpm",
        "yarn",
        "php",
        "composer",
        "pytest",
        "curl",
        "ssh",
        "rsync",
        "docker",
        "kubectl",
        "pm2",
        "bash",
        "sh",
        "zsh",
    )
    match = re.search(
        r"(?:^|[;&|]\s*)(?:(?:sudo|env)\s+)?(?:" +
        r"(?:[a-z_][a-z0-9_]*=[^\s]+\s+)*)([a-z0-9._/-]+)",
        normalized,
    )
    if not match:
        return "redacted"
    executable = match.group(1).rsplit("/", 1)[-1]
    return executable if executable in allowed_labels else "redacted"


# Tools that never run a shell command. Their text fields (an agent brief, a
# question, a memory note, a message) are prose, so a word such as "credential"
# or ".env" inside them is not an operation and must not be inspected.
_NON_COMMAND_TOOLS = frozenset(
    {
        "agent", "task", "sendmessage", "askuserquestion", "todowrite", "skill", "toolsearch",
        "taskcreate", "taskupdate", "taskget", "tasklist", "taskoutput", "taskstop",
        "enterplanmode", "exitplanmode", "webfetch", "websearch", "read", "glob", "grep",
        "notebookedit", "artifact", "artifactcomments", "artifactdata", "enterworktree",
        "exitworktree",
    }
)


def _command_texts_for_tool(tool_name: str, tool_input: Any) -> list[str]:
    """Return only the text a tool will actually execute as a command."""

    name = tool_name.lower()
    if name in _NON_COMMAND_TOOLS:
        return []
    if name.startswith("mcp__"):
        # MCP servers receive structured data, not a shell. Inspect only an
        # explicit command field so free text (notes, content) is not a command.
        if isinstance(tool_input, dict):
            return [
                value
                for key in ("command", "cmd")
                for value in [tool_input.get(key)]
                if isinstance(value, str)
            ]
        return []
    return _collect_command_text(tool_input)


def _collect_command_text(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        source = value.get("input")
        if isinstance(source, str) and "tools." in source:
            if "tools.exec_command" not in source:
                return []
            matches = re.findall(
                r"\bcmd\s*:\s*(\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`|[A-Za-z_$][A-Za-z0-9_$]*)",
                source,
                flags=re.S,
            )
            extracted: list[str] = []
            for expression in matches:
                encoded = expression
                if expression[0] not in "\"'`":
                    assignment = re.search(
                        rf"\b(?:const|let|var)\s+{re.escape(expression)}\s*=\s*"
                        r"(\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`)",
                        source,
                        flags=re.S,
                    )
                    if assignment is None:
                        return [source]
                    encoded = assignment.group(1)
                try:
                    if encoded.startswith('"'):
                        extracted.append(json.loads(encoded))
                    else:
                        extracted.append(encoded[1:-1])
                except (json.JSONDecodeError, IndexError):
                    return [source]
            if extracted:
                return extracted
            return [source]
        preferred = [
            value[key]
            for key in ("command", "cmd", "input", "source", "code")
            if key in value
        ]
        if preferred:
            parts: list[str] = []
            for item in preferred:
                parts.extend(_collect_command_text(item))
            return parts
        parts = []
        for item in value.values():
            parts.extend(_collect_command_text(item))
        return parts
    if isinstance(value, list):
        parts = []
        for item in value:
            parts.extend(_collect_command_text(item))
        return parts
    return []


def _deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, TypeError):
        return 0

    tool_name = str(payload.get("tool_name") or payload.get("toolName") or "")
    tool_input = payload.get("tool_input") or payload.get("toolInput") or {}
    decision = evaluate_tool_request(tool_name, tool_input, payload)
    if not decision.allowed:
        _deny(decision.reason)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
