#!/usr/bin/env python3
"""
=============================================================================
DATA ANALYSIS PIPELINE — Impact of Generative AI on Students
=============================================================================
Dataset : ai_student_impact_dataset (1).csv  (50,000 students x 16 columns)
Author  : Arena.ai Agent Mode
Stages  :
    1. Ingestion & Data Audit        (shape, dtypes, missing, dupes, outliers)
    2. Cleaning & Feature Engineering (GPA change, usage bands, ordinals)
    3. Descriptive Statistics
    4. Deep-Dive Analyses (7 analyses)
    5. Statistical Testing (correlations, ANOVA, t-tests, chi-square,
       with effect sizes)
    6. Export  -> pipeline_outputs/analysis_results.json + summary CSVs

Run:  python analysis_pipeline.py
=============================================================================
"""

import json
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "ai_student_impact_dataset (1).csv")
OUT_DIR = os.path.join(BASE_DIR, "pipeline_outputs")
os.makedirs(OUT_DIR, exist_ok=True)

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)

RESULTS: dict = {"meta": {}, "audit": {}, "descriptives": {}, "analyses": {},
                 "stats_tests": {}}


def banner(title: str) -> None:
    print("\n" + "=" * 78)
    print(f"  {title}")
    print("=" * 78)


def subsection(title: str) -> None:
    print(f"\n--- {title} " + "-" * max(0, 70 - len(title)))


def r(x, nd=4):
    """Round safely for JSON export."""
    if x is None or (isinstance(x, float) and (np.isnan(x) or np.isinf(x))):
        return None
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return round(float(x), nd)
    return x


# ============================================================================
# STAGE 1 — INGESTION & DATA AUDIT
# ============================================================================
banner("STAGE 1 — INGESTION & DATA AUDIT")

df = pd.read_csv(DATA_FILE)
print(f"Loaded: {os.path.basename(DATA_FILE)}")
print(f"Shape : {df.shape[0]:,} rows x {df.shape[1]} columns")

RESULTS["meta"] = {
    "source_file": os.path.basename(DATA_FILE),
    "rows": int(df.shape[0]),
    "cols": int(df.shape[1]),
    "columns": list(df.columns),
}

subsection("1.1 Schema & dtypes")
dtypes = {c: str(t) for c, t in df.dtypes.items()}
for c, t in dtypes.items():
    print(f"  {c:<28} {t}")
RESULTS["audit"]["dtypes"] = dtypes

subsection("1.2 Missing values")
missing = df.isna().sum()
missing_pct = (missing / len(df) * 100).round(3)
miss_tbl = pd.DataFrame({"missing": missing, "pct": missing_pct})
print(miss_tbl[miss_tbl["missing"] > 0] if miss_tbl["missing"].sum() else
      "  No missing values in any column.")
RESULTS["audit"]["missing"] = {c: {"count": int(missing[c]),
                                   "pct": float(missing_pct[c])}
                               for c in df.columns}
RESULTS["audit"]["total_missing"] = int(missing.sum())

subsection("1.3 Duplicates")
dup_rows = int(df.duplicated().sum())
dup_ids = int(df["Student_ID"].duplicated().sum())
print(f"  Fully duplicated rows     : {dup_rows}")
print(f"  Duplicated Student_IDs    : {dup_ids}")
RESULTS["audit"]["duplicate_rows"] = dup_rows
RESULTS["audit"]["duplicate_ids"] = dup_ids

subsection("1.4 Categorical cardinalities")
cat_cols = ["Major_Category", "Year_of_Study", "Primary_Use_Case",
            "Prompt_Engineering_Skill", "Institutional_Policy",
            "Burnout_Risk_Level", "Paid_Subscription"]
card = {}
for c in cat_cols:
    vc = df[c].value_counts()
    card[c] = {"n_unique": int(df[c].nunique()),
               "counts": {str(k): int(v) for k, v in vc.items()}}
    print(f"  {c:<26} {df[c].nunique()} unique -> {dict(vc)}")
RESULTS["audit"]["cardinality"] = card

