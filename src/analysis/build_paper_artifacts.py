import argparse
import json
import os
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def resolve_user_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def violation_count(row: dict[str, Any], key: str) -> int:
    return int(row.get("violation_counts", {}).get(key, 0))


def render_main_results_table(metrics_payload: dict[str, Any]) -> str:
    rows = sorted(
        metrics_payload.get("runs", []),
        key=lambda row: (str(row.get("benchmark", "")), str(row.get("subject", "")), str(row.get("run_name", ""))),
    )
    lines = [
        "# Main Results Table",
        "",
        "| Benchmark | Subject | Setting | Run | Total | Compliant | Answer Correct | Correct+Violating | Forbidden | Missing | Consistency |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        scored = int(row.get("answer_scored_cases", 0))
        correct = int(row.get("answer_correct", 0))
        correctness = "N/A" if scored == 0 else f"{correct}/{scored}"
        lines.append(
            "| {benchmark} | {subject} | {setting} | {run} | {total} | {compliant} | {correctness} | {cv} | {forbidden} | {missing} | {consistency} |".format(
                benchmark=row.get("benchmark", ""),
                subject=row.get("subject", "") or "—",
                setting=row.get("setting", ""),
                run=row.get("run_name", ""),
                total=row.get("total_cases", 0),
                compliant=row.get("compliant_cases", 0),
                correctness=correctness,
                cv=row.get("correct_but_violating", 0),
                forbidden=violation_count(row, "forbidden_source_used"),
                missing=violation_count(row, "missing_required_source"),
                consistency=violation_count(row, "consistency_violation"),
            )
        )
    return "\n".join(lines) + "\n"


def render_overview_figure(metrics_payload: dict[str, Any]) -> str:
    rows = metrics_payload.get("runs", [])
    width = 1040
    height = 340
    left = 80
    right = 70
    top = 56
    bottom = 78
    plot_w = width - left - right
    plot_h = height - top - bottom

    parts = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>",
        "<style>",
        "text { font-family: 'IBM Plex Sans', 'DejaVu Sans', sans-serif; fill: #17202a; }",
        ".title { font-size: 24px; font-weight: 700; }",
        ".sub { font-size: 13px; fill: #5f6b76; }",
        ".label { font-size: 13px; font-weight: 600; }",
        ".tick { font-size: 11px; fill: #5f6b76; }",
        "</style>",
        f"<rect x='0' y='0' width='{width}' height='{height}' fill='#f6f8fa'/>",
        f"<text class='title' x='{left}' y='30'>Cross-benchmark diagnostic map</text>",
        f"<text class='sub' x='{left}' y='50'>Green = compliance, blue = answer correctness, red circle = forbidden-source rate. InjecAgent correctness is intentionally not scored.</text>",
    ]

    for pct in range(0, 101, 25):
        y = top + plot_h - (pct / 100) * plot_h
        parts.append(f"<line x1='{left}' y1='{y}' x2='{width - right}' y2='{y}' stroke='#d7dee6' stroke-width='1'/>")
        parts.append(f"<text class='tick' x='{left - 10}' y='{y + 4}' text-anchor='end'>{pct}%</text>")

    step = plot_w / max(len(rows) - 1, 1)
    for idx, row in enumerate(rows):
        x = left + idx * step
        total = max(int(row.get("total_cases", 1)), 1)
        scored = int(row.get("answer_scored_cases", 0))
        compliance = int(round((int(row.get("compliant_cases", 0)) / total) * 100))
        correctness = None if scored == 0 else int(round((int(row.get("answer_correct", 0)) / max(scored, 1)) * 100))
        forbidden = int(round((violation_count(row, "forbidden_source_used") / total) * 100))

        comp_y = top + plot_h - (compliance / 100) * plot_h
        forb_y = top + plot_h - (forbidden / 100) * plot_h
        corr_y = None if correctness is None else top + plot_h - (correctness / 100) * plot_h

        parts.append(f"<line x1='{x}' y1='{top}' x2='{x}' y2='{top + plot_h}' stroke='#eef2f5' stroke-width='1'/>")
        if corr_y is not None:
            parts.append(f"<line x1='{x}' y1='{comp_y}' x2='{x}' y2='{corr_y}' stroke='#7f91a5' stroke-width='2.2' opacity='0.7'/>")
        parts.append(f"<circle cx='{x}' cy='{comp_y}' r='5.5' fill='#2e8b57' stroke='#ffffff' stroke-width='1.4'/>")
        if corr_y is None:
            na_y = top + plot_h - (3 / 100) * plot_h
            parts.append(f"<circle cx='{x}' cy='{na_y}' r='4.2' fill='#ffffff' stroke='#5f6b76' stroke-width='1.4'/>")
            parts.append(f"<text class='tick' x='{x + 8}' y='{na_y + 4}'>N/A</text>")
        else:
            parts.append(f"<circle cx='{x}' cy='{corr_y}' r='5.5' fill='#1f4e79' stroke='#ffffff' stroke-width='1.4'/>")
        radius = 6 + forbidden * 0.16
        parts.append(f"<circle cx='{x}' cy='{forb_y}' r='{radius:.1f}' fill='rgba(178,34,34,0.18)' stroke='#b22222' stroke-width='1.5'/>")

        label = row.get("subject") or row.get("benchmark", "")
        if row.get("benchmark") == "InjecAgent":
            label = row.get("setting", "")
        elif row.get("benchmark") == "HybridQA":
            label = "HybridQA"
        elif row.get("benchmark") == "MMMU":
            label = f"{row.get('subject', '')} {row.get('setting', '')}".strip()
        parts.append(f"<text class='tick' x='{x}' y='{height - 14}' text-anchor='end' transform='rotate(-28 {x},{height - 14})'>{label}</text>")

    legend_x = left
    legend_y = height - 44
    parts.append(f"<circle cx='{legend_x}' cy='{legend_y}' r='5.5' fill='#2e8b57'/><text class='tick' x='{legend_x + 12}' y='{legend_y + 4}'>Compliance</text>")
    parts.append(f"<circle cx='{legend_x + 120}' cy='{legend_y}' r='5.5' fill='#1f4e79'/><text class='tick' x='{legend_x + 132}' y='{legend_y + 4}'>Correctness</text>")
    parts.append(f"<circle cx='{legend_x + 255}' cy='{legend_y}' r='10' fill='rgba(178,34,34,0.18)' stroke='#b22222' stroke-width='1.5'/><text class='tick' x='{legend_x + 272}' y='{legend_y + 4}'>Forbidden-source rate</text>")

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def relativize_image_paths(case: dict[str, Any], panel_dir: Path) -> dict[str, Any]:
    image_info = dict(case.get("image_info", {}))
    rel_paths: list[str] = []
    for image_path in image_info.get("image_paths", []):
        absolute = (PROJECT_ROOT / image_path).resolve()
        rel_paths.append(os.path.relpath(absolute, panel_dir))
    image_info["image_paths"] = rel_paths
    case["image_info"] = image_info
    return case


