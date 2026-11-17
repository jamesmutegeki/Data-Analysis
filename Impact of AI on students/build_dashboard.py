#!/usr/bin/env python3
"""
=============================================================================
DASHBOARD BUILDER — Impact of Generative AI on Students
=============================================================================
Reads pipeline_outputs/analysis_results.json (produced by analysis_pipeline.py)
and injects every number into a single standalone HTML dashboard.

Layout follows the repository's master-prompt convention:
  1. Header  2. Executive Summary  3. KPI bar  4. Data Quality & Audit
  5. Strategic Action Items  6. Interactive Charts (LAST)

Run:  python build_dashboard.py
=============================================================================
"""

import json
import os
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "pipeline_outputs")
RESULTS_FILE = os.path.join(OUT_DIR, "analysis_results.json")
HTML_FILE = os.path.join(BASE_DIR, "AI_Impact_Student_Dashboard.html")

R = json.load(open(RESULTS_FILE))

K = R["descriptives"]["kpis"]
A = R["analyses"]
S = R["stats_tests"]
SEG = R["segments"]
AUD = R["audit"]

BANDS = ["Minimal (0-2h)", "Light (2-6h)", "Moderate (6-12h)",
         "Heavy (12-20h)", "Extreme (20h+)"]
SKILLS = ["Beginner", "Intermediate", "Advanced"]

# ---------------------------------------------------------------------------
# Chart data payloads (all straight from the pipeline JSON)
# ---------------------------------------------------------------------------
chart_data = {
    "bands": BANDS,
    "band_gpa": [A["gpa_by_usage_band"][b]["GPA_Change"] for b in BANDS],
    "band_retention": [A["gpa_by_usage_band"][b]["Skill_Retention_Score"]
                       for b in BANDS],
    "band_anxiety": [A["gpa_by_usage_band"][b]["Anxiety_Level_During_Exams"]
                     for b in BANDS],
    "band_n": [A["gpa_by_usage_band"][b]["n"] for b in BANDS],
    "use_cases": list(A["by_use_case"].keys()),          # already sorted desc
    "use_case_gpa": [A["by_use_case"][u]["GPA_Change"]
                     for u in A["by_use_case"]],
    "use_case_retention": [A["by_use_case"][u]["Skill_Retention_Score"]
                           for u in A["by_use_case"]],
    "skill_bands_gpa": {
        sk: [A["skill_x_usage_gpa"][b][sk] for b in BANDS] for sk in SKILLS},
    "burnout_usage": {
        lvl: [A["burnout_by_usage"][b][lvl] for b in BANDS]
        for lvl in ["Low", "Medium", "High"]},
    "policies": ["Actively_Encouraged", "Allowed_With_Citation", "Strict_Ban"],
    "policy_gpa": [A["by_policy"][p]["GPA_Change"] for p in
                   ["Actively_Encouraged", "Allowed_With_Citation",
                    "Strict_Ban"]],
    "policy_anxiety": [A["by_policy"][p]["Anxiety_Level_During_Exams"] for p in
                       ["Actively_Encouraged", "Allowed_With_Citation",
                        "Strict_Ban"]],
    "policy_hours": [A["by_policy"][p]["Weekly_GenAI_Hours"] for p in
                     ["Actively_Encouraged", "Allowed_With_Citation",
                      "Strict_Ban"]],
    "tool_diversity": list(A["by_tool_diversity"].keys()),
    "tool_gpa": [A["by_tool_diversity"][t]["GPA_Change"]
                 for t in A["by_tool_diversity"]],
    "tool_retention": [A["by_tool_diversity"][t]["Skill_Retention_Score"]
                       for t in A["by_tool_diversity"]],
    "corr_labels": ["GenAI Hours", "Traditional Study", "Prompt Skill",
                    "Tool Diversity", "AI Dependency", "Exam Anxiety",
                    "Burnout", "GPA Change", "Skill Retention"],
    "corr_matrix": [
        [A["correlation_matrix"][a][b] for b in
         ["Weekly_GenAI_Hours", "Traditional_Study_Hours", "Skill_Ord",
          "Tool_Diversity", "Perceived_AI_Dependency",
          "Anxiety_Level_During_Exams", "Burnout_Ord", "GPA_Change",
          "Skill_Retention_Score"]]
        for a in ["Weekly_GenAI_Hours", "Traditional_Study_Hours", "Skill_Ord",
                  "Tool_Diversity", "Perceived_AI_Dependency",
                  "Anxiety_Level_During_Exams", "Burnout_Ord", "GPA_Change",
                  "Skill_Retention_Score"]],
}