subsection("1.5 Range / validity checks")
range_checks = {
    "Pre_Semester_GPA": (0.0, 4.0),
    "Post_Semester_GPA": (0.0, 4.0),
    "Weekly_GenAI_Hours": (0.0, 168.0),
    "Traditional_Study_Hours": (0.0, 168.0),
    "Tool_Diversity": (0, 20),
    "Perceived_AI_Dependency": (1, 10),
    "Anxiety_Level_During_Exams": (1, 10),
    "Skill_Retention_Score": (0.0, 100.0),
}
violations = {}
for c, (lo, hi) in range_checks.items():
    bad = int(((df[c] < lo) | (df[c] > hi)).sum())
    violations[c] = bad
    print(f"  {c:<28} range [{df[c].min():>7.2f}, {df[c].max():>7.2f}] "
          f"valid window [{lo}, {hi}]  violations: {bad}")
RESULTS["audit"]["range_violations"] = violations

subsection("1.6 Outlier scan (1.5x IQR rule)")
outliers = {}
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
num_cols.remove("Student_ID")
for c in num_cols:
    q1, q3 = df[c].quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    n_out = int(((df[c] < lo) | (df[c] > hi)).sum())
    outliers[c] = {"n": n_out, "pct": round(n_out / len(df) * 100, 2),
                   "lower_fence": r(lo, 2), "upper_fence": r(hi, 2)}
    print(f"  {c:<28} outliers: {n_out:>5} ({n_out/len(df)*100:5.2f}%) "
          f"fences [{lo:8.2f}, {hi:8.2f}]")
RESULTS["audit"]["outliers_iqr"] = outliers


# ============================================================================
# STAGE 2 — CLEANING & FEATURE ENGINEERING
# ============================================================================
banner("STAGE 2 — CLEANING & FEATURE ENGINEERING")

# Dataset is clean (no missing/dupes/range violations) -> work on a copy.
d = df.copy()

# 2.1 Core engineered outcome: GPA change over the semester
d["GPA_Change"] = d["Post_Semester_GPA"] - d["Pre_Semester_GPA"]
d["GPA_Change_Pct"] = np.where(d["Pre_Semester_GPA"] > 0,
                               d["GPA_Change"] / d["Pre_Semester_GPA"] * 100,
                               np.nan)
print("Feature: GPA_Change = Post_Semester_GPA - Pre_Semester_GPA")

# 2.2 AI usage intensity bands (hours per week)
bins = [-0.001, 2, 6, 12, 20, np.inf]
labels = ["Minimal (0-2h)", "Light (2-6h)", "Moderate (6-12h)",
          "Heavy (12-20h)", "Extreme (20h+)"]
d["AI_Usage_Band"] = pd.cut(d["Weekly_GenAI_Hours"], bins=bins, labels=labels)
band_counts = d["AI_Usage_Band"].value_counts().reindex(labels)
print("Feature: AI_Usage_Band")
for k, v in band_counts.items():
    print(f"    {k:<18} {v:>6} ({v/len(d)*100:5.1f}%)")
RESULTS["descriptives"]["usage_band_counts"] = {str(k): int(v)
                                                for k, v in band_counts.items()}

# 2.3 Ordinal encodings
skill_map = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
burnout_map = {"Low": 1, "Medium": 2, "High": 3}
d["Skill_Ord"] = d["Prompt_Engineering_Skill"].map(skill_map)
d["Burnout_Ord"] = d["Burnout_Risk_Level"].map(burnout_map)

# 2.4 Dependency bands for wellbeing analysis
d["Dependency_Band"] = pd.cut(d["Perceived_AI_Dependency"],
                              bins=[0, 3, 6, 10],
                              labels=["Low (1-3)", "Medium (4-6)", "High (7-10)"])

# 2.5 Study displacement: share of total study time that is AI-assisted
d["Total_Study_Time"] = d["Weekly_GenAI_Hours"] + d["Traditional_Study_Hours"]
d["AI_Time_Share"] = np.where(d["Total_Study_Time"] > 0,
                              d["Weekly_GenAI_Hours"] / d["Total_Study_Time"] * 100,
                              np.nan)

