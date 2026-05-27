# Data Analysis Portfolio

A collection of end-to-end data analysis projects using Python, pandas, and interactive HTML dashboards. Each project is self-contained with raw data, analysis scripts, and a production-ready dashboard.

---

## Projects

### 1. Impact of AI on Students
**Folder:** [`Impact of AI on students/`](./Impact%20of%20AI%20on%20students/)

Analyzes how Generative AI usage affects 50,000 students across academic performance, skill retention, anxiety, and burnout. Dataset covers majors, study habits, AI tool diversity, institutional policies, and pre/post semester GPA.

- `ai_student_impact_dataset (1).csv` — 50,000 records, 16 columns
- `AI_Impact_Student_Analysis_Report.html` — Interactive executive dashboard

### 2. Shipping US — Superstore Sales Analysis
**Folder:** [`Shipping_US/`](./Shipping_US/)

Sales and shipping performance analysis for a US-based superstore with 9,800 orders. Includes regional breakdowns, category trends, and customer segment analysis.

- `train.csv` — 9,800 records, 18 columns
- `analysis.py` / `dashboard.py` / `report_pdf.py` — Python analysis scripts
- `Shipping_US.html` — Interactive HTML dashboard
- `Superstore_Sales_Analysis_Report.pdf` — PDF report with embedded charts

### 3. SuperStore
**Folder:** [`SuperStore/`](./SuperStore/)

[Details to be added after data exploration.]

---

## Master Prompt: Data Analysis & Dashboard Generation

Use the following prompt with OpenCode or any AI coding assistant to automatically analyse any CSV dataset and generate a production-ready HTML dashboard.

```
You are acting as an elite Senior Data Scientist, BI Analyst, and Full-Stack Engineer. Your goal is to conduct a rigorous, end-to-end empirical analysis of the attached dataset and output a single, production-ready interactive HTML dashboard.

You must execute this task in two distinct steps using your local execution environment:

=========================================
STEP 1: EMPIRICAL DATA AUDIT & ANALYSIS
=========================================
Before writing any HTML or text, write and execute a local Python script using `pandas` to profile the data. 

CRITICAL RULES FOR DATA SEEDING:
- Do not estimate, infer, or guess row counts, date ranges, distributions, or totals.
- All metrics, charts, and text narratives must be derived directly from the console output of your executed code.
- Check date column ranges carefully. Do not force `dayfirst=True` unless explicitly required by a min/max validity check.
- Aggregate and format the final analytical findings into an intermediate JSON structure or local variables so they can be hardcoded perfectly into the final asset.

Your data script must look for:
1. Data Audit: Shape, data types, missing value percentages, and structural anomalies (outliers, formatting errors).
2. Descriptive Statistics: Numerical summaries (mean, median, standard deviation) and categorical cardinalities.
3. Deep Dive Trends: Temporal/seasonality patterns, categorical groupings (top contributors vs risks), and key numerical correlations.

=========================================
STEP 2: HTML DASHBOARD GENERATION
=========================================
Once the data is computed, generate a single, highly polished, standalone `.html` file. You must output ONLY the complete code block starting with `<!DOCTYPE html>` and ending with `</html>`. Do not truncate code, and do not use placeholders like `// data goes here`.

Adhere to the following structural and technical specifications:

<technical_specifications>
1. Architecture: Single standalone `.html` file. No external local assets (images/CSS/JS). All scripts and styles must be embedded inline.
2. Styling: Use Tailwind CSS v4 via CDN:
   <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
   Use a modern corporate, clean light-mode palette (high-contrast white, light blues/slates, subtle accent alerts). Text must be dark and crisp (e.g., `text-slate-900`) for high readability and printing purposes.
3. Visualizations: Use Chart.js via CDN:
   <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
   Render 3-4 beautiful, responsive, interactive charts (e.g., temporal trends, sorted categorical bar charts, distributions) with rich tooltips and legends. 
4. Hardcoded Data: Hardcode your computed data structures and metrics directly into the Chart.js configs and text elements. 
</technical_specifications>

<dashboard_layout_and_narrative>
CRITICAL LAYOUT ORDER & DEPTH: The text-based analytical narrative must come first, written with extensive detail and technical rigor. All interactive visual charts must come strictly at the very bottom of the document.

The HTML page layout must follow this exact vertical sequence:
1. Header: Dashboard title, core business domain tagline, and generation timestamp.

2. Executive Summary & Core Story (Deep Dive Text): 
   - Start with a punchy 3-sentence summary of the overarching data narrative.
   - Follow with a comprehensive, multi-paragraph, deeply detailed explanation of your empirical findings. Explain *why* certain patterns exist, the operational/financial implications of the trends, and how different variables interact. Avoid surface-level summaries; make this a thorough executive-level briefing.

3. KPI Metrics Bar: 3-4 top-level aggregate metric cards highlighting totals, means, or key volumes with clean typography.

4. Data Quality & Audit Notes (Exhaustive Review): 
   - Provide a granular, transparent breakdown of the dataset's integrity based on your Step 1 script.
   - Explicitly detail missing values, systemic formatting inconsistencies, data-entry anomalies, and specific extreme outliers. Label each anomaly as either a standard business anomaly (e.g., a high-value transaction) or a data corruption error.