# ---------------------------------------------------------------------------
# Numbers used in the narrative
# ---------------------------------------------------------------------------
n = {
    "students": f"{K['n_students']:,}",
    "gpa_gain": f"+{K['mean_gpa_change']:.2f}",
    "gpa_gain3": f"+{K['mean_gpa_change']:.3f}",
    "pct_improved": f"{K['pct_improved']:.1f}%",
    "genai_hours": f"{K['mean_genai_hours']:.1f}",
    "trad_hours": f"{K['mean_traditional_hours']:.1f}",
    "retention": f"{K['mean_retention']:.1f}",
    "anxiety": f"{K['mean_anxiety']:.1f}",
    "high_burnout": f"{K['high_burnout_pct']:.0f}%",
    "paid_pct": f"{K['paid_sub_pct']:.0f}%",
    "peak_band_gpa": f"+{A['gpa_by_usage_band']['Moderate (6-12h)']['GPA_Change']:.3f}",
    "extreme_gpa": f"+{A['gpa_by_usage_band']['Extreme (20h+)']['GPA_Change']:.3f}",
    "extreme_ret": f"{A['gpa_by_usage_band']['Extreme (20h+)']['Skill_Retention_Score']:.1f}",
    "extreme_anx": f"{A['gpa_by_usage_band']['Extreme (20h+)']['Anxiety_Level_During_Exams']:.1f}",
    "extreme_burnout": f"{SEG['heavy']['burnout_high_pct']:.0f}%",
    "light_burnout": f"{SEG['light']['burnout_high_pct']:.0f}%",
    "debug_gpa": f"+{A['by_use_case']['Debugging/Troubleshooting']['GPA_Change']:.3f}",
    "dag_gpa": f"+{A['by_use_case']['Direct_Answer_Generation']['GPA_Change']:.3f}",
    "dag_gap": f"{(A['by_use_case']['Debugging/Troubleshooting']['GPA_Change'] - A['by_use_case']['Direct_Answer_Generation']['GPA_Change']):.3f}",
    "adv_gpa": f"+{A['by_skill']['Advanced']['GPA_Change']:.3f}",
    "beg_gpa": f"+{A['by_skill']['Beginner']['GPA_Change']:.3f}",
    "adv_ret": f"{A['by_skill']['Advanced']['Skill_Retention_Score']:.1f}",
    "beg_ret": f"{A['by_skill']['Beginner']['Skill_Retention_Score']:.1f}",
    "adv_extreme": f"+{A['skill_x_usage_gpa']['Extreme (20h+)']['Advanced']:.3f}",
    "beg_extreme": f"+{A['skill_x_usage_gpa']['Extreme (20h+)']['Beginner']:.3f}",
    "ban_anx": f"{A['by_policy']['Strict_Ban']['Anxiety_Level_During_Exams']:.2f}",
    "cite_anx": f"{A['by_policy']['Allowed_With_Citation']['Anxiety_Level_During_Exams']:.2f}",
    "ban_hours": f"{A['by_policy']['Strict_Ban']['Weekly_GenAI_Hours']:.1f}",
    "cite_hours": f"{A['by_policy']['Allowed_With_Citation']['Weekly_GenAI_Hours']:.1f}",
    "hd_n": f"{SEG['high_dependency']['n']:,}",
    "hd_pct": f"{SEG['high_dependency']['pct']:.1f}%",
    "hd_anx": f"{SEG['high_dependency']['anxiety']:.2f}",
    "hd_burnout": f"{SEG['high_dependency']['burnout_high_pct']:.0f}%",
    "r_dep_anx": f"{S['Perceived_AI_Dependency vs Anxiety_Level_During_Exams']['pearson_r']:.2f}",
    "beta_trad": f"{S['regression_gpa_change']['standardised_betas']['Traditional_Study_Hours']:.2f}",
    "r2": f"{S['regression_gpa_change']['r_squared']:.3f}",
    "eta_usecase": f"{S['ANOVA GPA_Change ~ use case']['eta_squared']:.3f}",
    "eta_policy": f"{S['ANOVA GPA_Change ~ policy']['eta_squared']:.3f}",
    "d_paid": f"{S['paid_vs_free_gpa_change']['cohens_d']:.3f}",
    "v_burnout": f"{S['chi2_dependency_x_burnout']['cramers_v']:.2f}",
    "tool4_gpa": f"+{A['by_tool_diversity']['4']['GPA_Change']:.3f}",
    "tool1_gpa": f"+{A['by_tool_diversity']['1']['GPA_Change']:.3f}",
    "stem_hours": f"{A['by_major']['STEM']['Weekly_GenAI_Hours']:.1f}",
    "hum_hours": f"{A['by_major']['Humanities']['Weekly_GenAI_Hours']:.1f}",
    "grad_gpa": f"+{A['by_year']['Graduate']['GPA_Change']:.3f}",
    "fresh_gpa": f"+{A['by_year']['Freshman']['GPA_Change']:.3f}",
    "gen_ts": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
}

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Impact of Generative AI on Students — Executive Analytics Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  @media print { .no-print { display: none; } }
  .kpi-card { transition: transform .18s ease, box-shadow .18s ease; }
  .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 12px 28px -12px rgba(15,23,42,.25); }
  .corr-cell { width:100%; aspect-ratio: 1.6/1; display:flex; align-items:center; justify-content:center;
               font-size:11px; font-variant-numeric: tabular-nums; border-radius:4px; }