improved = int((d["GPA_Change"] > 0).sum())
declined = int((d["GPA_Change"] < 0).sum())
flat = int((d["GPA_Change"] == 0).sum())
print(f"\nGPA trajectory: improved {improved:,} ({improved/len(d)*100:.1f}%) | "
      f"declined {declined:,} ({declined/len(d)*100:.1f}%) | flat {flat:,}")
RESULTS["descriptives"]["gpa_trajectory"] = {
    "improved": improved, "declined": declined, "flat": flat,
    "improved_pct": r(improved / len(d) * 100, 1),
    "declined_pct": r(declined / len(d) * 100, 1)}


# ============================================================================
# STAGE 3 — DESCRIPTIVE STATISTICS
# ============================================================================
banner("STAGE 3 — DESCRIPTIVE STATISTICS")

subsection("3.1 Numeric summary")
desc = d[["Pre_Semester_GPA", "Post_Semester_GPA", "GPA_Change",
          "Weekly_GenAI_Hours", "Traditional_Study_Hours", "AI_Time_Share",
          "Tool_Diversity", "Perceived_AI_Dependency",
          "Anxiety_Level_During_Exams", "Skill_Retention_Score"]].describe().T
desc["median"] = d[desc.index].median()
print(desc.round(3).to_string())
RESULTS["descriptives"]["numeric"] = {
    c: {k: r(v, 4) for k, v in desc.loc[c].items()} for c in desc.index}

subsection("3.2 Headline KPIs")
kpis = {
    "n_students": int(len(d)),
    "mean_pre_gpa": r(d["Pre_Semester_GPA"].mean(), 3),
    "mean_post_gpa": r(d["Post_Semester_GPA"].mean(), 3),
    "mean_gpa_change": r(d["GPA_Change"].mean(), 4),
    "pct_improved": r((d["GPA_Change"] > 0).mean() * 100, 1),
    "mean_genai_hours": r(d["Weekly_GenAI_Hours"].mean(), 2),
    "median_genai_hours": r(d["Weekly_GenAI_Hours"].median(), 2),
    "mean_traditional_hours": r(d["Traditional_Study_Hours"].mean(), 2),
    "mean_retention": r(d["Skill_Retention_Score"].mean(), 2),
    "mean_anxiety": r(d["Anxiety_Level_During_Exams"].mean(), 2),
    "high_burnout_pct": r((d["Burnout_Risk_Level"] == "High").mean() * 100, 1),
    "paid_sub_pct": r(d["Paid_Subscription"].mean() * 100, 1),
    "mean_dependency": r(d["Perceived_AI_Dependency"].mean(), 2),
}
for k, v in kpis.items():
    print(f"  {k:<26} {v}")
RESULTS["descriptives"]["kpis"] = kpis


# ============================================================================
# STAGE 4 — DEEP-DIVE ANALYSES
# ============================================================================
banner("STAGE 4 — DEEP-DIVE ANALYSES")

OUTCOMES = ["GPA_Change", "Post_Semester_GPA", "Skill_Retention_Score",
            "Anxiety_Level_During_Exams", "Weekly_GenAI_Hours",
            "Perceived_AI_Dependency"]


def group_table(frame, by, metrics, order=None):
    """Groupby mean + count, reordered, rounded — returns (df, dict)."""
    g = frame.groupby(by, observed=True).agg(
        n=("Student_ID", "count"),
        **{m: (m, "mean") for m in metrics})
    if order:
        g = g.reindex(order)
    g = g.dropna(how="all")
    out = {str(idx): {"n": int(row["n"]),
                      **{m: r(row[m], 4) for m in metrics}}
           for idx, row in g.iterrows()}
    return g.round(3), out


# --- 4.1 GPA change across AI usage intensity bands -------------------------
subsection("4.1 GPA change by AI usage intensity band")
t, res = group_table(d, "AI_Usage_Band",
                     ["GPA_Change", "Post_Semester_GPA",
                      "Skill_Retention_Score", "Anxiety_Level_During_Exams",
                      "Traditional_Study_Hours", "Perceived_AI_Dependency"],
                     order=labels)
