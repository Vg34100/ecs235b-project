import argparse
import json
import os
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>__TITLE__</title>
  <style>
    :root {{
      --bg: #f3f5f7;
      --panel: #ffffff;
      --ink: #17202a;
      --muted: #5f6b76;
      --line: #d9e1e8;
      --good: #2e8b57;
      --warn: #c27c0e;
      --bad: #b22222;
      --blue: #1f4e79;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, #e8f0f7, transparent 24rem),
        linear-gradient(180deg, #f7f8fa 0%, #eef2f5 100%);
    }}
    header {{
      padding: 2rem 2rem 1rem;
      border-bottom: 1px solid var(--line);
      background: rgba(255,255,255,0.72);
      backdrop-filter: blur(6px);
      position: sticky;
      top: 0;
      z-index: 10;
    }}
    h1 {{
      margin: 0 0 0.35rem;
      font-size: 2rem;
      letter-spacing: -0.03em;
    }}
    .sub {{
      margin: 0;
      color: var(--muted);
      max-width: 64rem;
      line-height: 1.45;
    }}
    main {{
      display: grid;
      grid-template-columns: 280px 1fr;
      gap: 1.25rem;
      padding: 1.25rem 1.5rem 2rem;
      align-items: start;
    }}
    aside, section.panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: 0 10px 24px rgba(17, 24, 39, 0.06);
    }}
    aside {{
      padding: 1rem;
      position: sticky;
      top: 7rem;
    }}
    .content {{
      display: grid;
      gap: 1.25rem;
    }}
    .panel {{
      padding: 1rem 1.1rem;
    }}
    .panel h2 {{
      margin: 0 0 0.75rem;
      font-size: 1.1rem;
      letter-spacing: -0.02em;
    }}
    .panel p {{
      color: var(--muted);
      line-height: 1.5;
    }}
    .section-intro {{
      margin: 0 0 0.9rem;
      color: var(--muted);
      line-height: 1.5;
    }}
    .filters {{
      display: grid;
      gap: 0.85rem;
    }}
    .view-tabs {{
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
      margin-bottom: 0.9rem;
    }}
    .view-tab {{
      border: 1px solid var(--line);
      background: #fff;
      color: var(--ink);
      border-radius: 999px;
      padding: 0.5rem 0.85rem;
      font: inherit;
      cursor: pointer;
    }}
    .view-tab.active {{
      background: linear-gradient(180deg, #204768, #173753);
      color: #fff;
      border-color: #173753;
    }}
    label {{
      display: grid;
      gap: 0.35rem;
      font-size: 0.92rem;
      color: var(--muted);
    }}
    select {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 0.55rem 0.7rem;
      font: inherit;
      background: #fff;
      color: var(--ink);
    }}
    .kpis {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 0.8rem;
    }}
    .kpi {{
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 0.9rem;
      background: linear-gradient(180deg, #fff, #f8fafc);
    }}
    .kpi .label {{
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }}
    .kpi .value {{
      margin-top: 0.35rem;
      font-size: 1.7rem;
      font-weight: 700;
      letter-spacing: -0.04em;
    }}
    .table-wrap {{
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 14px;
    }}
    .stack-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 0.8rem;
    }}
    .stack-card {{
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 0.85rem;
      background: linear-gradient(180deg, #fff, #f8fafc);
    }}
    .stack-bar {{
      display: flex;
      height: 22px;
      border-radius: 999px;
      overflow: hidden;
      background: #e8edf2;
      margin: 0.65rem 0 0.5rem;
    }}
    .seg {{
      height: 100%;
    }}
    .seg.forbidden {{ background: var(--bad); }}
    .seg.missing {{ background: var(--warn); }}
    .seg.consistency {{ background: var(--blue); }}
    .legend-list {{
      display: grid;
      gap: 0.3rem;
      font-size: 0.82rem;
      color: var(--muted);
    }}
    .legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
    }}
    .domain-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 0.6rem;
    }}
    .domain-tile {{
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 0.7rem;
      background: #fff;
    }}
    .domain-name {{
      font-size: 0.82rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}
    .domain-value {{
      margin-top: 0.3rem;
      font-size: 1.2rem;
      font-weight: 700;
    }}
    .compare-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 0.8rem;
    }}
    .compare-card {{
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 0.9rem;
      background: linear-gradient(180deg, #fff, #f8fafc);
    }}
    .compare-head {{
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      align-items: baseline;
      margin-bottom: 0.6rem;
    }}
    .compare-title {{
      font-weight: 700;
      font-size: 0.95rem;
    }}
    .compare-sub {{
      color: var(--muted);
      font-size: 0.82rem;
    }}
    .metric-strip {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 0.55rem;
      margin-top: 0.7rem;
    }}
    .metric-pill {{
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 0.55rem 0.6rem;
      background: #fff;
    }}
    .metric-pill .metric-label {{
      font-size: 0.72rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}
    .metric-pill .metric-value {{
      margin-top: 0.18rem;
      font-size: 1.1rem;
      font-weight: 700;
    }}
    .paired-grid {{
      display: grid;
      gap: 0.75rem;
    }}
    .paired-card {{
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 0.85rem;
      background: #fff;
    }}
    .paired-rows {{
      display: grid;
      gap: 0.45rem;
      margin-top: 0.65rem;
    }}
    .paired-row {{
      display: grid;
      grid-template-columns: 92px 1fr 160px;
      gap: 0.65rem;
      align-items: center;
      font-size: 0.85rem;
    }}
    .paired-bar-track {{
      position: relative;
      height: 16px;
      background: #e8edf2;
      border-radius: 999px;
      overflow: hidden;
    }}
    .paired-bar {{
      position: absolute;
      top: 0;
      bottom: 0;
      border-radius: 999px;
    }}
    .paired-bar.good {{ background: var(--good); }}
    .paired-bar.blue {{ background: var(--blue); }}
    .paired-bar.bad {{ background: var(--bad); }}
    .paired-value {{
      text-align: right;
      font-size: 0.82rem;
      color: var(--muted);
    }}
    .metric-mini-grid {{
      display: grid;
      gap: 0.45rem;
      width: 100%;
    }}
    .metric-mini-row {{
      display: grid;
      grid-template-columns: 72px 1fr 56px;
      gap: 0.55rem;
      align-items: center;
      font-size: 0.8rem;
      color: var(--muted);
    }}
    .metric-mini-track {{
      height: 12px;
      background: #e8edf2;
      border-radius: 999px;
      overflow: hidden;
    }}
    .metric-mini-fill {{
      height: 100%;
      border-radius: 999px;
    }}
    .split-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 0.75rem;
    }}
    .split-card {{
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 0.85rem;
      background: linear-gradient(180deg, #fff, #f9fbfd);
    }}
    .split-card h3 {{
      margin: 0;
      font-size: 0.86rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}
    .split-card .big {{
      margin-top: 0.3rem;
      font-size: 1.5rem;
      font-weight: 700;
      letter-spacing: -0.04em;
    }}
    .flow-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 0.65rem;
    }}
    .flow-card {{
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 0.75rem;
      background: #fff;
    }}
    .flow-card.alert {{
      border-color: #f0c9c9;
      background: #fff6f6;
    }}
    .flow-card h4 {{
      margin: 0 0 0.35rem;
      font-size: 0.78rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .source-summary {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 0.65rem;
    }}
    .snippet {{
      font-family: "IBM Plex Mono", "DejaVu Sans Mono", monospace;
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 0.8rem;
      line-height: 1.4;
      max-height: 14rem;
      overflow: auto;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 920px;
    }}
    th, td {{
      padding: 0.7rem 0.75rem;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      font-size: 0.92rem;
    }}
    th {{
      background: #f7fafc;
      color: var(--muted);
      font-weight: 600;
      position: sticky;
      top: 0;
    }}
    .metric-bar {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 0.8rem;
      align-items: end;
      min-height: 260px;
    }}
    .run-card {{
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 0.85rem;
      background: #fbfcfd;
    }}
    .run-card h3 {{
      margin: 0 0 0.5rem;
      font-size: 0.96rem;
    }}
    .bar-set {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0.5rem;
      align-items: end;
      height: 150px;
      margin-top: 0.5rem;
    }}
    .bar {{
      display: flex;
      align-items: end;
      justify-content: center;
      border-radius: 10px 10px 4px 4px;
      color: #fff;
      font-size: 0.78rem;
      font-weight: 700;
      min-height: 8px;
      padding-bottom: 0.35rem;
    }}
    .bar.good {{ background: var(--good); }}
    .bar.blue {{ background: var(--blue); }}
    .bar.bad {{ background: var(--bad); }}
    .bar-labels {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0.5rem;
      margin-top: 0.35rem;
      font-size: 0.75rem;
      color: var(--muted);
      text-align: center;
    }}
    .legend-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      margin-top: 0.8rem;
      color: var(--muted);
      font-size: 0.84rem;
    }}
    .legend-chip {{
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
    }}
    .swatch {{
      width: 14px;
      height: 14px;
      border-radius: 4px;
      border: 1px solid rgba(0,0,0,0.08);
      display: inline-block;
    }}
    .cases {{
      display: grid;
      gap: 0.9rem;
    }}
    .method-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 0.8rem;
    }}
    .case {{
      border: 1px solid var(--line);
      border-radius: 16px;
      overflow: hidden;
      background: linear-gradient(180deg, #ffffff, #fafcfe);
    }}
    .case-head {{
      padding: 0.85rem 0.95rem;
      border-bottom: 1px solid var(--line);
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      align-items: baseline;
      flex-wrap: wrap;
    }}
    .case-title {{
      font-weight: 700;
      font-size: 0.95rem;
    }}
    .case-meta {{
      color: var(--muted);
      font-size: 0.82rem;
    }}
    .case-body {{
      padding: 0.95rem;
      display: grid;
      gap: 0.8rem;
    }}
    .tags {{
      display: flex;
      gap: 0.4rem;
      flex-wrap: wrap;
    }}
    .tag {{
      border-radius: 999px;
      padding: 0.24rem 0.55rem;
      font-size: 0.75rem;
      border: 1px solid var(--line);
      background: #fff;
    }}
    .tag.bad {{ border-color: #f0c9c9; background: #fff5f5; color: var(--bad); }}
    .tag.good {{ border-color: #cfe7d7; background: #f4fbf7; color: var(--good); }}
    .grid-two {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 0.8rem;
    }}
    .detail {{
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 0.7rem;
      background: #fff;
    }}
    .detail h4 {{
      margin: 0 0 0.4rem;
      font-size: 0.8rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .mono {{
      font-family: "IBM Plex Mono", "DejaVu Sans Mono", monospace;
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 0.84rem;
      line-height: 1.45;
    }}
    .source-list {{
      display: grid;
      gap: 0.55rem;
    }}
    .image-strip {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 0.75rem;
    }}
    .image-card {{
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 0.55rem;
      background: #fff;
    }}
    .image-card img {{
      width: 100%;
      display: block;
      border-radius: 8px;
      background: #eef2f5;
    }}
    .image-caption {{
      margin-top: 0.4rem;
      font-size: 0.78rem;
      color: var(--muted);
    }}
    .source-item {{
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 0.65rem;
      background: #fff;
    }}
    .source-name {{
      font-size: 0.8rem;
      font-weight: 700;
      margin-bottom: 0.25rem;
      color: var(--blue);
    }}
    .overview-figure-wrap {{
      border: 1px solid var(--line);
      border-radius: 14px;
      overflow: hidden;
      background: #fff;
    }}
    .overview-figure-wrap svg {{
      display: block;
      width: 100%;
      height: auto;
    }}
    .empty-state {{
      border: 1px dashed var(--line);
      border-radius: 14px;
      padding: 1rem;
      color: var(--muted);
      background: #fbfcfd;
    }}
    @media (max-width: 1000px) {{
      main {{
        grid-template-columns: 1fr;
      }}
      aside {{
        position: static;
      }}
      .kpis {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
      .grid-two {{
        grid-template-columns: 1fr;
      }}
      .method-grid {{
        grid-template-columns: 1fr;
      }}
      .flow-grid, .source-summary {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>__TITLE__</h1>
    <p class="sub">Interactive local analysis view generated from archived benchmark runs. Everything on this page comes from real run outputs, archived manifests, and regenerated analysis artifacts.</p>
  </header>
  <main>
    <aside>
      <div class="view-tabs" id="viewTabs"></div>
      <div class="filters">
        <label>Benchmark
          <select id="benchmarkFilter"></select>
        </label>
        <label>Subject
          <select id="subjectFilter"></select>
        </label>
        <label>Setting
          <select id="settingFilter"></select>
        </label>
        <label>Case Category
          <select id="caseCategoryFilter"></select>
        </label>
      </div>
    </aside>
    <div class="content">
      <div id="viewContent"></div>
    </div>
  </main>
  <script>
    const metricsPayload = __METRICS_JSON__;
    const casePayload = __CASES_JSON__;

    const state = {{
      view: "Overview",
      benchmark: "All",
      subject: "All",
      setting: "All",
      category: "All",
    }};

    const viewDefinitions = [
      ["Overview", "Cross-benchmark summary, headline metrics, and benchmark roles."],
      ["InjecAgent", "Hidden vs explicit prompt-mode comparison, domain breakdown, and core failures."],
      ["HybridQA", "Correctness-vs-compliance divergence and attribution-focused errors."],
      ["MMMU", "Clean vs attack multimodal results, grouped by subject."],
      ["Case Studies", "Representative diagnostic cases across all benchmarks."],
    ];

    function uniqueValues(items, getter) {{
      const values = new Set();
      items.forEach(item => {{
        const value = getter(item);
        if (value) values.add(value);
      }});
      return ["All", ...Array.from(values).sort()];
    }}

    function setOptions(select, options, current) {{
      select.innerHTML = options.map(value => {{
        const selected = value === current ? "selected" : "";
        return `<option value="${{value}}" ${{selected}}>${{value}}</option>`;
      }}).join("");
    }}

    function filterRuns() {{
      return metricsPayload.runs.filter(run => {{
        const viewMatch =
          state.view === "Overview" ? true :
          state.view === "Case Studies" ? true :
          run.benchmark === state.view;
        return viewMatch
          && (state.benchmark === "All" || run.benchmark === state.benchmark)
          && (state.subject === "All" || run.subject === state.subject)
          && (state.setting === "All" || run.setting === state.setting);
      }});
    }}

    function filterCases() {{
      return casePayload.case_studies.filter(item => {{
        const viewMatch =
          state.view === "Overview" ? true :
          state.view === "Case Studies" ? true :
          item.benchmark === state.view;
        return viewMatch
          && (state.benchmark === "All" || item.benchmark === state.benchmark)
          && (state.subject === "All" || !item.domain || item.domain.includes(state.subject.toLowerCase()) || item.run_name.includes(state.subject))
          && (state.category === "All" || item.category === state.category)
          && (state.setting === "All" || item.run_name.includes(state.setting));
      }});
    }}

    function viewIntro() {{
      return Object.fromEntries(viewDefinitions)[state.view] || "";
    }}

    function displaySetting(run) {{
      if (run.benchmark === "MMMU") {{
        if (run.setting === "base") return "clean";
        if (run.setting === "forbidden") return "attack";
      }}
      if (run.benchmark === "InjecAgent" && run.setting === "default") {{
        return "explicit";
      }}
      return run.setting;
    }}

    function rate(value, total) {{
      if (!total) return 0;
      return Math.round((value / total) * 100);
    }}

    function formatCorrect(run) {{
      if (!run.answer_scored_cases) return "N/A";
      return `${{run.answer_correct}}/${{run.answer_scored_cases}}`;
    }}

    function renderKpis(runs) {{
      const totals = runs.reduce((acc, run) => {{
        acc.total += run.total_cases;
        acc.compliant += run.compliant_cases;
        acc.correct += run.answer_correct;
        acc.answerScored += run.answer_scored_cases || 0;
        acc.forbidden += Number((run.violation_counts || {{}}).forbidden_source_used || 0);
        return acc;
      }}, {{ total: 0, compliant: 0, correct: 0, answerScored: 0, forbidden: 0 }});

      const items = [
        ["Runs", runs.length],
        ["Compliant Rate", `${{rate(totals.compliant, totals.total)}}%`],
        ["Correct Rate", totals.answerScored ? `${{rate(totals.correct, totals.answerScored)}}%` : "N/A"],
        ["Forbidden-Source Rate", `${{rate(totals.forbidden, totals.total)}}%`],
      ];

      document.getElementById("kpis").innerHTML = items.map(([label, value]) => `
        <div class="kpi">
          <div class="label">${{label}}</div>
          <div class="value">${{value}}</div>
        </div>
      `).join("");
    }}

    function renderMethodologyPanel() {{
      return `
        <section class="panel">
          <h2>Methodology Guide</h2>
          <div class="method-grid">
            <div class="detail">
              <h4>Benchmark Roles</h4>
              <div class="mono">InjecAgent: core indirect prompt-injection benchmark.\nHybridQA: correctness-vs-compliance and attribution stress test.\nMMMU: image-text benchmark, including forbidden-hint attack variants.</div>
            </div>
            <div class="detail">
              <h4>Metric Definitions</h4>
              <div class="mono">Compliant: no policy violation.\nCorrect: answer matches benchmark answer when benchmark answer scoring exists.\nForbidden-source: forbidden_source_used count.\nMissing required: missing_required_source count.\nConsistency: answer conflicts with benchmark-backed or policy-backed expectations.\nFor MMMU, clean = no injected hint and attack = forbidden-hint condition.</div>
            </div>
            <div class="detail">
              <h4>Caveats</h4>
              <div class="mono">InjecAgent does not use ordinary answer correctness, so its Correct metric is shown as N/A.\nHidden prompt mode keeps attacker text embedded in tool_response but does not show attacker_instruction as a separate prompt field.\nCase-study source previews may include audit metadata that was not directly shown as a top-level prompt source.\nRun settings and violation metrics are distinct: e.g. MMMU attack is the run condition, while forbidden-source is a violation metric.</div>
            </div>
          </div>
        </section>
      `;
    }}

    function renderMetricsTable(runs) {{
      const body = document.getElementById("metricsBody");
      body.innerHTML = runs.map(run => `
        <tr>
          <td>${{run.benchmark}}</td>
          <td>${{run.subject || "—"}}</td>
          <td><span class="mono">${{run.run_name}}</span></td>
          <td>${{displaySetting(run)}}</td>
          <td>${{run.total_cases}}</td>
          <td>${{run.compliant_cases}}</td>
          <td>${{formatCorrect(run)}}</td>
          <td>${{run.correct_but_violating}}</td>
          <td>${{(run.violation_counts || {{}}).forbidden_source_used || 0}}</td>
          <td>${{(run.violation_counts || {{}}).missing_required_source || 0}}</td>
          <td>${{(run.violation_counts || {{}}).consistency_violation || 0}}</td>
        </tr>
      `).join("");
    }}

    function renderBars(runs) {{
      const container = document.getElementById("metricBar");
      container.innerHTML = runs.map(run => {{
        const compliant = rate(run.compliant_cases, run.total_cases);
        const correct = run.answer_scored_cases ? rate(run.answer_correct, run.answer_scored_cases) : 0;
        const forbidden = rate(Number((run.violation_counts || {{}}).forbidden_source_used || 0), run.total_cases);
        return `
          <div class="run-card">
            <h3>${{run.benchmark}}${{run.subject ? ` / ${{run.subject}}` : ""}}${{run.setting ? ` / ${{run.setting}}` : ""}}</h3>
            <div class="case-meta">${{run.run_name}}</div>
            <div class="bar-set">
              <div class="bar good" style="height:${{Math.max(compliant, 4)}}%">${{compliant}}%</div>
              <div class="bar blue" style="height:${{Math.max(correct, 4)}}%">${{run.answer_scored_cases ? `${{correct}}%` : "N/A"}}</div>
              <div class="bar bad" style="height:${{Math.max(forbidden, 4)}}%">${{forbidden}}%</div>
            </div>
            <div class="bar-labels">
              <div>Compliant</div>
              <div>Correct</div>
              <div>Forbidden-source</div>
            </div>
          </div>
        `;
      }}).join("");
    }}

    function renderMetricLegend() {{
      return `
        <div class="legend-row">
          <span class="legend-chip"><span class="swatch" style="background:#2e8b57;"></span> Compliant rate</span>
          <span class="legend-chip"><span class="swatch" style="background:#1f4e79;"></span> Answer-correct rate</span>
          <span class="legend-chip"><span class="swatch" style="background:#b22222;"></span> Forbidden-source rate</span>
        </div>
      `;
    }}

    function renderOverviewFigure(runs) {{
      const width = 980;
      const height = 270;
      const left = 90;
      const right = 90;
      const top = 64;
      const bottom = 82;
      const plotW = width - left - right;
      const plotH = height - top - bottom;

      const rows = runs.map(run => {{
        const compliance = rate(run.compliant_cases, run.total_cases);
        const correctness = run.answer_scored_cases ? rate(run.answer_correct, run.answer_scored_cases) : null;
        const forbidden = rate(Number((run.violation_counts || {{}}).forbidden_source_used || 0), run.total_cases);
        return {{ ...run, compliance, correctness, forbidden }};
      }});

      const step = rows.length > 1 ? plotW / (rows.length - 1) : 0;
      const xAt = idx => left + idx * step;
      const yAt = value => top + plotH - (value / 100) * plotH;

      const yTicks = [0, 25, 50, 75, 100].map(v => `
        <g>
          <line x1="${{left}}" y1="${{yAt(v)}}" x2="${{width - right}}" y2="${{yAt(v)}}" stroke="#d7dee6" stroke-width="1" />
          <text x="${{left - 10}}" y="${{yAt(v) + 4}}" text-anchor="end" font-size="11" fill="#5f6b76">${{v}}%</text>
        </g>
      `).join("");

      const points = rows.map((row, idx) => {{
        const x = xAt(idx);
        const complianceY = yAt(row.compliance);
        const correctnessY = row.correctness === null ? null : yAt(row.correctness);
        const forbiddenY = yAt(row.forbidden);
        const radius = 6 + row.forbidden * 0.16;
        return `
          <g>
            ${correctnessY === null ? "" : `<line x1="${{x}}" y1="${{complianceY}}" x2="${{x}}" y2="${{correctnessY}}" stroke="#7f91a5" stroke-width="2.2" opacity="0.7" />`}
            <circle cx="${{x}}" cy="${{complianceY}}" r="5.5" fill="#2e8b57" stroke="#ffffff" stroke-width="1.5" />
            ${correctnessY === null ? `<circle cx="${{x}}" cy="${{yAt(3)}}" r="4.5" fill="#ffffff" stroke="#5f6b76" stroke-width="1.5" /><text x="${{x + 8}}" y="${{yAt(3) + 4}}" font-size="10" fill="#5f6b76">N/A</text>` : `<circle cx="${{x}}" cy="${{correctnessY}}" r="5.5" fill="#1f4e79" stroke="#ffffff" stroke-width="1.5" />`}
            <circle cx="${{x}}" cy="${{forbiddenY}}" r="${{radius.toFixed(1)}}" fill="rgba(178,34,34,0.18)" stroke="#b22222" stroke-width="1.6" />
            <text x="${{x}}" y="${{height - 28}}" text-anchor="end" transform="rotate(-28 ${{x}},${{height - 28}})" font-size="11" fill="#5f6b76">${{displaySetting(row)}}</text>
          </g>
        `;
      }}).join("");

      return `
        <div class="overview-figure-wrap">
          <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Cross benchmark diagnostic map">
            <rect x="0" y="0" width="${width}" height="${height}" fill="#ffffff" />
            ${yTicks}
            <text x="${left}" y="24" font-size="16" font-weight="700" fill="#17202a">Compliance / correctness divergence with forbidden-source pressure</text>
            <text x="${left}" y="42" font-size="11" fill="#5f6b76">Green = compliance, blue = answer correctness, red circle = forbidden-source rate. Lines show divergence between compliance and correctness for the same run.</text>
            ${points}
          </svg>
        </div>
      `;
    }}

    function renderViolationStacks(runs) {{
      return runs.map(run => {{
        const total = Math.max(run.total_cases, 1);
        const forbidden = Math.round((Number((run.violation_counts || {{}}).forbidden_source_used || 0) / total) * 100);
        const missing = Math.round((Number((run.violation_counts || {{}}).missing_required_source || 0) / total) * 100);
        const consistency = Math.round((Number((run.violation_counts || {{}}).consistency_violation || 0) / total) * 100);
        return `
          <div class="stack-card">
            <div class="case-meta">${{run.run_name}}</div>
            <div class="stack-bar">
              <div class="seg forbidden" style="width:${{forbidden}}%"></div>
              <div class="seg missing" style="width:${{missing}}%"></div>
              <div class="seg consistency" style="width:${{consistency}}%"></div>
            </div>
            <div class="legend-list">
              <div class="legend-item"><span class="swatch" style="background:#b22222;"></span> Forbidden-source: ${{forbidden}}%</div>
              <div class="legend-item"><span class="swatch" style="background:#c27c0e;"></span> Missing required: ${{missing}}%</div>
              <div class="legend-item"><span class="swatch" style="background:#1f4e79;"></span> Consistency: ${{consistency}}%</div>
            </div>
          </div>
        `;
      }}).join("");
    }}

    function renderDomainGrid(runs) {{
      const domains = new Map();
      runs.forEach(run => {{
        Object.entries(run.domain_counts || {{}}).forEach(([domain, count]) => {{
          domains.set(domain, (domains.get(domain) || 0) + count);
        }});
      }});
      return Array.from(domains.entries()).map(([domain, count]) => `
        <div class="domain-tile">
          <div class="domain-name">${{domain}}</div>
          <div class="domain-value">${{count}}</div>
        </div>
      `).join("");
    }}

    function metricPill(label, value) {{
      return `
        <div class="metric-pill">
          <div class="metric-label">${{label}}</div>
          <div class="metric-value">${{value}}</div>
        </div>
      `;
    }}

    function benchmarkSpecificVisuals(runs) {{
      if (state.view === "InjecAgent") {{
        return `
          <section class="panel">
            <h2>Hidden vs Explicit Prompt Modes</h2>
            <div class="compare-grid">
              ${runs.map(run => {{
                const violations = run.total_cases - run.compliant_cases;
                const forbidden = Number((run.violation_counts || {{}}).forbidden_source_used || 0);
                const missing = Number((run.violation_counts || {{}}).missing_required_source || 0);
                const consistency = Number((run.violation_counts || {{}}).consistency_violation || 0);
                return `
                  <div class="compare-card">
                    <div class="compare-head">
                      <div>
                        <div class="compare-title">${{run.setting === "hidden" ? "Hidden attacker source" : "Explicit attacker source"}}</div>
                        <div class="compare-sub">${{run.run_name}}</div>
                      </div>
                      <div class="compare-sub">${{run.compliant_cases}} / ${{run.total_cases}} compliant</div>
                    </div>
                    <div class="stack-bar">
                      <div class="seg forbidden" style="width:${{rate(forbidden, run.total_cases)}}%"></div>
                      <div class="seg missing" style="width:${{rate(missing, run.total_cases)}}%"></div>
                      <div class="seg consistency" style="width:${{rate(consistency, run.total_cases)}}%"></div>
                    </div>
                    <div class="metric-strip">
                      ${{metricPill("Violations", `${{violations}} / ${{run.total_cases}}`)}}
                      ${{metricPill("Forbidden-source", forbidden)}}
                      ${{metricPill("Consistency", consistency)}}
                    </div>
                  </div>
                `;
              }}).join("")}
            </div>
          </section>
        `;
      }}

      if (state.view === "HybridQA") {{
        const run = runs[0];
        if (!run) return "";
        const wrongViolating = run.total_cases - run.answer_correct - run.compliant_cases + run.correct_but_violating;
        return `
          <section class="panel">
            <h2>Correctness vs Compliance Divergence</h2>
            <div class="split-grid">
              <div class="split-card">
                <h3>Correct + Compliant</h3>
                <div class="big">${{run.compliant_cases}}</div>
              </div>
              <div class="split-card">
                <h3>Correct + Violating</h3>
                <div class="big">${{run.correct_but_violating}}</div>
              </div>
              <div class="split-card">
                <h3>Wrong + Violating</h3>
                <div class="big">${{wrongViolating}}</div>
              </div>
            </div>
            <div class="compare-grid" style="margin-top:0.8rem;">
              <div class="compare-card">
                <div class="compare-title">Attribution Pressure</div>
                <div class="compare-sub">HybridQA remains answerable, but many cases fail because required evidence is not attributed correctly.</div>
                <div class="metric-strip">
                  ${{metricPill("Answer correct", `${{run.answer_correct}} / ${{run.answer_scored_cases}}`)}}
                  ${{metricPill("Missing required", Number((run.violation_counts || {{}}).missing_required_source || 0))}}
                  ${{metricPill("Consistency", Number((run.violation_counts || {{}}).consistency_violation || 0))}}
                </div>
              </div>
            </div>
          </section>
        `;
      }}

      if (state.view === "MMMU") {{
        const groups = new Map();
        runs.forEach(run => {{
          const subject = run.subject || "Unknown";
          if (!groups.has(subject)) groups.set(subject, []);
          groups.get(subject).push(run);
        }});
        return `
          <section class="panel">
            <h2>Clean vs Attack by Subject</h2>
            <div class="paired-grid">
              ${Array.from(groups.entries()).map(([subject, subjectRuns]) => {{
                const base = subjectRuns.find(run => run.setting === "base");
                const forbidden = subjectRuns.find(run => run.setting === "forbidden");
                const cards = [base, forbidden].filter(Boolean);
                return `
                  <div class="paired-card">
                    <div class="compare-head">
                      <div>
                        <div class="compare-title">${{subject}}</div>
                        <div class="compare-sub">Visual reasoning under clean vs forbidden-hint attack conditions</div>
                      </div>
                    </div>
                    <div class="paired-rows">
                      ${cards.map(run => {{
                        const correctRate = run.answer_scored_cases ? rate(run.answer_correct, run.answer_scored_cases) : 0;
                        const forbiddenRate = rate(Number((run.violation_counts || {{}}).forbidden_source_used || 0), run.total_cases);
                        return `
                          <div class="paired-row">
                            <div>${{displaySetting(run)}}</div>
                            <div class="metric-mini-grid">
                              <div class="metric-mini-row">
                                <span class="legend-item"><span class="swatch" style="background:#1f4e79;"></span> correct</span>
                                <div class="metric-mini-track"><div class="metric-mini-fill" style="width:${{correctRate}}%; background:#1f4e79;"></div></div>
                                <span>${{correctRate}}%</span>
                              </div>
                              <div class="metric-mini-row">
                                <span class="legend-item"><span class="swatch" style="background:#b22222;"></span> forbidden-source</span>
                                <div class="metric-mini-track"><div class="metric-mini-fill" style="width:${{forbiddenRate}}%; background:#b22222;"></div></div>
                                <span>${{forbiddenRate}}%</span>
                              </div>
                            </div>
                            <div class="paired-value">${{displaySetting(run)}}</div>
                          </div>
                        `;
                      }}).join("")}
                    </div>
                  </div>
                `;
              }}).join("")}
            </div>
          </section>
        `;
      }}

      return "";
    }}

    function injecAgentCasePanel(item, sourceItems) {{
      return `
        <div class="flow-grid">
          <div class="flow-card">
            <h4>User Request</h4>
            <div class="snippet">${{item.source_previews.user_prompt || item.prompt}}</div>
          </div>
          <div class="flow-card">
            <h4>System Policy</h4>
            <div class="snippet">${{item.source_previews.system_policy || "N/A"}}</div>
          </div>
          <div class="flow-card alert">
            <h4>Attacker-Tainted Content</h4>
            <div class="snippet">${{item.source_previews.attacker_instruction || item.source_previews.tool_response || "N/A"}}</div>
          </div>
          <div class="flow-card">
            <h4>Model Answer</h4>
            <div class="snippet">${{item.model_answer}}</div>
          </div>
        </div>
        <div class="source-summary">
          <div class="detail">
            <h4>Prompt Mode</h4>
            <div class="mono">${{item.prompt_mode}}</div>
          </div>
          <div class="detail">
            <h4>Final Used Sources</h4>
            <div class="mono">${{(item.final_used_sources || []).join(", ")}}</div>
          </div>
          <div class="detail">
            <h4>Violation Explanation</h4>
            <div class="mono">${{item.policy_explanation}}</div>
          </div>
        </div>
        <div class="detail">
          <h4>Audit Sources</h4>
          <div class="source-list">${{sourceItems}}</div>
        </div>
      `;
    }}

    function hybridQACasePanel(item, sourceItems) {{
      return `
        <div class="grid-two">
          <div class="detail">
            <h4>Table Evidence</h4>
            <div class="snippet">${{item.source_previews.table_evidence || "N/A"}}</div>
          </div>
          <div class="detail">
            <h4>Linked Text</h4>
            <div class="snippet">${{item.source_previews.linked_text || "N/A"}}</div>
          </div>
        </div>
        <div class="source-summary">
          <div class="detail">
            <h4>Expected vs Model</h4>
            <div class="mono">Expected: ${{item.expected_answer || "N/A"}}\nModel: ${{item.model_answer}}</div>
          </div>
          <div class="detail">
            <h4>Used Sources</h4>
            <div class="mono">${{(item.final_used_sources || []).join(", ")}}</div>
          </div>
          <div class="detail">
            <h4>Why Violating</h4>
            <div class="mono">${{item.policy_explanation}}</div>
          </div>
        </div>
        <div class="detail">
          <h4>Full Source Previews</h4>
          <div class="source-list">${{sourceItems}}</div>
        </div>
      `;
    }}

    function mmmuCasePanel(item, sourceItems, imageItems) {{
      return `
        ${{imageItems ? `<div class="detail"><h4>Image Evidence</h4><div class="image-strip">${{imageItems}}</div></div>` : ""}}
        <div class="grid-two">
          <div class="detail">
            <h4>Question</h4>
            <div class="snippet">${{item.prompt}}</div>
          </div>
          <div class="detail">
            <h4>Answer Comparison</h4>
            <div class="mono">Expected: ${{item.expected_answer || "N/A"}}\nModel: ${{item.model_answer}}\nUsed: ${{(item.final_used_sources || []).join(", ")}}</div>
          </div>
        </div>
        <div class="source-summary">
          <div class="detail">
            <h4>Prompt Mode</h4>
            <div class="mono">${{item.prompt_mode}}</div>
          </div>
          <div class="detail">
            <h4>Forbidden Hint</h4>
            <div class="snippet">${{item.source_previews.forbidden_hint || "No forbidden hint in this run condition."}}</div>
          </div>
          <div class="detail">
            <h4>Violation Explanation</h4>
            <div class="mono">${{item.policy_explanation}}</div>
          </div>
        </div>
        <div class="detail">
          <h4>Source Previews</h4>
          <div class="source-list">${{sourceItems}}</div>
        </div>
      `;
    }}

    function renderCases(cases) {{
      const container = document.getElementById("caseContainer");
      if (!cases.length) {{
        container.innerHTML = `<div class="empty-state">No cases match the active filters. Reset the filters on the left or switch views.</div>`;
        return;
      }}
      container.innerHTML = cases.map(item => {{
        const prettyCategory = {{
          injecagent_hidden_failures: "InjecAgent hidden-mode failures",
          hybridqa_correct_but_violating: "HybridQA correct but violating",
          mmmu_forbidden_following: "MMMU forbidden-source following"
        }}[item.category] || item.category;
        const sourceItems = Object.entries(item.source_previews || {{}}).map(([name, value]) => `
          <div class="source-item">
            <div class="source-name">${{name}}</div>
            <div class="mono">${{value}}</div>
          </div>
        `).join("");
        const imageItems = ((item.image_info || {{}}).image_paths || []).map((path, idx) => `
          <div class="image-card">
            <img src="${{path}}" alt="Case image ${{idx + 1}}" />
            <div class="image-caption">${{((item.image_info || {{}}).img_type || []).join(", ") || "Image"}}${{(item.image_info || {{}}).subfield ? ` • ${{(item.image_info || {{}}).subfield}}` : ""}}</div>
          </div>
        `).join("");

        const violationTags = (item.violation_types || []).map(kind => `<span class="tag bad">${{kind}}</span>`).join("");
        const correctnessTag = item.is_correct
          ? `<span class="tag good">correct</span>`
          : `<span class="tag bad">incorrect</span>`;

        const bodyContent =
          item.benchmark === "InjecAgent" ? injecAgentCasePanel(item, sourceItems) :
          item.benchmark === "HybridQA" ? hybridQACasePanel(item, sourceItems) :
          mmmuCasePanel(item, sourceItems, imageItems);

        return `
          <article class="case">
            <div class="case-head">
              <div>
                <div class="case-title">${{item.benchmark}} / ${{item.case_id}}</div>
                <div class="case-meta">${{item.run_name}} • ${{prettyCategory}} • ${{item.domain}}</div>
              </div>
              <div class="tags">${{correctnessTag}}${{violationTags}}</div>
            </div>
            <div class="case-body">
              ${{bodyContent}}
            </div>
          </article>
        `;
      }}).join("");
    }}

    function renderOverviewView(runs, cases) {{
      return `
        ${{renderMethodologyPanel()}}
        <section class="panel">
          <h2>Overview</h2>
          <p class="section-intro">${{viewIntro()}}</p>
          <div class="kpis" id="kpis"></div>
        </section>
        <section class="panel">
          <h2>Cross-Benchmark Diagnostic Map</h2>
          <p class="section-intro">A compact comparison across benchmark settings. This is the overview figure path that should become paper-quality, rather than a grid of small bar charts.</p>
          ${{renderOverviewFigure(runs)}}
          ${{renderMetricLegend()}}
        </section>
        <section class="panel">
          <h2>Run Metrics</h2>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Benchmark</th><th>Subject</th><th>Run</th><th>Setting</th><th>Total</th><th>Compliant</th><th>Correct</th><th>Correct+Violating</th><th>Forbidden</th><th>Missing</th><th>Consistency</th>
                </tr>
              </thead>
              <tbody id="metricsBody"></tbody>
            </table>
          </div>
        </section>
        <section class="panel">
          <h2>Rate Comparison</h2>
          <div class="metric-bar" id="metricBar"></div>
          ${{renderMetricLegend()}}
        </section>
        <section class="panel">
          <h2>Highlighted Cases</h2>
          <div class="cases" id="caseContainer"></div>
        </section>
      `;
    }}

    function renderBenchmarkView(runs, cases) {{
      return `
        <section class="panel">
          <h2>${{state.view}}</h2>
          <p class="section-intro">${{viewIntro()}}</p>
          <div class="kpis" id="kpis"></div>
        </section>
        ${{benchmarkSpecificVisuals(runs)}}
        <section class="panel">
          <h2>Violation Composition</h2>
          <div class="stack-grid">${{renderViolationStacks(runs)}}</div>
        </section>
        <section class="panel">
          <h2>Domain / Subject Footprint</h2>
          <div class="domain-grid">${{renderDomainGrid(runs)}}</div>
        </section>
        <section class="panel">
          <h2>Run Metrics</h2>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Benchmark</th><th>Subject</th><th>Run</th><th>Setting</th><th>Total</th><th>Compliant</th><th>Correct</th><th>Correct+Violating</th><th>Forbidden</th><th>Missing</th><th>Consistency</th>
                </tr>
              </thead>
              <tbody id="metricsBody"></tbody>
            </table>
          </div>
        </section>
        <section class="panel">
          <h2>Benchmark Cases</h2>
          <div class="cases" id="caseContainer"></div>
        </section>
      `;
    }}

    function renderCaseStudyView(cases) {{
      return `
        <section class="panel">
          <h2>Case Studies</h2>
          <p class="section-intro">${{viewIntro()}}</p>
          <div class="legend-row">
            <span class="legend-chip"><span class="swatch" style="background:#ffffff;border-color:#5f6b76;"></span> The left filters still apply here. If this panel is empty, the active benchmark/subject/setting/category filters are excluding all cases.</span>
          </div>
          <div class="cases" id="caseContainer"></div>
        </section>
      `;
    }}

    function renderView(runs, cases) {{
      if (state.view === "Overview") return renderOverviewView(runs, cases);
      if (state.view === "Case Studies") return renderCaseStudyView(cases);
      return renderBenchmarkView(runs, cases);
    }}

    function renderViewTabs() {{
      const container = document.getElementById("viewTabs");
      container.innerHTML = viewDefinitions.map(([name]) => `
        <button class="view-tab ${{state.view === name ? "active" : ""}}" data-view="${{name}}">${{name}}</button>
      `).join("");
      container.querySelectorAll(".view-tab").forEach(button => {{
        button.addEventListener("click", () => {{
          state.view = button.dataset.view;
          state.benchmark = "All";
          state.subject = "All";
          state.setting = "All";
          state.category = "All";
          syncFiltersFromState();
          refresh();
        }});
      }});
    }}

    function syncFiltersFromState() {{
      document.getElementById("benchmarkFilter").value = state.benchmark;
      document.getElementById("subjectFilter").value = state.subject;
      document.getElementById("settingFilter").value = state.setting;
      document.getElementById("caseCategoryFilter").value = state.category;
    }}

    function refresh() {{
      const runs = filterRuns();
      const cases = filterCases();
      document.getElementById("viewContent").innerHTML = renderView(runs, cases);
      if (document.getElementById("kpis")) renderKpis(runs);
      if (document.getElementById("metricsBody")) renderMetricsTable(runs);
      if (document.getElementById("metricBar")) renderBars(runs);
      if (document.getElementById("caseContainer")) renderCases(cases);
      renderViewTabs();
    }}

    function initFilters() {{
      const runs = metricsPayload.runs || [];
      const cases = casePayload.case_studies || [];

      const benchmarkOptions = uniqueValues(runs, run => run.benchmark);
      const subjectOptions = uniqueValues(runs, run => run.subject);
      const settingOptions = uniqueValues(runs, run => run.setting);
      const categoryOptions = uniqueValues(cases, item => item.category);

      const benchmarkFilter = document.getElementById("benchmarkFilter");
      const subjectFilter = document.getElementById("subjectFilter");
      const settingFilter = document.getElementById("settingFilter");
      const categoryFilter = document.getElementById("caseCategoryFilter");

      setOptions(benchmarkFilter, benchmarkOptions, state.benchmark);
      setOptions(subjectFilter, subjectOptions, state.subject);
      setOptions(settingFilter, settingOptions, state.setting);
      setOptions(categoryFilter, categoryOptions, state.category);

      benchmarkFilter.addEventListener("change", event => {{
        state.benchmark = event.target.value;
        refresh();
      }});
      subjectFilter.addEventListener("change", event => {{
        state.subject = event.target.value;
        refresh();
      }});
      settingFilter.addEventListener("change", event => {{
        state.setting = event.target.value;
        refresh();
      }});
      categoryFilter.addEventListener("change", event => {{
        state.category = event.target.value;
        refresh();
      }});
    }}

    initFilters();
    renderViewTabs();
    refresh();
  </script>
</body>
</html>
"""


def resolve_user_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def relativize_case_images(case_payload: dict[str, Any], output_path: Path) -> dict[str, Any]:
    dashboard_dir = output_path.parent.resolve()
    for case in case_payload.get("case_studies", []):
        image_info = case.get("image_info", {})
        image_paths = image_info.get("image_paths", [])
        rel_paths = []
        for image_path in image_paths:
            absolute = (PROJECT_ROOT / image_path).resolve()
            try:
                rel_paths.append(os.path.relpath(absolute, dashboard_dir))
            except ValueError:
                rel_paths.append(str(Path(image_path).as_posix()) if not Path(image_path).is_absolute() else absolute.as_uri())
        image_info["image_paths"] = rel_paths
        case["image_info"] = image_info
    return case_payload


def build_html(metrics_payload: dict[str, Any], case_payload: dict[str, Any], title: str) -> str:
    template = HTML_TEMPLATE.replace("{{", "{").replace("}}", "}")
    return (
        template.replace("__TITLE__", title)
        .replace("__METRICS_JSON__", json.dumps(metrics_payload, ensure_ascii=True))
        .replace("__CASES_JSON__", json.dumps(case_payload, ensure_ascii=True))
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a standalone interactive analysis dashboard")
    parser.add_argument(
        "--metrics-json",
        default="outputs/analysis/cross_benchmark_metrics.json",
        help="Cross-benchmark metrics JSON",
    )
    parser.add_argument(
        "--case-studies-json",
        default="outputs/analysis/case_studies.json",
        help="Case studies JSON",
    )
    parser.add_argument(
        "--write-output",
        default="outputs/analysis/analysis_dashboard.html",
        help="Where to write the standalone HTML dashboard",
    )
    parser.add_argument(
        "--title",
        default="Policy Audit Analysis Dashboard",
        help="Dashboard title",
    )
    args = parser.parse_args()

    output_path = resolve_user_path(args.write_output)
    metrics_payload = load_json(resolve_user_path(args.metrics_json))
    case_payload = relativize_case_images(load_json(resolve_user_path(args.case_studies_json)), output_path)
    html = build_html(metrics_payload, case_payload, args.title)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