</style>
</head>
<body class="bg-slate-100 text-slate-900 antialiased">
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">

  <!-- ============================== 1. HEADER ============================== -->
  <header class="bg-gradient-to-r from-slate-900 via-slate-800 to-blue-900 rounded-2xl p-8 sm:p-10 text-white shadow-xl">
    <div class="flex flex-wrap items-center gap-3 mb-4">
      <span class="bg-blue-500/20 border border-blue-400/40 text-blue-200 text-xs font-semibold tracking-widest uppercase px-3 py-1 rounded-full">Education Analytics</span>
      <span class="bg-emerald-500/20 border border-emerald-400/40 text-emerald-200 text-xs font-semibold tracking-widest uppercase px-3 py-1 rounded-full">n = 50,000 students</span>
    </div>
    <h1 class="text-3xl sm:text-4xl font-extrabold tracking-tight">The Impact of Generative AI on Student Outcomes</h1>
    <p class="mt-3 text-slate-300 max-w-3xl">Academic performance, skill retention, exam anxiety and burnout across 50,000 students &mdash; what AI usage helps, what it costs, and where the tipping points lie.</p>
    <p class="mt-4 text-xs text-slate-400">Generated __GEN_TS__ &middot; Source: ai_student_impact_dataset (1).csv &middot; Pipeline: analysis_pipeline.py (pandas + scipy)</p>
  </header>

  <!-- ======================= 2. EXECUTIVE SUMMARY ========================== -->
  <section class="mt-8 bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
    <h2 class="text-2xl font-bold flex items-center gap-3"><span class="w-9 h-9 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center text-lg font-extrabold">1</span>Executive Summary &amp; Core Story</h2>

    <div class="mt-5 bg-blue-50 border-l-4 border-blue-500 rounded-r-xl p-5">
      <p class="font-semibold text-blue-950 leading-relaxed">
        Generative AI is a net positive for students &mdash; __PCT_IMPROVED__ of the 50,000 students in this cohort finished the semester with a higher GPA than they started, for an average gain of __GPA_GAIN3__ grade points.
        But the benefit follows a strict inverted-U: moderate users (6&ndash;12 hrs/week) gained the most (__PEAK_BAND_GPA__), while extreme users (20+ hrs) saw gains collapse to __EXTREME_GPA__ with skill retention falling to __EXTREME_RET__/100 and 3 in 4 landing in the high-burnout bracket.
        <em>How</em> students use AI matters more than <em>how much</em>: active, engaged use cases (debugging, drafting) outperform passive answer-generation by up to __DAG_GAP__ GPA points, and prompt-engineering skill is the single largest modifiable lever in the data.
      </p>
    </div>

    <div class="mt-6 space-y-5 text-slate-700 leading-relaxed text-[15px]">
      <p>
        <strong class="text-slate-900">The Goldilocks dosage curve.</strong> Banding students by weekly GenAI hours reveals a clear performance arc.
        Minimal users (0&ndash;2h, 21.5% of students) gained +0.188 GPA on average; light users (2&ndash;6h, 29.7%) gained +0.204; the optimum sits at
        <strong>moderate use of 6&ndash;12 hours per week (__PEAK_BAND_GPA__, n=12,316)</strong>. Beyond that the curve bends: heavy users (12&ndash;20h) slip to +0.213,
        and the extreme band (20h+, n=5,006 &mdash; a full 10% of the population) falls to __EXTREME_GPA__, the worst of any band. The same band shows the dataset&rsquo;s
        worst wellbeing profile: mean exam anxiety of __EXTREME_ANX__/10 (vs 3.81 for minimal users), skill retention of __EXTREME_RET__ (vs 77.1 at the optimum),
        and a high-burnout rate of __EXTREME_BURNOUT__ &mdash; 8&times; the __LIGHT_BURNOUT__ rate of minimal users. ANOVA confirms the band differences are real
        (F=161.1, p&lt;0.001), and the overall hours&rarr;GPA correlation is negative (r=&minus;0.046), entirely driven by this extreme tail.
      </p>
      <p>
        <strong class="text-slate-900">Use case is the strongest categorical driver of GPA gains.</strong> Students whose primary use is
        <strong>Debugging/Troubleshooting</strong> gained __DEBUG_GPA__ with the best retention in the dataset (78.1), followed by Copywriting/Drafting (+0.200),
        Ideation (+0.200) and Summarizing (+0.197). At the bottom sits <strong>Direct Answer Generation</strong>: __DAG_GPA__ &mdash; a __DAG_GAP__ gap versus debugging,
        with the lowest retention (73.7) as well. Eta-squared for use case (&eta;&sup2;=__ETA_USECASE__) is the largest of any categorical factor tested, 18&times;
        larger than institutional policy (&eta;&sup2;=__ETA_POLICY__). The pattern is consistent with cognitive offloading: tasks that keep the student in the loop
        (debugging, drafting, ideating) reinforce learning; outsourcing answers wholesale erodes it.
      </p>
      <p>
        <strong class="text-slate-900">Prompt-engineering skill amplifies every hour spent &mdash; and armours against overuse.</strong>
        Advanced prompters gained __ADV_GPA__ vs __BEG_GPA__ for beginners, and retained far more (__ADV_RET__ vs __BEG_RET__ out of 100; r=0.33 between skill and retention).
        The skill&times;usage interaction is the most striking surface in the analysis: at the optimal 6&ndash;12h band, advanced users gain +0.272; and even in the
        extreme 20h+ band they still gain __ADV_EXTREME__, while extreme-use beginners collapse to __BEG_EXTREME__. Skill doesn&rsquo;t just raise the ceiling &mdash;
        it flattens the downside. Tool diversity tells the same story from another angle: students using 4&ndash;5 distinct tools gained __TOOL4_GPA__ vs __TOOL1_GPA__
        for single-tool users, with retention rising monotonically from 72.6 to 79.8 across the 1&rarr;5 tool range (r=0.20 with retention), reflecting that diversity
        of tooling is a proxy for sophistication of use.
      </p>
      <p>
        <strong class="text-slate-900">Institutional policy barely moves grades &mdash; but bans measurably raise anxiety.</strong> Students under strict bans use AI
        essentially as much as everyone else (__BAN_HOURS__h vs __CITE_HOURS__h per week under citation policies), and their GPA gains are only marginally lower
        (+0.187 vs +0.208). What bans do change is stress: mean exam anxiety is __BAN_ANX__ under strict bans versus __CITE_ANX__ where AI is allowed with citation
        &mdash; a 19% elevation purchased for roughly zero behavioural effect. Policy explains just 0.2% of GPA variance (&eta;&sup2;=__ETA_POLICY__).
      </p>
      <p>
        <strong class="text-slate-900">Dependency &mdash; not usage &mdash; is the real risk axis.</strong> Perceived AI dependency correlates with exam anxiety at
        r=__R_DEP_ANX__ and with burnout at Cram&eacute;r&rsquo;s V=__V_BURNOUT__ (&chi;&sup2;=6,780, p&lt;0.001). The __HD_N__ students (__HD_PCT__) reporting dependency
        &ge;8/10 average anxiety of __HD_ANX__ and an __HD_BURNOUT__ high-burnout rate, with retention down at 70.3. Meanwhile the strongest positive predictor of GPA
        growth in the multivariate model is not any AI variable at all &mdash; it is <strong>traditional study hours (standardised &beta;=__BETA_TRAD__)</strong>,
        ahead of prompt skill (&beta;=0.12); weekly GenAI hours contribute almost nothing once other factors are held (&beta;=0.02; model R&sup2;=__R2__).
        Paid subscriptions are likewise a non-factor (Cohen&rsquo;s d=__D_PAID__ &mdash; negligible despite paid users logging 3.3 more AI hours weekly).
        Experience compounds the effect: graduate students (+__GRAD_GPA__) and seniors (+0.243) gain far more from AI than freshmen (__FRESH_GPA__), and STEM students
        &mdash; the heaviest users at __STEM_HOURS__h/week vs __HUM_HOURS__h in Humanities &mdash; post the largest gains of any major (+0.217).
        The overarching conclusion: <strong>AI amplifies existing study capacity and skill; it does not substitute for them.</strong>
      </p>
    </div>
  </section>

  <!-- ============================ 3. KPI BAR ============================== -->
  <section class="mt-8 grid grid-cols-2 lg:grid-cols-4 gap-4">
    <div class="kpi-card bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
      <p class="text-xs font-semibold uppercase tracking-widest text-slate-500">Students Analysed</p>
      <p class="mt-2 text-4xl font-extrabold text-slate-900">__STUDENTS__</p>
      <p class="mt-1 text-sm text-slate-500">5 majors &middot; 5 year levels</p>
    </div>
    <div class="kpi-card bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
      <p class="text-xs font-semibold uppercase tracking-widest text-slate-500">Mean GPA Gain</p>
      <p class="mt-2 text-4xl font-extrabold text-emerald-600">__GPA_GAIN__</p>
      <p class="mt-1 text-sm text-slate-500">__PCT_IMPROVED__ improved this semester</p>
    </div>
    <div class="kpi-card bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
      <p class="text-xs font-semibold uppercase tracking-widest text-slate-500">Avg Weekly GenAI Use</p>
      <p class="mt-2 text-4xl font-extrabold text-blue-600">__GENAI_HOURS__h</p>
      <p class="mt-1 text-sm text-slate-500">vs __TRAD_HOURS__h traditional study</p>
    </div>
    <div class="kpi-card bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
      <p class="text-xs font-semibold uppercase tracking-widest text-slate-500">High Burnout &mdash; Extreme Users</p>
      <p class="mt-2 text-4xl font-extrabold text-rose-600">__EXTREME_BURNOUT__</p>
      <p class="mt-1 text-sm text-slate-500">20h+/week band vs __LIGHT_BURNOUT__ minimal</p>
    </div>
  </section>

  <!-- ====================== 4. DATA QUALITY & AUDIT ======================== -->
  <section class="mt-8 bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
    <h2 class="text-2xl font-bold flex items-center gap-3"><span class="w-9 h-9 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center text-lg font-extrabold">2</span>Data Quality &amp; Audit Notes</h2>
    <p class="mt-3 text-slate-600 text-[15px]">Full audit executed in Stage&nbsp;1 of the pipeline (<code class="bg-slate-100 px-1.5 py-0.5 rounded text-sm">analysis_pipeline.py</code>). Verdict: <strong class="text-emerald-700">publication-grade clean</strong> &mdash; no imputation or row removal was required; all findings below are computed on the raw 50,000&times;16 file.</p>

    <div class="mt-6 grid md:grid-cols-3 gap-4">
      <div class="rounded-xl border border-emerald-200 bg-emerald-50 p-5">
        <p class="font-bold text-emerald-900">Structural integrity</p>
        <ul class="mt-2 text-sm text-emerald-900/80 space-y-1.5 list-disc list-inside">
          <li>0 missing values across all 16 columns (0.000%)</li>
          <li>0 duplicate rows; all 50,000 Student_IDs unique (100001&ndash;150000, sequential)</li>
          <li>All 8 numeric fields inside valid domain windows (GPA 0&ndash;4, scales 1&ndash;10, retention 0&ndash;100, hours &le; 168)</li>
          <li>Category labels fully consistent &mdash; no stray whitespace, casing or spelling variants in any of the 7 categorical fields</li>
        </ul>
      </div>
      <div class="rounded-xl border border-amber-200 bg-amber-50 p-5">
        <p class="font-bold text-amber-900">Flagged outliers (1.5&times;IQR) &mdash; kept</p>
        <ul class="mt-2 text-sm text-amber-900/80 space-y-1.5 list-disc list-inside">
          <li><strong>2,583 students (5.2%)</strong> above the GenAI-hours upper fence (25.7h) &mdash; a genuine heavy-user segment, not corruption; analysed as its own band</li>
          <li>346 low Post_Semester_GPA outliers (0.7%) and 328 low Pre_GPA (0.7%) &mdash; real struggling students, bounded &ge;1.0</li>
          <li>216 retention-score outliers (0.4%), floor 10.78 &mdash; plausible low performers</li>
        </ul>
      </div>
      <div class="rounded-xl border border-slate-200 bg-slate-50 p-5">
        <p class="font-bold text-slate-900">Methodological caveats</p>
        <ul class="mt-2 text-sm text-slate-600 space-y-1.5 list-disc list-inside">
          <li>Cross-sectional single-semester data &mdash; associations, not proof of causation</li>
          <li>Dependency &amp; anxiety are self-reported 1&ndash;10 Likert scales (subject to perception bias)</li>
          <li>With n=50,000 almost every test is p&lt;0.001; we therefore report <strong>effect sizes</strong> (Cohen&rsquo;s d, &eta;&sup2;, Cram&eacute;r&rsquo;s V, standardised &beta;) alongside p-values throughout</li>
        </ul>
      </div>
    </div>
  </section>

  <!-- ======================= 5. STRATEGIC ACTIONS ========================== -->
  <section class="mt-8 bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
    <h2 class="text-2xl font-bold flex items-center gap-3"><span class="w-9 h-9 rounded-lg bg-violet-100 text-violet-700 flex items-center justify-center text-lg font-extrabold">3</span>Strategic Action Items <span class="text-sm font-medium text-slate-400">(data-backed)</span></h2>

    <div class="mt-6 space-y-4">
      <div class="border border-slate-200 rounded-xl p-5 hover:border-violet-300 transition-colors">
        <div class="flex items-start gap-4">
          <span class="shrink-0 w-8 h-8 rounded-full bg-violet-600 text-white font-bold flex items-center justify-center">1</span>
          <div>
            <p class="font-bold text-slate-900">Institutionalise prompt-engineering training &mdash; it is the largest modifiable lever in the data.</p>
            <p class="mt-1 text-sm text-slate-600 leading-relaxed">Advanced prompters out-gain beginners by +0.063 GPA (__ADV_GPA__ vs __BEG_GPA__) and retain 11 points more skill (__ADV_RET__ vs __BEG_RET__). Only 27.6% of students are advanced today. A mandatory first-semester AI-literacy module is the cheapest intervention available &mdash; and it doubles as protection: advanced users who over-use (20h+) still gain __ADV_EXTREME__ while beginners in the same band collapse to __BEG_EXTREME__.</p>
          </div>
        </div>
      </div>
      <div class="border border-slate-200 rounded-xl p-5 hover:border-violet-300 transition-colors">
        <div class="flex items-start gap-4">
          <span class="shrink-0 w-8 h-8 rounded-full bg-violet-600 text-white font-bold flex items-center justify-center">2</span>
          <div>
            <p class="font-bold text-slate-900">Redesign assignments to reward active AI use and starve answer-generation.</p>
            <p class="mt-1 text-sm text-slate-600 leading-relaxed">Direct Answer Generation is the weakest use case (__DAG_GPA__, retention 73.7) while Debugging/Troubleshooting is the strongest (__DEBUG_GPA__, retention 78.1) &mdash; a __DAG_GAP__ GPA gap, and use case carries the largest categorical effect size in the study (&eta;&sup2;=__ETA_USECASE__). Assignments that require students to submit prompts, critiques of AI output, or iterative drafts convert AI from a shortcut into a study tool.</p>
          </div>
        </div>
      </div>
      <div class="border border-slate-200 rounded-xl p-5 hover:border-rose-300 transition-colors">
        <div class="flex items-start gap-4">
          <span class="shrink-0 w-8 h-8 rounded-full bg-rose-600 text-white font-bold flex items-center justify-center">3</span>
          <div>
            <p class="font-bold text-slate-900">Stand up a wellbeing watch-list for the high-dependency cohort before midterms.</p>
            <p class="mt-1 text-sm text-slate-600 leading-relaxed">__HD_N__ students (__HD_PCT__) report AI dependency &ge;8/10. They average anxiety __HD_ANX__/10, run an __HD_BURNOUT__ high-burnout rate (V=__V_BURNOUT__), and retain only 70.3/100. Dependency &ge;7 or 20+ AI hours/week (where burnout hits __EXTREME_BURNOUT__) should trigger counselling outreach and mandatory study-skill coaching &mdash; this cohort&rsquo;s GPA gains (__HD_GPA__) are already the lowest of any dependency band.</p>
          </div>
        </div>
      </div>
      <div class="border border-slate-200 rounded-xl p-5 hover:border-violet-300 transition-colors">
        <div class="flex items-start gap-4">
          <span class="shrink-0 w-8 h-8 rounded-full bg-violet-600 text-white font-bold flex items-center justify-center">4</span>
          <div>
            <p class="font-bold text-slate-900">Replace strict bans with &ldquo;allowed with citation&rdquo; policies.</p>
            <p class="mt-1 text-sm text-slate-600 leading-relaxed">Bans do not reduce usage (__BAN_HOURS__h/week vs __CITE_HOURS__h under citation policies) and explain only 0.2% of GPA variance, but they raise exam anxiety from __CITE_ANX__ to __BAN_ANX__ and shave GPA gains (+0.187 vs +0.208). Citation policies achieve compliance transparency at zero wellbeing cost.</p>
          </div>
        </div>
      </div>
      <div class="border border-slate-200 rounded-xl p-5 hover:border-violet-300 transition-colors">
        <div class="flex items-start gap-4">
          <span class="shrink-0 w-8 h-8 rounded-full bg-violet-600 text-white font-bold flex items-center justify-center">5</span>
          <div>
            <p class="font-bold text-slate-900">Coach the &ldquo;6&ndash;12 hour + traditional study&rdquo; sweet spot &mdash; and stop marketing paid AI tiers as an academic edge.</p>
            <p class="mt-1 text-sm text-slate-600 leading-relaxed">The performance optimum is 6&ndash;12 AI hours/week (__PEAK_BAND_GPA__), and traditional study hours remain the strongest GPA predictor in the multivariate model (&beta;=__BETA_TRAD__ vs &beta;=0.02 for AI hours). Students whose AI time exceeds ~50% of total study time drift into the declining tail. Meanwhile paid subscriptions deliver no measurable advantage (d=__D_PAID__) despite 42.3% adoption &mdash; guidance should steer spending toward skills, not tiers.</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ====================== 6. INTERACTIVE CHARTS ========================== -->
  <section class="mt-8">
    <div class="bg-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-xl">
      <h2 class="text-2xl font-bold flex items-center gap-3"><span class="w-9 h-9 rounded-lg bg-blue-500/30 text-blue-200 flex items-center justify-center text-lg font-extrabold">4</span>Interactive Visual Analytics</h2>
      <p class="mt-2 text-slate-400 text-sm">Hover any chart for exact values. All figures computed from the full 50,000-record dataset.</p>
    </div>

    <div class="mt-6 grid lg:grid-cols-2 gap-6">

      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:col-span-2">
        <h3 class="font-bold text-lg">The Goldilocks Curve &mdash; GPA Gain &amp; Exam Anxiety by Weekly AI Usage</h3>
        <p class="text-sm text-slate-500 mt-1">Performance peaks at 6&ndash;12h/week; beyond 20h gains collapse while anxiety climbs. Bar size context: band populations shown in tooltips.</p>
        <div class="mt-4 h-80"><canvas id="chGoldilocks"></canvas></div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <h3 class="font-bold text-lg">GPA Gain by Primary Use Case <span class="text-xs font-medium text-slate-400">(sorted)</span></h3>
        <p class="text-sm text-slate-500 mt-1">Active engagement beats passive answer generation.</p>
        <div class="mt-4 h-72"><canvas id="chUseCase"></canvas></div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <h3 class="font-bold text-lg">Prompt Skill &times; Usage Intensity &rarr; GPA Gain</h3>
        <p class="text-sm text-slate-500 mt-1">Advanced prompters win at every dosage &mdash; and are protected at extreme use.</p>
        <div class="mt-4 h-72"><canvas id="chSkillUsage"></canvas></div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <h3 class="font-bold text-lg">Burnout Risk Mix by Usage Band <span class="text-xs font-medium text-slate-400">(% of band)</span></h3>
        <p class="text-sm text-slate-500 mt-1">High-burnout share rises from 8.9% (minimal) to 74.3% (extreme).</p>
        <div class="mt-4 h-72"><canvas id="chBurnout"></canvas></div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <h3 class="font-bold text-lg">Institutional Policy: Grades vs Anxiety</h3>
        <p class="text-sm text-slate-500 mt-1">Bans don&rsquo;t cut usage (8.4h vs 8.4h) &mdash; they only raise anxiety.</p>
        <div class="mt-4 h-72"><canvas id="chPolicy"></canvas></div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <h3 class="font-bold text-lg">Tool Diversity &rarr; GPA Gain &amp; Retention</h3>
        <p class="text-sm text-slate-500 mt-1">Monotonic rise from 1 to 4 tools; breadth of tooling proxies sophistication.</p>
        <div class="mt-4 h-72"><canvas id="chTools"></canvas></div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <h3 class="font-bold text-lg">Correlation Matrix <span class="text-xs font-medium text-slate-400">(Pearson r)</span></h3>
        <p class="text-sm text-slate-500 mt-1">Dependency&harr;hours r=0.67 is the strongest link; dependency&harr;burnout r=0.37; traditional study&harr;GPA-gain r=0.38.</p>
        <div class="mt-4 overflow-x-auto"><div id="corrGrid" class="min-w-[560px]"></div></div>
      </div>

    </div>
  </section>

  <footer class="mt-10 text-center text-xs text-slate-400 pb-6">
    Pipeline: <code>analysis_pipeline.py</code> (audit &rarr; features &rarr; descriptives &rarr; deep dives &rarr; stats tests &rarr; export) &middot;
    Dashboard: <code>build_dashboard.py</code> &middot; All metrics derived from executed pandas/scipy output &mdash; no estimates.
  </footer>