print(t.to_string())
RESULTS["analyses"]["gpa_by_usage_band"] = res

# --- 4.2 Primary use case effectiveness -------------------------------------
subsection("4.2 Outcomes by primary AI use case")
t, res = group_table(d, "Primary_Use_Case",
                     ["GPA_Change", "Post_Semester_GPA",
                      "Skill_Retention_Score", "Anxiety_Level_During_Exams",
                      "Weekly_GenAI_Hours"])
t = t.sort_values("GPA_Change", ascending=False)
res = {str(k): v for k, v in
       sorted(res.items(), key=lambda kv: -(kv[1]["GPA_Change"] or -9))}
print(t.to_string())
RESULTS["analyses"]["by_use_case"] = res

# --- 4.3 Prompt-engineering skill -------------------------------------------
subsection("4.3 Outcomes by prompt-engineering skill")
skill_order = ["Beginner", "Intermediate", "Advanced"]
t, res = group_table(d, "Prompt_Engineering_Skill",
                     ["GPA_Change", "Skill_Retention_Score",
                      "Anxiety_Level_During_Exams", "Weekly_GenAI_Hours",
                      "Perceived_AI_Dependency"], order=skill_order)
print(t.to_string())
RESULTS["analyses"]["by_skill"] = res

# Skill moderates the hours effect? (interaction)
subsection("4.3b Interaction: skill x usage band -> GPA change")
pivot = d.pivot_table(index="AI_Usage_Band", columns="Prompt_Engineering_Skill",
                      values="GPA_Change", aggfunc="mean", observed=True)
pivot = pivot.reindex(index=labels, columns=skill_order)
print(pivot.round(4).to_string())
RESULTS["analyses"]["skill_x_usage_gpa"] = {
    str(band): {str(sk): r(pivot.loc[band, sk], 4) for sk in skill_order}
    for band in labels}

# --- 4.4 Tool diversity ------------------------------------------------------
subsection("4.4 Outcomes by number of AI tools used")
t, res = group_table(d, "Tool_Diversity",
                     ["GPA_Change", "Skill_Retention_Score",
                      "Anxiety_Level_During_Exams"])
print(t.to_string())
RESULTS["analyses"]["by_tool_diversity"] = res

# --- 4.5 Institutional policy -------------------------------------------------
subsection("4.5 Outcomes by institutional AI policy")
t, res = group_table(d, "Institutional_Policy",
                     ["GPA_Change", "Weekly_GenAI_Hours",
                      "Skill_Retention_Score", "Anxiety_Level_During_Exams",
                      "Perceived_AI_Dependency"])
print(t.to_string())
RESULTS["analyses"]["by_policy"] = res

# --- 4.6 Wellbeing: dependency -> anxiety & burnout ---------------------------
subsection("4.6 Wellbeing by perceived AI dependency band")
dep_order = ["Low (1-3)", "Medium (4-6)", "High (7-10)"]
t, res = group_table(d, "Dependency_Band",
                     ["Anxiety_Level_During_Exams", "GPA_Change",
                      "Skill_Retention_Score", "Weekly_GenAI_Hours"],
                     order=dep_order)
print(t.to_string())
RESULTS["analyses"]["by_dependency"] = res

subsection("4.6b Burnout risk distribution by dependency band")
ct = pd.crosstab(d["Dependency_Band"], d["Burnout_Risk_Level"],
                 normalize="index") * 100
ct = ct.reindex(index=dep_order, columns=["Low", "Medium", "High"])
print(ct.round(2).to_string())
RESULTS["analyses"]["burnout_by_dependency"] = {
    str(idx): {str(c): r(ct.loc[idx, c], 2) for c in ct.columns}
    for idx in ct.index}

subsection("4.6c Burnout risk by usage band")
ct2 = pd.crosstab(d["AI_Usage_Band"], d["Burnout_Risk_Level"],
                  normalize="index") * 100
