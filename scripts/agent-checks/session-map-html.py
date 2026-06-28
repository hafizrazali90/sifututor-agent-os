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
FLOW_STAGES = [
    "Exploring",
    "Decided",
    "Updated",
    "Checked",
    "Committed",
    "On GitHub",
    "Done",
]


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
    if any(word in normalized for word in ["on github", "pushed", "done", "passed", "closed", "committed"]):
        return "done"
    if any(word in normalized for word in ["exploring", "decided", "updated", "checked", "active", "progress", "discussing"]):
        return "active"
    if any(word in normalized for word in ["waiting", "parked", "paused", "captured", "needs hafiz", "needs decision"]):
        return "waiting"
    return "neutral"


def flow_stage(status: str) -> str:
    normalized = " ".join(status.lower().replace("-", " ").replace("_", " ").split())
    aliases = {
        "thinking": "Exploring",
        "talking": "Exploring",
        "in discussion": "Exploring",
        "discussing": "Exploring",
        "not started": "Exploring",
        "agreed": "Decided",
        "chosen": "Decided",
        "approved": "Decided",
        "written": "Updated",
        "done locally": "Updated",
        "local": "Updated",
        "passed": "Checked",
        "verified": "Checked",
        "committed": "Committed",
        "saved": "Committed",
        "pushed": "On GitHub",
        "shared": "On GitHub",
        "merged": "Done",
        "closed": "Done",
        "finished": "Done",
    }
    for stage in FLOW_STAGES:
        if stage.lower() in normalized:
            return stage
    for key, stage in aliases.items():
        if key in normalized:
            return stage
    return "Exploring"


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


def status_label(status: str) -> str:
    css = status_class(status)
    label = status.strip().replace("_", " ").replace("-", " ")
    label = " ".join(label.split())
    return f"<span class=\"badge {css}\">{markdown_inline(label.title())}</span>"


def status_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    counts = {"done": 0, "active": 0, "waiting": 0, "neutral": 0}
    for row in rows:
        counts[status_class(row.get("Status", ""))] += 1
    return counts


def render_metric_strip(progress: list[dict[str, str]], decisions: list[dict[str, str]], side_paths: list[dict[str, str]]) -> str:
    counts = status_counts(progress)
    metrics = [
        ("Moving", str(counts["active"]), "Open work in this session"),
        ("Finished", str(counts["done"]), "Completed or already pushed"),
        ("Parked", str(counts["waiting"]), "Captured for later"),
        ("Choices", str(len(decisions)), "Decisions already made"),
        ("Side paths", str(len(side_paths)), "Topics outside the main path"),
    ]
    return "\n".join(
        [
            "<section class=\"metrics\" aria-label=\"Session metrics\">",
            *[
                (
                    "<article class=\"metric-card\">"
                    f"<strong>{html.escape(value)}</strong>"
                    f"<span>{html.escape(label)}</span>"
                    f"<small>{html.escape(help_text)}</small>"
                    "</article>"
                )
                for label, value, help_text in metrics
            ],
            "</section>",
        ]
    )


def collect_waiting(progress: list[dict[str, str]], human: dict[str, str]) -> str:
    waiting = []
    for row in progress:
        status = row.get("Status", "")
        if flow_stage(status) not in {"On GitHub", "Done"}:
            item = row.get("Item", "Untitled item")
            next_step = row.get("Next", "")
            waiting.append(f"{item}: {next_step or status}")
    if waiting:
        return "; ".join(waiting[:3])
    decision = human.get("Decision needed from Hafiz", "")
    return decision if decision and decision.lower() != "no" else "Nothing urgent recorded."


def confidence_text(progress: list[dict[str, str]], links: str) -> str:
    evidence_text = links.lower()
    checked_rows = [row for row in progress if flow_stage(row.get("Status", "")) in {"Checked", "Committed", "On GitHub", "Done"}]
    if any(word in evidence_text for word in ["passed", "checked", "guard", "health", "validator"]):
        return "Evidence recorded. Latest checks are visible below."
    if checked_rows:
        return "Some items have check or commit evidence. Review details below."
    return "Not enough evidence recorded yet."


def render_control_deck(human: dict[str, str], context: dict[str, str], progress: list[dict[str, str]], links: str) -> str:
    cards = [
        ("Now", human.get("Right now", context.get("Current focus", "")), "now"),
        ("Goal", context.get("Main goal", human.get("Started because", "")), "goal"),
        ("Next", human.get("Next recommended move", ""), "next"),
        ("Waiting", collect_waiting(progress, human), "waiting"),
        ("Confidence", confidence_text(progress, links), "confidence"),
    ]
    return "\n".join(
        [
            "<section class=\"control-deck\" aria-label=\"First glance session state\">",
            *[
                (
                    f"<article class=\"control-card {html.escape(css)}\">"
                    f"<span>{html.escape(label)}</span>"
                    f"<p>{markdown_inline(value) if value else '<em>Not recorded.</em>'}</p>"
                    "</article>"
                )
                for label, value, css in cards
            ],
            "</section>",
        ]
    )