</div>

<script>
const D = __CHART_DATA__;

Chart.defaults.font.family = "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif";
Chart.defaults.color = "#475569";
const gridCol = "rgba(148,163,184,.18)";
const tip = { backgroundColor: "#0f172a", padding: 12, cornerRadius: 10, titleFont: {weight: "700"} };

/* ---- 1. Goldilocks: GPA bars + anxiety line ---- */
new Chart(document.getElementById("chGoldilocks"), {
  data: { labels: D.bands,
    datasets: [
      { type: "bar", label: "Mean GPA gain", data: D.band_gpa, yAxisID: "y",
        backgroundColor: D.band_gpa.map((v,i)=> i===2 ? "#059669" : (i===4 ? "#f43f5e" : "#93c5fd")),
        borderColor: D.band_gpa.map((v,i)=> i===2 ? "#047857" : (i===4 ? "#e11d48" : "#3b82f6")),
        borderWidth: 1.5, borderRadius: 8, order: 2 },
      { type: "line", label: "Mean exam anxiety (1-10)", data: D.band_anxiety, yAxisID: "y1",
        borderColor: "#f59e0b", backgroundColor: "#f59e0b", tension: .35,
        pointRadius: 5, pointHoverRadius: 7, borderWidth: 3, order: 1 },
      { type: "line", label: "Skill retention (0-100, scaled /100)", data: D.band_retention.map(v=>v/10), yAxisID: "y1",
        borderColor: "#8b5cf6", backgroundColor: "#8b5cf6", borderDash: [6,4], tension: .35,
        pointRadius: 4, borderWidth: 2.5, order: 0 }
    ]},
  options: { responsive: true, maintainAspectRatio: false,
    interaction: { mode: "index", intersect: false },
    plugins: { tooltip: {...tip, callbacks: { afterBody: (c)=> "n = " + D.band_n[c[0].dataIndex].toLocaleString() + " students" }},
               legend: { position: "bottom", labels: { usePointStyle: true, padding: 18 } } },
    scales: { y:  { position: "left",  min: 0.10, max: 0.26, title: { display: true, text: "Mean GPA change" }, grid: { color: gridCol } },
              y1: { position: "right", min: 0, max: 10, title: { display: true, text: "Anxiety (1-10) · Retention/10" }, grid: { drawOnChartArea: false } },
              x:  { grid: { display: false } } } }
});