ct2 = ct2.reindex(index=labels, columns=["Low", "Medium", "High"])
print(ct2.round(2).to_string())
RESULTS["analyses"]["burnout_by_usage"] = {
    str(idx): {str(c): r(ct2.loc[idx, c], 2) for c in ct2.columns}
    for idx in ct2.index}

# --- 4.7 Demographics: major & year -------------------------------------------
subsection("4.7 Outcomes by major")
t, res = group_table(d, "Major_Category",
                     ["GPA_Change", "Weekly_GenAI_Hours",
                      "Skill_Retention_Score", "Anxiety_Level_During_Exams"])
print(t.to_string())
RESULTS["analyses"]["by_major"] = res

subsection("4.7b Outcomes by year of study")
year_order = ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"]
t, res = group_table(d, "Year_of_Study",
                     ["GPA_Change", "Weekly_GenAI_Hours",
                      "Anxiety_Level_During_Exams"], order=year_order)
print(t.to_string())
RESULTS["analyses"]["by_year"] = res

# --- 4.8 Paid vs free ----------------------------------------------------------
subsection("4.8 Paid subscription vs free users")
t, res = group_table(d, "Paid_Subscription",
                     ["GPA_Change", "Weekly_GenAI_Hours",
                      "Tool_Diversity", "Skill_Retention_Score"])
t.index = t.index.map({True: "Paid", False: "Free"})
res = {("Paid" if k == "True" else "Free"): v for k, v in res.items()}
print(t.to_string())
RESULTS["analyses"]["paid_vs_free"] = res

# --- 4.9 Correlation matrix ----------------------------------------------------
subsection("4.9 Correlation matrix (Pearson)")
corr_cols = ["Weekly_GenAI_Hours", "Traditional_Study_Hours", "Skill_Ord",
             "Tool_Diversity", "Perceived_AI_Dependency",
             "Anxiety_Level_During_Exams", "Burnout_Ord",
             "Pre_Semester_GPA", "Post_Semester_GPA", "GPA_Change",
             "Skill_Retention_Score"]
corr = d[corr_cols].corr()
print(corr.round(3).to_string())
RESULTS["analyses"]["correlation_matrix"] = {
    c: {c2: r(corr.loc[c, c2], 4) for c2 in corr.columns} for c in corr.index}


# ============================================================================
# STAGE 5 — STATISTICAL TESTS (p-values + effect sizes)
# ============================================================================
banner("STAGE 5 — STATISTICAL TESTING")


def cohens_d(a, b):
    na, nb = len(a), len(b)
    pooled = np.sqrt(((na - 1) * a.std(ddof=1) + (nb - 1) * b.std(ddof=1))
                     / (na + nb - 2))
    return (a.mean() - b.mean()) / pooled if pooled else np.nan


def eta_squared(frame, group_col, val_col):
    groups = [g[val_col].values for _, g in frame.groupby(group_col,
                                                          observed=True)]
    grand = frame[val_col].mean()
    ss_between = sum(len(g) * (g.mean() - grand) ** 2 for g in groups)
    ss_total = ((frame[val_col] - grand) ** 2).sum()
    return ss_between / ss_total if ss_total else np.nan


def cramers_v(table):
    chi2 = stats.chi2_contingency(table)[0]
    n = table.values.sum()
    k = min(table.shape) - 1
    return np.sqrt(chi2 / (n * k)) if k else np.nan


tests = {}


def record(name, **kw):
    tests[name] = {k: r(v, 6) if isinstance(v, float) else v
                   for k, v in kw.items()}
    line = ", ".join(f"{k}={v}" for k, v in tests[name].items())
    print(f"  {name:<46} {line}")