5. Strategic Action Items (Data-Backed): 
   - Present 3-5 highly granular, concrete, actionable business recommendations. 
   - Each item must be thoroughly explained and directly linked to specific numbers or trends uncovered in your analysis. Avoid generic or templated business advice; these must be hyper-specific to this dataset.

6. Interactive Charts Section (VISUALS LAST): 
   - Positioned at the very end of the dashboard layout. 
   - Render the 3-4 interactive Chart.js canvases here in a clean, responsive grid layout. Ensure bar charts are explicitly sorted in ascending or descending order.
</dashboard_layout_and_narrative>

Begin by executing the Step 1 Python data analysis script. Once complete, output the final HTML matching this exact sequence.
```

---

## Installing & Using OpenCode for Free

### What is OpenCode?

[OpenCode](https://opencode.ai) is a free, open-source CLI tool that brings AI coding assistants (Claude, GPT, Gemini, DeepSeek, etc.) directly into your terminal. It reads/writes files, runs commands, and executes code in your local environment — no copy-pasting.

### Installation (Windows / macOS / Linux)

#### Option 1: One-liner (Recommended)

```bash
# Windows (PowerShell)
winget install OpenCode

# macOS / Linux
curl -fsSL https://opencode.ai/install.sh | sh
```

#### Option 2: Manual Download

1. Go to [https://opencode.ai/download](https://opencode.ai/download)
2. Download the binary for your OS (Windows `.exe`, macOS `.zip`, Linux `.tar.gz`)
3. Add it to your `PATH`

#### Option 3: Using Node.js (via npm)

```bash
npm install -g @opencode/cli
```

### Getting a Free API Key

OpenCode works with multiple providers. Here are the best free/cheap options:

| Provider | Free Tier | How to Get |
|---|---|---|
| **GitHub Models** | Free with GitHub account | Go to [github.com/marketplace/models](https://github.com/marketplace/models) → Generate token |
| **Google AI Studio** | Free tier (60 req/min) | [aistudio.google.com](https://aistudio.google.com) → Get API key |
| **Anthropic** | No free tier (pay-per-use) | [console.anthropic.com](https://console.anthropic.com) |
| **OpenAI** | $5 free credit (new accounts) | [platform.openai.com](https://platform.openai.com) |

### Basic Usage

```bash
# Start a session with Claude
opencode -m claude-sonnet-4

# Run a task
opencode "Analyze this CSV and create a dashboard"

# Use with a specific provider
opencode -m gemini-2.5-pro -p google
```

For the master prompt above, run:

```bash
opencode -m claude-sonnet-4
```

Then paste the master prompt, attach your CSV file path, and OpenCode will execute the analysis and generate the HTML dashboard automatically.

---

## Best Models for Data Analysis (Free)

When running data analysis tasks with OpenCode, these models give the best results for pandas scripting and dashboard generation:

| Model | Provider | Cost | Best For |
|---|---|---|---|
| **Claude Sonnet 4** | Anthropic | ~$3/M tokens | Best overall; excellent at pandas, Chart.js, and following complex instructions |
| **Gemini 2.5 Pro** | Google | **Free tier** | Very strong at data analysis; generous free quota |
| **GPT-4o** | OpenAI | ~$2.50/M tokens | Great all-rounder; strong at code generation |
| **DeepSeek V3** | DeepSeek | **Very cheap (~$0.50/M tokens)** | Good for large datasets; cost-effective |
| **Qwen 2.5-72B** | Alibaba (via OpenRouter) | **Free** | Decent for basic analysis; good for experimentation |

### Where to Download Models for Free

For running models **locally** (no API key needed):

| Model | Size | Requirements | Download |
|---|---|---|---|
| **Llama 3.1 8B** | ~4.5 GB | 8 GB+ RAM | `ollama run llama3.1` |
| **Qwen 2.5 7B** | ~4 GB | 8 GB+ RAM | `ollama run qwen2.5` |
| **DeepSeek Coder 6.7B** | ~3.8 GB | 8 GB+ RAM | `ollama run deepseek-coder` |
| **Mistral 7B** | ~4 GB | 8 GB+ RAM | `ollama run mistral` |

**Recommended tool:** [Ollama](https://ollama.com) — one command to download and run any open-source model:

```bash
# Install Ollama (Windows/macOS/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Download and run a model
ollama pull llama3.1
ollama run llama3.1

# Use with OpenCode
opencode -m ollama/llama3.1
```

### Recommended Setup for Data Analysis

For the best balance of quality and cost:

1. **Primary:** Claude Sonnet 4 (via Anthropic API) — for complex multi-step analysis
2. **Free fallback:** Gemini 2.5 Pro (via Google AI Studio) — generous free tier
3. **Local fallback:** Llama 3.1 8B (via Ollama) — no internet needed, no cost

---

## Workflow

```bash
# 1. Clone this repo
git clone https://github.com/jamesmutegeki/Data-Analysis.git
cd Data-Analysis

# 2. Install OpenCode (one time)
winget install OpenCode   # Windows
# or: npm install -g @opencode/cli

# 3. Run analysis on any project
opencode -m claude-sonnet-4
# Then paste the master prompt and specify the CSV file

# 4. Open the generated HTML dashboard
open AI_Impact_Student_Analysis_Report.html  # macOS
start AI_Impact_Student_Analysis_Report.html  # Windows
```

---

## License

MIT — Free to use, modify, and distribute.