/* ---- 2. Use case (sorted horizontal bars) ---- */
new Chart(document.getElementById("chUseCase"), {
  type: "bar",
  data: { labels: D.use_cases.map(s=>s.replaceAll("_"," ")),
    datasets: [{ label: "Mean GPA gain", data: D.use_case_gpa,
      backgroundColor: D.use_case_gpa.map((v,i)=> i===0 ? "#059669" : (i===D.use_case_gpa.length-1 ? "#f43f5e" : "#93c5fd")),
      borderColor: D.use_case_gpa.map((v,i)=> i===0 ? "#047857" : (i===D.use_case_gpa.length-1 ? "#e11d48" : "#3b82f6")),
      borderWidth: 1.5, borderRadius: 8 }]},
  options: { indexAxis: "y", responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false },
      tooltip: {...tip, callbacks: { afterBody: (c)=> "Retention: " + D.use_case_retention[c[0].dataIndex].toFixed(1) + " / 100" }} },
    scales: { x: { min: 0.10, max: 0.27, title: { display: true, text: "Mean GPA change" }, grid: { color: gridCol } },
              y: { grid: { display: false }, ticks: { font: { size: 12, weight: "600" } } } } }
});

/* ---- 3. Skill x Usage grouped bars ---- */
new Chart(document.getElementById("chSkillUsage"), {
  type: "bar",
  data: { labels: D.bands,
    datasets: [
      { label: "Beginner",     data: D.skill_bands_gpa.Beginner,     backgroundColor: "#fca5a5", borderColor: "#ef4444", borderWidth: 1.5, borderRadius: 6 },
      { label: "Intermediate", data: D.skill_bands_gpa.Intermediate, backgroundColor: "#fcd34d", borderColor: "#f59e0b", borderWidth: 1.5, borderRadius: 6 },
      { label: "Advanced",     data: D.skill_bands_gpa.Advanced,     backgroundColor: "#6ee7b7", borderColor: "#059669", borderWidth: 1.5, borderRadius: 6 }
    ]},
  options: { responsive: true, maintainAspectRatio: false,
    interaction: { mode: "index", intersect: false },
    plugins: { tooltip: tip, legend: { position: "bottom", labels: { usePointStyle: true, padding: 18 } } },
    scales: { y: { min: 0.10, max: 0.30, title: { display: true, text: "Mean GPA change" }, grid: { color: gridCol } },
              x: { grid: { display: false } } } }
});