subsection("5.1 Correlations with p-values")
for a, b in [("Weekly_GenAI_Hours", "GPA_Change"),
             ("Weekly_GenAI_Hours", "Skill_Retention_Score"),
             ("Weekly_GenAI_Hours", "Anxiety_Level_During_Exams"),
             ("Weekly_GenAI_Hours", "Traditional_Study_Hours"),
             ("Perceived_AI_Dependency", "Anxiety_Level_During_Exams"),
             ("Perceived_AI_Dependency", "Burnout_Ord"),
             ("Perceived_AI_Dependency", "GPA_Change"),
             ("Skill_Ord", "GPA_Change"),
             ("Tool_Diversity", "GPA_Change"),
             ("Traditional_Study_Hours", "GPA_Change"),
             ("GPA_Change", "Skill_Retention_Score"),
             ("Anxiety_Level_During_Exams", "Post_Semester_GPA")]:
    pr, pp = stats.pearsonr(d[a], d[b])
    sr, sp = stats.spearmanr(d[a], d[b])
    record(f"{a} vs {b}", pearson_r=pr, pearson_p=pp,
           spearman_r=sr, spearman_p=sp)

subsection("5.2 One-way ANOVA + eta-squared")
for col, label in [("AI_Usage_Band", "usage band"),
                   ("Primary_Use_Case", "use case"),
                   ("Prompt_Engineering_Skill", "skill"),
                   ("Institutional_Policy", "policy"),
                   ("Dependency_Band", "dependency (anxiety outcome)")]:
    val = "Anxiety_Level_During_Exams" if "anxiety" in label else "GPA_Change"
    groups = [g[val].values for _, g in d.groupby(col, observed=True)]
    F, p = stats.f_oneway(*groups)
    eta2 = eta_squared(d, col, val)
    record(f"ANOVA {val} ~ {label}", F=F, p=p, eta_squared=eta2,
           n_groups=len(groups))

subsection("5.3 t-test: paid vs free (GPA change)")
paid = d.loc[d["Paid_Subscription"], "GPA_Change"]
free = d.loc[~d["Paid_Subscription"], "GPA_Change"]
tstat, p = stats.ttest_ind(paid, free, equal_var=False)
record("paid_vs_free_gpa_change", t=tstat, p=p,
       cohens_d=cohens_d(paid, free),
       mean_paid=paid.mean(), mean_free=free.mean())

subsection("5.4 t-test: extreme vs minimal users (GPA change)")
extreme = d.loc[d["AI_Usage_Band"] == "Extreme (20h+)", "GPA_Change"]
minimal = d.loc[d["AI_Usage_Band"] == "Minimal (0-2h)", "GPA_Change"]
tstat, p = stats.ttest_ind(extreme, minimal, equal_var=False)
record("extreme_vs_minimal_gpa_change", t=tstat, p=p,
       cohens_d=cohens_d(extreme, minimal),
       mean_extreme=extreme.mean(), mean_minimal=minimal.mean())

subsection("5.5 Chi-square: dependency band x burnout level")
table = pd.crosstab(d["Dependency_Band"], d["Burnout_Risk_Level"])
chi2, p, dof, _ = stats.chi2_contingency(table)
record("chi2_dependency_x_burnout", chi2=chi2, p=p, dof=int(dof),
       cramers_v=cramers_v(table))

subsection("5.6 Chi-square: policy x burnout level")
table2 = pd.crosstab(d["Institutional_Policy"], d["Burnout_Risk_Level"])
chi2, p, dof, _ = stats.chi2_contingency(table2)
record("chi2_policy_x_burnout", chi2=chi2, p=p, dof=int(dof),
       cramers_v=cramers_v(table2))

subsection("5.7 OLS-style multiple regression (numpy lstsq, standardised)")
feats = ["Weekly_GenAI_Hours", "Traditional_Study_Hours", "Skill_Ord",
         "Tool_Diversity", "Perceived_AI_Dependency",
         "Anxiety_Level_During_Exams", "Pre_Semester_GPA"]
X = d[feats].values
y = d["GPA_Change"].values
Xz = (X - X.mean(0)) / X.std(0)
yz = (y - y.mean()) / y.std()
Xz = np.column_stack([np.ones(len(Xz)), Xz])
beta, *_ = np.linalg.lstsq(Xz, yz, rcond=None)
yhat = Xz @ beta
r2 = 1 - ((yz - yhat) ** 2).sum() / ((yz - yz.mean()) ** 2).sum()
print(f"  R^2 = {r2:.4f}")
for name, b in zip(["Intercept"] + feats, beta):
    print(f"    beta[{name:<28}] = {b:+.4f}")