def pick_case(case_payload: dict[str, Any], benchmark: str) -> dict[str, Any] | None:
    for case in case_payload.get("case_studies", []):
        if case.get("benchmark") == benchmark:
            return case
    return None


def render_case_panel(case: dict[str, Any], panel_title: str) -> str:
    source_blocks = []
    for name, value in case.get("source_previews", {}).items():
        source_blocks.append(
            f"<div class='source'><div class='name'>{name}</div><pre>{value}</pre></div>"
        )

    images = "".join(
        f"<figure><img src='{path}' alt='case image' /><figcaption>{', '.join(case.get('image_info', {}).get('img_type', [])) or 'image'}</figcaption></figure>"
        for path in case.get("image_info", {}).get("image_paths", [])
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{panel_title}</title>
  <style>
    body {{ font-family: "IBM Plex Sans", "Segoe UI", sans-serif; margin: 0; background: #f4f7fa; color: #17202a; }}
    main {{ max-width: 980px; margin: 0 auto; padding: 1.5rem; display: grid; gap: 1rem; }}
    .panel {{ background: white; border: 1px solid #d9e1e8; border-radius: 18px; padding: 1rem; box-shadow: 0 10px 24px rgba(17,24,39,0.05); }}
    h1 {{ margin: 0; font-size: 1.65rem; }}
    h2 {{ margin: 0 0 0.6rem; font-size: 1rem; }}
    .meta {{ color: #5f6b76; font-size: 0.92rem; }}
    .tags {{ display: flex; gap: 0.45rem; flex-wrap: wrap; margin-top: 0.7rem; }}
    .tag {{ border: 1px solid #d9e1e8; border-radius: 999px; padding: 0.22rem 0.55rem; font-size: 0.76rem; }}
    .bad {{ border-color: #f0c9c9; color: #b22222; background: #fff6f6; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.9rem; }}
    .source-grid {{ display: grid; gap: 0.75rem; }}
    .source {{ border: 1px solid #d9e1e8; border-radius: 12px; padding: 0.75rem; background: #fbfcfe; }}
    .name {{ font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; color: #5f6b76; margin-bottom: 0.35rem; }}
    pre {{ margin: 0; white-space: pre-wrap; word-break: break-word; font-family: "IBM Plex Mono", monospace; font-size: 0.82rem; line-height: 1.45; }}
    .summary {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.8rem; }}
    figure {{ margin: 0; }}
    img {{ width: 100%; border-radius: 12px; border: 1px solid #d9e1e8; background: #eef2f5; }}
    figcaption {{ color: #5f6b76; font-size: 0.78rem; margin-top: 0.35rem; }}
    @media (max-width: 900px) {{ .grid, .summary {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <main>
    <section class="panel">
      <h1>{panel_title}</h1>
      <div class="meta">{case.get('benchmark')} • {case.get('run_name')} • {case.get('case_id')}</div>
      <div class="tags">
        <span class="tag">{case.get('prompt_mode')}</span>
        {''.join(f"<span class='tag bad'>{kind}</span>" for kind in case.get('violation_types', []))}
      </div>
    </section>
    <section class="panel">
      <h2>Question / Prompt</h2>
      <pre>{case.get('prompt', '')}</pre>
    </section>
    <section class="panel">
      <div class="summary">
        <div class="source"><div class="name">Expected</div><pre>{case.get('expected_answer') or 'N/A'}</pre></div>
        <div class="source"><div class="name">Model</div><pre>{case.get('model_answer', '')}</pre></div>
        <div class="source"><div class="name">Used sources</div><pre>{', '.join(case.get('final_used_sources', []))}</pre></div>
      </div>
    </section>
    {'<section class="panel"><h2>Image Evidence</h2>' + images + '</section>' if images else ''}
    <section class="panel">
      <h2>Policy Explanation</h2>
      <pre>{case.get('policy_explanation', '')}</pre>
    </section>
    <section class="panel">
      <h2>Source Previews</h2>
      <div class="source-grid">{''.join(source_blocks)}</div>
    </section>
  </main>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build paper-ready artifacts from analysis outputs")
    parser.add_argument("--metrics-json", default="outputs/analysis/cross_benchmark_metrics.json")
    parser.add_argument("--case-studies-json", default="outputs/analysis/case_studies.json")
    parser.add_argument("--write-dir", default="outputs/paper")
    args = parser.parse_args()

    metrics_payload = load_json(resolve_user_path(args.metrics_json))
    case_payload = load_json(resolve_user_path(args.case_studies_json))
    output_dir = resolve_user_path(args.write_dir)
    panel_dir = output_dir / "case_panels"
    panel_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "main_results_table.md").write_text(render_main_results_table(metrics_payload), encoding="utf-8")
    (output_dir / "overview_figure.svg").write_text(render_overview_figure(metrics_payload), encoding="utf-8")

    chosen = {}
    for benchmark in ("InjecAgent", "HybridQA", "MMMU"):
      case = pick_case(case_payload, benchmark)
      if case is None:
          continue
      case = relativize_image_paths(dict(case), panel_dir)
      chosen[benchmark] = {"case_id": case.get("case_id", ""), "run_name": case.get("run_name", "")}
      filename = {
          "InjecAgent": "injecagent_panel.html",
          "HybridQA": "hybridqa_panel.html",
          "MMMU": "mmmu_panel.html",
      }[benchmark]
      title = f"{benchmark} Case Panel"
      (panel_dir / filename).write_text(render_case_panel(case, title), encoding="utf-8")

    (panel_dir / "manifest.json").write_text(json.dumps(chosen, indent=2), encoding="utf-8")
    print(f"wrote {output_dir / 'main_results_table.md'}")
    print(f"wrote {output_dir / 'overview_figure.svg'}")
    print(f"wrote case panels to {panel_dir}")


if __name__ == "__main__":
    main()