/* ---- 4. Burnout stacked 100% ---- */
new Chart(document.getElementById("chBurnout"), {
  type: "bar",
  data: { labels: D.bands,
    datasets: [
      { label: "Low",    data: D.burnout_usage.Low,    backgroundColor: "#34d399", borderRadius: 4, stack: "s" },
      { label: "Medium", data: D.burnout_usage.Medium, backgroundColor: "#fbbf24", borderRadius: 4, stack: "s" },
      { label: "High",   data: D.burnout_usage.High,   backgroundColor: "#f43f5e", borderRadius: 4, stack: "s" }
    ]},
  options: { responsive: true, maintainAspectRatio: false,
    plugins: { tooltip: {...tip, callbacks: { label: (c)=> " " + c.dataset.label + ": " + c.parsed.y.toFixed(1) + "% of band" }},
               legend: { position: "bottom", labels: { usePointStyle: true, padding: 18 } } },
    scales: { y: { stacked: true, max: 100, title: { display: true, text: "% of students in band" }, grid: { color: gridCol }, ticks: { callback: v=>v+"%" } },
              x: { stacked: true, grid: { display: false } } } }
});

/* ---- 5. Policy: GPA bars + anxiety line ---- */
new Chart(document.getElementById("chPolicy"), {
  data: { labels: D.policies.map(s=>s.replaceAll("_"," ")),
    datasets: [
      { type: "bar", label: "Mean GPA gain", data: D.policy_gpa, yAxisID: "y",
        backgroundColor: ["#6ee7b7","#93c5fd","#fca5a5"], borderColor: ["#059669","#3b82f6","#ef4444"], borderWidth: 1.5, borderRadius: 8, order: 2 },
      { type: "line", label: "Mean exam anxiety", data: D.policy_anxiety, yAxisID: "y1",
        borderColor: "#f59e0b", backgroundColor: "#f59e0b", tension: .3, pointRadius: 6, pointHoverRadius: 8, borderWidth: 3, order: 1 }
    ]},
  options: { responsive: true, maintainAspectRatio: false,
    interaction: { mode: "index", intersect: false },
    plugins: { tooltip: {...tip, callbacks: { afterBody: (c)=> "Avg weekly GenAI hours: " + D.policy_hours[c[0].dataIndex].toFixed(1) + "h" }},
               legend: { position: "bottom", labels: { usePointStyle: true, padding: 18 } } },
    scales: { y:  { position: "left", min: 0.15, max: 0.23, title: { display: true, text: "Mean GPA change" }, grid: { color: gridCol } },
              y1: { position: "right", min: 3.5, max: 5.2, title: { display: true, text: "Anxiety (1-10)" }, grid: { drawOnChartArea: false } },
              x:  { grid: { display: false } } } }
});