tests["regression_gpa_change"] = {
    "r_squared": r(r2, 4),
    "standardised_betas": {f: r(b, 4) for f, b in zip(feats, beta[1:])}}

RESULTS["stats_tests"] = tests

# --- Segment spotlight: who wins / who loses ---------------------------------
banner("SEGMENT SPOTLIGHTS")
seg = {}

best_skill = max(RESULTS["analyses"]["by_skill"].items(),
                 key=lambda kv: kv[1]["GPA_Change"])
seg["advanced_gpa_gain"] = best_skill[1]["GPA_Change"]
print(f"Advanced prompters mean GPA change: {best_skill[1]['GPA_Change']:+.4f}")

heavy = d[d["Weekly_GenAI_Hours"] >= 20]
light = d[d["Weekly_GenAI_Hours"] <= 2]
seg["heavy"] = {"n": len(heavy), "gpa_change": r(heavy["GPA_Change"].mean()),
                "anxiety": r(heavy["Anxiety_Level_During_Exams"].mean()),
                "retention": r(heavy["Skill_Retention_Score"].mean()),
                "burnout_high_pct": r((heavy["Burnout_Risk_Level"] == "High")
                                      .mean() * 100, 1)}
seg["light"] = {"n": len(light), "gpa_change": r(light["GPA_Change"].mean()),
                "anxiety": r(light["Anxiety_Level_During_Exams"].mean()),
                "retention": r(light["Skill_Retention_Score"].mean()),
                "burnout_high_pct": r((light["Burnout_Risk_Level"] == "High")
                                      .mean() * 100, 1)}
print(f"Heavy users (20h+/wk) n={len(heavy):,}: GPA {seg['heavy']['gpa_change']:+.4f}, "
      f"anxiety {seg['heavy']['anxiety']}, high-burnout {seg['heavy']['burnout_high_pct']}%")
print(f"Light users (<=2h/wk) n={len(light):,}: GPA {seg['light']['gpa_change']:+.4f}, "
      f"anxiety {seg['light']['anxiety']}, high-burnout {seg['light']['burnout_high_pct']}%")

# High-dependency cohort
hd = d[d["Perceived_AI_Dependency"] >= 8]
seg["high_dependency"] = {
    "n": len(hd), "pct": r(len(hd) / len(d) * 100, 1),
    "anxiety": r(hd["Anxiety_Level_During_Exams"].mean()),
    "burnout_high_pct": r((hd["Burnout_Risk_Level"] == "High").mean() * 100, 1),
    "gpa_change": r(hd["GPA_Change"].mean())}
print(f"High dependency (>=8/10) n={len(hd):,} ({seg['high_dependency']['pct']}%): "
      f"anxiety {seg['high_dependency']['anxiety']}, "
      f"high-burnout {seg['high_dependency']['burnout_high_pct']}%")

RESULTS["segments"] = seg


# ============================================================================
# STAGE 6 — EXPORT
# ============================================================================
banner("STAGE 6 — EXPORT")

json_path = os.path.join(OUT_DIR, "analysis_results.json")
with open(json_path, "w") as f:
    json.dump(RESULTS, f, indent=2, default=str)
print(f"JSON results      -> {json_path}")

d.to_csv(os.path.join(OUT_DIR, "students_enriched.csv"), index=False)
print(f"Enriched dataset  -> {OUT_DIR}/students_enriched.csv")

for name, key in [("summary_usage_band.csv", "gpa_by_usage_band"),
                  ("summary_use_case.csv", "by_use_case"),
                  ("summary_skill.csv", "by_skill"),
                  ("summary_policy.csv", "by_policy"),
                  ("summary_dependency.csv", "by_dependency"),
                  ("summary_major.csv", "by_major"),
                  ("summary_tool_diversity.csv", "by_tool_diversity")]:
    pd.DataFrame(RESULTS["analyses"][key]).T.to_csv(
        os.path.join(OUT_DIR, name))
    print(f"Summary table     -> {OUT_DIR}/{name}")

banner("PIPELINE COMPLETE")
print(f"All outputs in: {OUT_DIR}")