def render_progress_flow(progress: list[dict[str, str]]) -> str:
    if not progress:
        current_stage = "Exploring"
    else:
        stage_indexes = [FLOW_STAGES.index(flow_stage(row.get("Status", ""))) for row in progress]
        current_stage = FLOW_STAGES[max(stage_indexes)]

    current_index = FLOW_STAGES.index(current_stage)
    parts = ["<section class=\"flow-panel panel\"><h2>Progress Flow</h2><div class=\"flow-bar\">"]
    for index, stage in enumerate(FLOW_STAGES):
        css = "complete" if index < current_index else "current" if index == current_index else "future"
        parts.append(
            "<div class=\"flow-step\">"
            f"<span class=\"flow-dot {css}\"></span>"
            f"<strong>{html.escape(stage)}</strong>"
            "</div>"
        )
    parts.append("</div><p class=\"muted flow-help\">Exploring means still shaping. Committed means saved locally. On GitHub means future agents can fetch it.</p></section>")
    return "\n".join(parts)


def render_focus_banner(human: dict[str, str]) -> str:
    next_move = human.get("Next recommended move", "")
    decision = human.get("Decision needed from Hafiz", "")
    return (
        "<section class=\"focus-banner\" aria-label=\"Current decision point\">"
        "<div><span>Do Next</span>"
        f"<strong>{markdown_inline(next_move) if next_move else 'Not recorded.'}</strong></div>"
        "<div><span>Needs Hafiz</span>"
        f"<strong>{markdown_inline(decision) if decision else 'Not recorded.'}</strong></div>"
        "</section>"
    )