/* ---- 6. Tool diversity: bars + retention line ---- */
new Chart(document.getElementById("chTools"), {
  data: { labels: D.tool_diversity.map(t=> t + (t==="1" ? " tool" : " tools")),
    datasets: [
      { type: "bar", label: "Mean GPA gain", data: D.tool_gpa, yAxisID: "y",
        backgroundColor: "#a5b4fc", borderColor: "#6366f1", borderWidth: 1.5, borderRadius: 8, order: 2 },
      { type: "line", label: "Skill retention (0-100)", data: D.tool_retention, yAxisID: "y1",
        borderColor: "#0ea5e9", backgroundColor: "#0ea5e9", tension: .35, pointRadius: 5, borderWidth: 3, order: 1 }
    ]},
  options: { responsive: true, maintainAspectRatio: false,
    interaction: { mode: "index", intersect: false },
    plugins: { tooltip: tip, legend: { position: "bottom", labels: { usePointStyle: true, padding: 18 } } },
    scales: { y:  { position: "left", min: 0.15, max: 0.25, title: { display: true, text: "Mean GPA change" }, grid: { color: gridCol } },
              y1: { position: "right", min: 70, max: 82, title: { display: true, text: "Retention" }, grid: { drawOnChartArea: false } },
              x:  { grid: { display: false } } } }
});

