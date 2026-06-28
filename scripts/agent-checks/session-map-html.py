#!/usr/bin/env python3
"""Generate a readable HTML dashboard from a Session Map Markdown file."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SESSION_DIR = ROOT / ".agent-os" / "session-maps"

FIELD_PATTERN = re.compile(r"^- \*\*(?P<name>[^:]+):\*\*\s*(?P<value>.*)$")


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def split_sections(markdown: str) -> tuple[str, dict[str, str]]:
    lines = markdown.splitlines()
    title = lines[0].removeprefix("# ").strip() if lines else "Session Map"
    sections: dict[str, list[str]] = {}
    current: str | None = None

    for line in lines[1:]:
        if line.startswith("## "):
            current = line.removeprefix("## ").strip()
            sections[current] = []
            continue
        if current:
            sections[current].append(line)

    return title, {key: "\n".join(value).strip() for key, value in sections.items()}


def extract_fields(section: str) -> dict[str, str]:
    fields: dict[str, list[str]] = {}
    current: str | None = None

    for line in section.splitlines():
        match = FIELD_PATTERN.match(line)
        if match:
            current = match.group("name").strip()
            fields[current] = [match.group("value").strip()]
            continue
        if current and line.startswith("  "):
            fields[current].append(line.strip())
            continue
        current = None

    return {key: " ".join(part for part in value if part).strip() for key, value in fields.items()}


def parse_table(section: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return []

    headers = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells)))
    return rows


def strip_code_blocks(section: str) -> str:
    return re.sub(r"```.*?```", "", section, flags=re.DOTALL).strip()


def extract_code_block(section: str, language: str | None = None) -> str:
    if language:
        pattern = rf"```{re.escape(language)}\n(?P<body>.*?)```"
    else:
        pattern = r"```\w*\n(?P<body>.*?)```"
    match = re.search(pattern, section, flags=re.DOTALL)
    return match.group("body").strip() if match else ""


def markdown_inline(value: str) -> str:
    escaped = html.escape(value)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    return escaped


def render_list(section: str) -> str:
    cleaned = strip_code_blocks(section)
    items = [line for line in cleaned.splitlines() if line.strip().startswith("- ")]
    if not items:
        return f"<p>{markdown_inline(cleaned)}</p>" if cleaned else "<p class=\"muted\">No details recorded yet.</p>"

    html_lines = ["<ul class=\"plain-list\">"]
    for line in items:
        depth = max(0, (len(line) - len(line.lstrip(" "))) // 2)
        label = markdown_inline(line.strip().removeprefix("- ").strip())
        html_lines.append(f"<li style=\"margin-left: {depth * 18}px\">{label}</li>")
    html_lines.append("</ul>")
    return "\n".join(html_lines)


def status_class(status: str) -> str:
    normalized = status.lower()
    if any(word in normalized for word in ["pushed", "done", "passed", "closed", "committed"]):
        return "done"
    if any(word in normalized for word in ["active", "progress", "discussing"]):
        return "active"
    if any(word in normalized for word in ["waiting", "paused", "captured"]):
        return "waiting"
    return "neutral"


def render_table(rows: list[dict[str, str]], *, status_key: str = "Status") -> str:
    if not rows:
        return "<p class=\"muted\">No rows recorded yet.</p>"

    headers = list(rows[0].keys())
    parts = ["<div class=\"table-wrap\"><table>", "<thead><tr>"]
    for header in headers:
        parts.append(f"<th>{html.escape(header)}</th>")
    parts.append("</tr></thead><tbody>")
    for row in rows:
        parts.append("<tr>")
        for header in headers:
            value = row.get(header, "")
            if header == status_key:
                badge = status_class(value)
                parts.append(f"<td><span class=\"badge {badge}\">{markdown_inline(value)}</span></td>")
            else:
                parts.append(f"<td>{markdown_inline(value)}</td>")
        parts.append("</tr>")
    parts.append("</tbody></table></div>")
    return "\n".join(parts)


def card(title: str, value: str, accent: str = "") -> str:
    css = f" summary-card {accent}".strip()
    return (
        f"<article class=\"{css}\">"
        f"<span>{html.escape(title)}</span>"
        f"<p>{markdown_inline(value) if value else '<em>Not recorded.</em>'}</p>"
        "</article>"
    )


def build_html(markdown_path: Path, markdown: str) -> str:
    title, sections = split_sections(markdown)
    human = extract_fields(sections.get("Human Snapshot", ""))
    context = extract_fields(sections.get("Agent Context", ""))
    progress = parse_table(sections.get("Progress Board", ""))
    decisions = parse_table(sections.get("Decisions", ""))
    side_paths = parse_table(sections.get("Side Paths And Return Path", ""))
    links = sections.get("Links And Evidence", "")
    continuation = extract_code_block(sections.get("Continuation Prompt", ""), "text")

    mindmap_body = strip_code_blocks(sections.get("Mindmap", ""))
    mermaid = extract_code_block(sections.get("Mindmap", ""), "mermaid")

    summary_cards = "\n".join(
        [
            card("Main goal", context.get("Main goal", ""), "primary"),
            card("Current focus", human.get("Right now", context.get("Current focus", "")), "focus"),
            card("What changed", human.get("What changed so far", "")),
            card("Recommended next", human.get("Next recommended move", ""), "next"),
            card("Decision needed", human.get("Decision needed from Hafiz", ""), "decision"),
        ]
    )

    context_chips = "\n".join(
        f"<span>{html.escape(key)}: {markdown_inline(value)}</span>"
        for key, value in context.items()
        if key in {"Date", "Project", "Agent", "Branch", "Risk lane", "Approved boundary"}
    )

    mermaid_panel = ""
    if mermaid:
        mermaid_panel = f"<details><summary>Mermaid source</summary><pre>{html.escape(mermaid)}</pre></details>"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --bg: #f5f7fb;
      --panel: #ffffff;
      --ink: #18202f;
      --muted: #697386;
      --line: #dce3ee;
      --brand: #2563eb;
      --teal: #0f766e;
      --amber: #b45309;
      --green: #15803d;
      --rose: #be123c;
      --shadow: 0 18px 45px rgba(22, 35, 60, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }}
    a {{ color: var(--brand); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    code {{
      border-radius: 6px;
      background: #edf2f7;
      padding: 2px 6px;
      font-size: 0.9em;
    }}
    .shell {{
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 32px 0 48px;
    }}
    .hero {{
      display: grid;
      gap: 18px;
      border-bottom: 1px solid var(--line);
      padding-bottom: 24px;
      margin-bottom: 24px;
    }}
    .eyebrow {{
      color: var(--brand);
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(2rem, 4vw, 3.6rem);
      line-height: 1.05;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 1.05rem;
      letter-spacing: 0;
    }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .chips span, .badge {{
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: #fff;
      padding: 4px 10px;
      color: var(--muted);
      font-size: 0.82rem;
      font-weight: 650;
    }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 20px;
    }}
    .summary-card, .panel {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: var(--shadow);
    }}
    .summary-card {{
      padding: 16px;
      min-height: 148px;
      border-top: 4px solid #94a3b8;
    }}
    .summary-card span {{
      display: block;
      margin-bottom: 9px;
      color: var(--muted);
      font-size: 0.78rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .summary-card p {{
      margin: 0;
      font-size: 0.96rem;
      font-weight: 620;
    }}
    .summary-card.primary {{ border-top-color: var(--brand); }}
    .summary-card.focus {{ border-top-color: var(--teal); }}
    .summary-card.next {{ border-top-color: var(--green); }}
    .summary-card.decision {{ border-top-color: var(--amber); }}
    .grid {{
      display: grid;
      grid-template-columns: 1.35fr 0.85fr;
      gap: 18px;
      align-items: start;
    }}
    .panel {{
      padding: 18px;
      margin-bottom: 18px;
    }}
    .table-wrap {{
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 720px;
      background: #fff;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 11px 12px;
      text-align: left;
      vertical-align: top;
      font-size: 0.9rem;
    }}
    th {{
      background: #f8fafc;
      color: var(--muted);
      font-size: 0.74rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    tr:last-child td {{ border-bottom: 0; }}
    .badge.done {{ border-color: #bbf7d0; background: #f0fdf4; color: var(--green); }}
    .badge.active {{ border-color: #bfdbfe; background: #eff6ff; color: var(--brand); }}
    .badge.waiting {{ border-color: #fed7aa; background: #fff7ed; color: var(--amber); }}
    .badge.neutral {{ background: #f8fafc; }}
    .plain-list {{
      margin: 0;
      padding: 0;
      list-style: none;
    }}
    .plain-list li {{
      border-left: 3px solid var(--line);
      padding: 5px 0 5px 10px;
      color: var(--ink);
    }}
    pre {{
      margin: 0;
      overflow-x: auto;
      border-radius: 8px;
      background: #101828;
      color: #f8fafc;
      padding: 14px;
      font-size: 0.86rem;
      white-space: pre-wrap;
    }}
    details {{
      margin-top: 12px;
      color: var(--muted);
    }}
    summary {{
      cursor: pointer;
      font-weight: 700;
    }}
    .muted {{
      color: var(--muted);
    }}
    .footer {{
      margin-top: 24px;
      color: var(--muted);
      font-size: 0.84rem;
    }}
    @media (max-width: 980px) {{
      .summary-grid, .grid {{
        grid-template-columns: 1fr;
      }}
      .summary-card {{
        min-height: auto;
      }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <header class="hero">
      <div>
        <div class="eyebrow">Sifututor Agent OS Session Dashboard</div>
        <h1>{html.escape(title)}</h1>
      </div>
      <div class="chips">{context_chips}</div>
    </header>

    <section class="summary-grid" aria-label="Session summary">
      {summary_cards}
    </section>

    <section class="grid">
      <div>
        <section class="panel">
          <h2>Progress Board</h2>
          {render_table(progress)}
        </section>

        <section class="panel">
          <h2>Decisions</h2>
          {render_table(decisions, status_key="")}
        </section>

        <section class="panel">
          <h2>Side Paths And Return Path</h2>
          {render_table(side_paths)}
        </section>
      </div>

      <aside>
        <section class="panel">
          <h2>Mindmap</h2>
          {render_list(mindmap_body)}
          {mermaid_panel}
        </section>

        <section class="panel">
          <h2>Links And Evidence</h2>
          {render_list(links)}
        </section>

        <section class="panel">
          <h2>Continuation Prompt</h2>
          <pre>{html.escape(continuation) if continuation else "No continuation prompt recorded."}</pre>
        </section>
      </aside>
    </section>

    <p class="footer">
      Generated from {html.escape(relative(markdown_path))}. Edit the Markdown source, then regenerate this view.
    </p>
  </main>
</body>
</html>
"""


def latest_session_map() -> Path:
    candidates = sorted(
        DEFAULT_SESSION_DIR.glob("*.md"),
        key=lambda path: (path.stat().st_mtime, path.name),
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(f"no Session Map Markdown files found in {DEFAULT_SESSION_DIR}")
    return candidates[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Session Map HTML dashboard.")
    parser.add_argument(
        "input",
        nargs="?",
        help="Session Map Markdown file. Defaults to the latest active local Session Map.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output HTML path. Defaults to the input path with .html extension.",
    )
    args = parser.parse_args()

    try:
        input_path = Path(args.input).resolve() if args.input else latest_session_map()
    except FileNotFoundError as exc:
        parser.error(str(exc))

    if not input_path.exists():
        parser.error(f"input file does not exist: {input_path}")

    output_path = Path(args.output).resolve() if args.output else input_path.with_suffix(".html")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    markdown = input_path.read_text(encoding="utf-8")
    output_path.write_text(build_html(input_path, markdown), encoding="utf-8")
    print(f"session-map-html: wrote {relative(output_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