def render_progress_cards(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "<p class=\"muted\">No progress items recorded yet.</p>"

    cards = []
    for row in rows:
        status = row.get("Status", "")
        stage = flow_stage(status)
        cards.append(
            "<article class=\"work-card\">"
            f"<div class=\"work-card-top\">{status_label(stage)}<span>{markdown_inline(row.get('Owner', ''))}</span></div>"
            f"<h3>{markdown_inline(row.get('Item', 'Untitled item'))}</h3>"
            f"<p>{markdown_inline(row.get('Next', ''))}</p>"
            f"<small>{markdown_inline(row.get('Evidence / Link', ''))}</small>"
            "</article>"
        )
    return "<div class=\"work-grid\">" + "\n".join(cards) + "</div>"


def render_decision_timeline(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "<p class=\"muted\">No decisions recorded yet.</p>"

    items = []
    for row in rows[:5]:
        effect = row.get("Effect", "")
        status = row.get("Status", "")
        items.append(
            "<article class=\"timeline-item\">"
            f"<time>{markdown_inline(row.get('Date', ''))}</time>"
            f"{status_label(status) if status else ''}"
            f"<h3>{markdown_inline(row.get('Decision', 'Untitled decision'))}</h3>"
            f"<p><strong>Reason:</strong> {markdown_inline(row.get('Why', ''))}</p>"
            f"{f'<p><strong>Effect:</strong> {markdown_inline(effect)}</p>' if effect else ''}"
            f"<small>{markdown_inline(row.get('Owner', ''))}</small>"
            "</article>"
        )
    return "<div class=\"timeline\">" + "\n".join(items) + "</div>"


def render_side_path_cards(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "<p class=\"muted\">No side paths recorded yet.</p>"

    cards = []
    for row in rows:
        status = row.get("Status", "")
        cards.append(
            "<article class=\"side-card\">"
            f"<div class=\"side-card-top\">{status_label(status)}</div>"
            f"<h3>{markdown_inline(row.get('Side path', 'Untitled side path'))}</h3>"
            f"<p>{markdown_inline(row.get('Why it appeared', ''))}</p>"
            "<div class=\"return-box\"><span>Return path</span>"
            f"<strong>{markdown_inline(row.get('Return path', ''))}</strong></div>"
            "</article>"
        )
    return "<div class=\"side-grid\">" + "\n".join(cards) + "</div>"


def render_reference_pack(section: str, markdown_path: Path, context: dict[str, str]) -> str:
    cleaned = strip_code_blocks(section)
    if not cleaned:
        cleaned = "\n".join(
            [
                f"- Primary Session Map: `{relative(markdown_path)}`",
                f"- Generated dashboard: `{relative(markdown_path.with_suffix('.html'))}`",
                "- Core docs: `docs/agent-playbooks/session-map.md`, `docs/agent-playbooks/templates/session-map.md`, `scripts/agent-checks/session-map-html.py`",
                f"- Branch: `{context.get('Branch', 'not recorded')}`",
                "- What to ignore: product app code, production files, `.env*`, and unrelated docs unless Hafiz asks.",
            ]
        )
    return render_list(cleaned)


def render_visual_mindmap(section: str) -> str:
    cleaned = strip_code_blocks(section)
    items = [line for line in cleaned.splitlines() if line.strip().startswith("- ")]
    if not items:
        return "<p class=\"muted\">No mindmap recorded yet.</p>"

    nodes = []
    for line in items:
        depth = max(0, (len(line) - len(line.lstrip(" "))) // 2)
        label = markdown_inline(line.strip().removeprefix("- ").strip())
        nodes.append(f"<div class=\"map-node depth-{min(depth, 3)}\">{label}</div>")
    return "<div class=\"map-board\">" + "\n".join(nodes) + "</div>"


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
    reference_pack = sections.get("Reference Pack", "")
    continuation = extract_code_block(sections.get("Continuation Prompt", ""), "text")

    mindmap_body = strip_code_blocks(sections.get("Mindmap", ""))
    mermaid = extract_code_block(sections.get("Mindmap", ""), "mermaid")

    context_chips = "\n".join(
        f"<span>{html.escape(key)}: {markdown_inline(value)}</span>"
        for key, value in context.items()
        if key in {"Date", "Project", "Agent", "Branch", "Risk lane", "Approved boundary"}
    )

    mermaid_panel = ""
    if mermaid:
        mermaid_panel = f"<details><summary>Mermaid source</summary><pre>{html.escape(mermaid)}</pre></details>"

    metrics = render_metric_strip(progress, decisions, side_paths)
    control_deck = render_control_deck(human, context, progress, links)
    progress_flow = render_progress_flow(progress)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --bg: #f6f8fb;
      --panel: #ffffff;
      --ink: #18202f;
      --muted: #697386;
      --line: #e1e7f0;
      --soft: #f8fafc;
      --brand: #2563eb;
      --teal: #0f766e;
      --amber: #b45309;
      --green: #15803d;
      --rose: #be123c;
      --shadow: 0 10px 30px rgba(22, 35, 60, 0.06);
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
      background: var(--soft);
      padding: 4px 10px;
      color: var(--muted);
      font-size: 0.82rem;
      font-weight: 650;
    }}
    .focus-banner {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-bottom: 18px;
    }}
    .focus-banner div {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      box-shadow: var(--shadow);
      padding: 16px 18px;
    }}
    .focus-banner span {{
      display: block;
      margin-bottom: 6px;
      color: var(--muted);
      font-size: 0.76rem;
      font-weight: 800;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }}
    .focus-banner strong {{
      display: block;
      font-size: 1.05rem;
      line-height: 1.35;
    }}
    .control-deck {{
      display: grid;
      grid-template-columns: 1.2fr 1.2fr 1fr 1fr 1fr;
      gap: 12px;
      margin-bottom: 18px;
    }}
    .control-card {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      box-shadow: var(--shadow);
      padding: 16px;
      min-height: 138px;
    }}
    .control-card span {{
      display: block;
      margin-bottom: 8px;
      color: var(--muted);
      font-size: 0.78rem;
      font-weight: 850;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    .control-card p {{
      margin: 0;
      font-size: 0.95rem;
      font-weight: 650;
    }}
    .control-card.now {{ background: #f8fbff; }}
    .control-card.goal {{ background: #f6fefc; }}
    .control-card.next {{ background: #fffaf0; }}
    .control-card.waiting {{ background: #fff7ed; }}
    .control-card.confidence {{ background: #f8fafc; }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }}
    .metric-card {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      box-shadow: var(--shadow);
      padding: 14px;
    }}
    .metric-card strong {{
      display: block;
      color: var(--brand);
      font-size: 2rem;
      line-height: 1;
    }}
    .metric-card span {{
      display: block;
      margin-top: 8px;
      font-weight: 800;
    }}
    .metric-card small {{
      display: block;
      margin-top: 2px;
      color: var(--muted);
    }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
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
    .summary-card.primary {{ background: #f8fbff; }}
    .summary-card.focus {{ background: #f6fefc; }}
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
    .flow-panel {{
      margin-bottom: 18px;
    }}
    .flow-bar {{
      display: grid;
      grid-template-columns: repeat(7, minmax(0, 1fr));
      gap: 10px;
    }}
    .flow-step {{
      position: relative;
      display: grid;
      gap: 8px;
      min-height: 76px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 12px;
    }}
    .flow-step strong {{
      font-size: 0.88rem;
      line-height: 1.2;
    }}
    .flow-dot {{
      width: 14px;
      height: 14px;
      border-radius: 50%;
      border: 2px solid var(--line);
      background: #fff;
    }}
    .flow-dot.complete {{
      border-color: #86efac;
      background: var(--green);
    }}
    .flow-dot.current {{
      border-color: #bfdbfe;
      background: var(--brand);
    }}
    .flow-dot.future {{
      background: #f8fafc;
    }}
    .flow-help {{
      margin: 12px 0 0;
      font-size: 0.86rem;
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
      background: var(--soft);
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
    .work-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .work-card, .side-card, .timeline-item {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 14px;
      box-shadow: 0 1px 2px rgba(22, 35, 60, 0.04);
    }}
    .work-card-top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 12px;
    }}
    .work-card-top > span {{
      color: var(--muted);
      font-size: 0.82rem;
      font-weight: 700;
    }}
    .work-card h3, .side-card h3, .timeline-item h3 {{
      margin: 0 0 8px;
      font-size: 0.98rem;
      letter-spacing: 0;
    }}
    .work-card p, .side-card p, .timeline-item p {{
      margin: 0 0 10px;
      color: var(--muted);
      font-size: 0.9rem;
    }}
    .work-card small, .timeline-item small {{
      color: var(--muted);
      font-size: 0.8rem;
    }}
    .timeline {{
      position: relative;
      display: grid;
      gap: 12px;
      padding-left: 18px;
    }}
    .timeline::before {{
      content: "";
      position: absolute;
      left: 5px;
      top: 6px;
      bottom: 6px;
      width: 2px;
      background: var(--line);
    }}
    .timeline-item {{
      position: relative;
    }}
    .timeline-item::before {{
      content: "";
      position: absolute;
      left: -18px;
      top: 19px;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--brand);
    }}
    .timeline-item time {{
      display: block;
      color: var(--brand);
      font-size: 0.78rem;
      font-weight: 800;
      margin-bottom: 4px;
    }}
    .side-grid {{
      display: grid;
      gap: 12px;
    }}
    .side-card {{
      display: grid;
      gap: 9px;
    }}
    .side-card-top {{
      display: flex;
      justify-content: flex-start;
    }}
    .return-box {{
      display: block;
      border-radius: 8px;
      background: var(--soft);
      border: 1px solid #eef2f7;
      padding: 10px;
    }}
    .return-box span {{
      display: block;
      color: var(--muted);
      font-size: 0.72rem;
      font-weight: 800;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      margin-bottom: 4px;
    }}
    .return-box strong {{
      display: block;
      font-size: 0.88rem;
    }}
    .map-board {{
      display: grid;
      gap: 9px;
    }}
    .map-node {{
      position: relative;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 10px 12px;
      font-weight: 750;
    }}
    .map-node.depth-0 {{
      border-color: #bfdbfe;
      background: #eff6ff;
      color: #1d4ed8;
      font-size: 1rem;
    }}
    .map-node.depth-1 {{ margin-left: 18px; background: #f8fbff; }}
    .map-node.depth-2 {{ margin-left: 36px; background: #f6fefc; font-weight: 700; }}
    .map-node.depth-3 {{ margin-left: 54px; background: #fffaf0; font-weight: 650; }}
    .plain-list {{
      margin: 0;
      padding: 0;
      list-style: none;
    }}
    .plain-list li {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 8px 10px;
      margin-bottom: 8px;
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
      .summary-grid, .grid, .focus-banner, .metrics, .work-grid, .control-deck, .flow-bar {{
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
        <div class="eyebrow">Sifututor Agent OS Session Control Board</div>
        <h1>{html.escape(title)}</h1>
      </div>
      <div class="chips">{context_chips}</div>
    </header>

    {control_deck}

    {metrics}

    {progress_flow}

    <section class="grid">
      <div>
        <section class="panel">
          <h2>Work Items</h2>
          {render_progress_cards(progress)}
          <details><summary>Show original table</summary>{render_table(progress)}</details>
        </section>

        <section class="panel">
          <h2>Decision Board</h2>
          {render_decision_timeline(decisions)}
          <details><summary>Show full decision history</summary>{render_table(decisions)}</details>
        </section>

        <section class="panel">
          <h2>Side Paths</h2>
          {render_side_path_cards(side_paths)}
        </section>
      </div>

      <aside>
        <section class="panel">
          <h2>Session Map</h2>
          {render_visual_mindmap(mindmap_body)}
          {mermaid_panel}
        </section>

        <section class="panel">
          <h2>Evidence / Checks</h2>
          {render_list(links)}
        </section>

        <section class="panel">
          <h2>Reference Pack</h2>
          {render_reference_pack(reference_pack, markdown_path, context)}
        </section>

        <section class="panel">
          <h2>Continuation Prompt</h2>
          <pre>{html.escape(continuation) if continuation else "No continuation prompt recorded."}</pre>
        </section>
      </aside>
    </section>

    <p class="footer">
      Source: {html.escape(relative(markdown_path))}. Update the Markdown, then regenerate this view.
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