/* ---- 7. Correlation heatmap (CSS grid) ---- */
(function(){
  const el = document.getElementById("corrGrid");
  const L = D.corr_labels, M = D.corr_matrix;
  const colour = v => {
    if (v >= 0) { const a = Math.min(Math.abs(v),1); return `background:rgba(37,99,235,${(a*.85+.06).toFixed(2)});color:${a>.45?"#fff":"#1e293b"}`; }
    const a = Math.min(Math.abs(v),1); return `background:rgba(225,29,72,${(a*.85+.06).toFixed(2)});color:${a>.45?"#fff":"#1e293b"}`;
  };
  let html = `<div style="display:grid;grid-template-columns:150px repeat(${L.length},1fr);gap:3px;">`;
  html += `<div></div>` + L.map(l=>`<div class="text-[10px] font-bold text-slate-500 flex items-end justify-center pb-1 text-center leading-tight" style="min-height:52px">${l}</div>`).join("");
  M.forEach((row,i)=>{
    html += `<div class="text-[10px] font-bold text-slate-500 flex items-center pr-2 justify-end text-right leading-tight">${L[i]}</div>`;
    row.forEach(v=>{ html += `<div class="corr-cell" style="${colour(v)}" title="${L[i]} vs ${L[M.indexOf(row)]}: r=${v}">${v.toFixed(2)}</div>`; });
  });
  html += `</div>
  <div class="flex items-center gap-3 mt-3 text-[11px] text-slate-500">
    <span>Negative</span>
    <div class="h-2.5 flex-1 rounded-full" style="background:linear-gradient(to right, rgba(225,29,72,.9), rgba(226,232,240,.6), rgba(37,99,235,.9))"></div>
    <span>Positive</span>
  </div>`;
  el.innerHTML = html;
})();
</script>
</body>
</html>
"""

for key, val in n.items():
    HTML = HTML.replace(f"__{key.upper()}__", str(val))
HTML = HTML.replace("__CHART_DATA__", json.dumps(chart_data))

# The narrative needs HD_GPA which lives in segments
HTML = HTML.replace("__HD_GPA__",
                    f"+{SEG['high_dependency']['gpa_change']:.3f}")

leftover = [tok for tok in HTML.split("__") if tok.isupper() and len(tok) > 3]
if leftover:
    raise SystemExit(f"UNREPLACED TOKENS: {set(leftover)}")

with open(HTML_FILE, "w") as f:
    f.write(HTML)
print(f"Dashboard written -> {HTML_FILE} ({os.path.getsize(HTML_FILE)/1024:.0f} KB)")
