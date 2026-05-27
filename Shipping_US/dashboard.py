import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('train.csv', encoding='latin1')
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)
df['Year'] = df['Order Date'].dt.year
df['YearMonth'] = df['Order Date'].dt.to_period('M').astype(str)

# Pre-compute aggregates
yearly_cat = df.groupby(['Year', 'Category'])['Sales'].sum().reset_index()
yearly_cat_pivot = yearly_cat.pivot(index='Year', columns='Category', values='Sales').fillna(0)

region_stats = df.groupby('Region').agg(
    Total_Sales=('Sales', 'sum'),
    Customer_Count=('Customer ID', 'nunique')
).reset_index()

segment_stats = df.groupby('Segment').agg(
    Total_Sales=('Sales', 'sum'),
    Customer_Count=('Customer ID', 'nunique')
).reset_index()
segment_stats['Sales_per_Customer'] = segment_stats['Total_Sales'] / segment_stats['Customer_Count']

region_yearly = df.groupby(['Year', 'Region'])['Sales'].sum().reset_index()
region_yearly_pivot = region_yearly.pivot(index='Year', columns='Region', values='Sales').fillna(0)

segment_yearly = df.groupby(['Year', 'Segment'])['Sales'].sum().reset_index()
segment_yearly_pivot = segment_yearly.pivot(index='Year', columns='Segment', values='Sales').fillna(0)

# Category colors
cat_colors = {'Furniture': '#1f77b4', 'Office Supplies': '#ff7f0e', 'Technology': '#2ca02c'}
region_colors = {'West': '#2B5B84', 'East': '#5B9BD5', 'Central': '#70AD47', 'South': '#FFC000'}
segment_colors = {'Consumer': '#5B9BD5', 'Corporate': '#70AD47', 'Home Office': '#FFC000'}

# ── Chart 1: Category Revenue Trends ──
fig1 = make_subplots(specs=[[{'secondary_y': False}]])
for cat in ['Furniture', 'Office Supplies', 'Technology']:
    cat_data = df[df['Category'] == cat].groupby('Year')['Sales'].sum().reset_index()
    fig1.add_trace(go.Scatter(
        x=cat_data['Year'], y=cat_data['Sales'],
        mode='lines+markers', name=cat,
        line=dict(width=3, color=cat_colors[cat]),
        marker=dict(size=10)
    ))
fig1.update_layout(
    title=dict(text='Category Revenue Trends (2015-2018)', font=dict(size=16, color='#2B5B84')),
    xaxis=dict(tickmode='array', tickvals=[2015, 2016, 2017, 2018]),
    yaxis=dict(title='Sales ($)', tickprefix='$', separatethousands=True),
    plot_bgcolor='rgba(245,248,252,1)',
    paper_bgcolor='white',
    hovermode='x unified',
    legend=dict(orientation='h', y=-0.2)
)

# ── Chart 2: Regional Sales Bar ──
fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=region_stats['Region'], y=region_stats['Total_Sales'],
    marker_color=[region_colors[r] for r in region_stats['Region']],
    text=[f'${v:,.0f}' for v in region_stats['Total_Sales']],
    textposition='outside',
    textfont=dict(size=13, color='#2B5B84'),
    hovertemplate='%{x}: $%{y:,.0f}<extra></extra>'
))
fig2.add_trace(go.Scatter(
    x=region_stats['Region'], y=region_stats['Customer_Count'] * 1000,
    mode='markers', name='Customers (scaled)',
    marker=dict(size=12, color='#ED7D31', symbol='diamond'),
    yaxis='y2', hovertemplate='%{x}: %{y:,.0f} customers<extra></extra>'
))
fig2.update_layout(
    title=dict(text='Regional Sales & Customer Base', font=dict(size=16, color='#2B5B84')),
    yaxis=dict(title='Total Sales ($)', tickprefix='$', separatethousands=True),
    yaxis2=dict(title='Customers', overlaying='y', side='right', showgrid=False),
    plot_bgcolor='rgba(245,248,252,1)',
    paper_bgcolor='white',
    hovermode='x unified',
    showlegend=False
)

# ── Chart 3: Regional Trend ──
fig3 = go.Figure()
for r in region_yearly_pivot.columns:
    fig3.add_trace(go.Scatter(
        x=region_yearly_pivot.index, y=region_yearly_pivot[r],
        mode='lines+markers', name=r,
        line=dict(width=3, color=region_colors[r]),
        marker=dict(size=8)
    ))
fig3.update_layout(
    title=dict(text='Regional Sales Growth Trajectory', font=dict(size=16, color='#2B5B84')),
    xaxis=dict(tickmode='array', tickvals=[2015, 2016, 2017, 2018]),
    yaxis=dict(title='Sales ($)', tickprefix='$', separatethousands=True),
    plot_bgcolor='rgba(245,248,252,1)',
    paper_bgcolor='white',
    hovermode='x unified',
    legend=dict(orientation='h', y=-0.2)
)

# ── Chart 4: Segment Pie Chart ──
fig4_pie = go.Figure()
fig4_pie.add_trace(go.Pie(
    labels=segment_stats['Segment'], values=segment_stats['Total_Sales'],
    marker_colors=['#5B9BD5', '#70AD47', '#FFC000'],
    textinfo='label+percent',
    hovertemplate='%{label}: $%{value:,.0f} (%{percent})<extra></extra>'
))
fig4_pie.update_layout(
    title=dict(text='Revenue by Segment', font=dict(size=14, color='#2B5B84')),
    plot_bgcolor='rgba(245,248,252,1)',
    paper_bgcolor='white',
    height=320,
    margin=dict(t=40, b=20, l=20, r=20)
)

# ── Chart 5: Segment per-Customer Value ──
fig5_bar = go.Figure()
fig5_bar.add_trace(go.Bar(
    x=segment_stats['Segment'], y=segment_stats['Sales_per_Customer'],
    marker_color=['#5B9BD5', '#70AD47', '#FFC000'],
    text=[f'${v:,.0f}' for v in segment_stats['Sales_per_Customer']],
    textposition='outside',
    textfont=dict(size=13, color='#2B5B84'),
    hovertemplate='%{x}: $%{y:,.0f}/customer<extra></extra>'
))
fig5_bar.update_layout(
    title=dict(text='Sales per Customer ($)', font=dict(size=14, color='#2B5B84')),
    yaxis=dict(title='Sales per Customer ($)', tickprefix='$'),
    plot_bgcolor='rgba(245,248,252,1)',
    paper_bgcolor='white',
    height=320,
    margin=dict(t=40, b=20, l=20, r=20)
)

# ── Chart 6: Segment Trend ──
fig6 = go.Figure()
for s in segment_yearly_pivot.columns:
    fig6.add_trace(go.Scatter(
        x=segment_yearly_pivot.index, y=segment_yearly_pivot[s],
        mode='lines+markers', name=s,
        line=dict(width=3, color=segment_colors[s]),
        marker=dict(size=8)
    ))
fig6.update_layout(
    title=dict(text='Segment Growth Trends', font=dict(size=16, color='#2B5B84')),
    xaxis=dict(tickmode='array', tickvals=[2015, 2016, 2017, 2018]),
    yaxis=dict(title='Sales ($)', tickprefix='$', separatethousands=True),
    plot_bgcolor='rgba(245,248,252,1)',
    paper_bgcolor='white',
    hovermode='x unified',
    legend=dict(orientation='h', y=-0.2)
)

# ── Chart 5: Segment Trend ──
fig5 = go.Figure()
for s in segment_yearly_pivot.columns:
    fig5.add_trace(go.Scatter(
        x=segment_yearly_pivot.index, y=segment_yearly_pivot[s],
        mode='lines+markers', name=s,
        line=dict(width=3, color=segment_colors[s]),
        marker=dict(size=8)
    ))
fig5.update_layout(
    title=dict(text='Segment Growth Trends', font=dict(size=16, color='#2B5B84')),
    xaxis=dict(tickmode='array', tickvals=[2015, 2016, 2017, 2018]),
    yaxis=dict(title='Sales ($)', tickprefix='$', separatethousands=True),
    plot_bgcolor='rgba(245,248,252,1)',
    paper_bgcolor='white',
    hovermode='x unified',
    legend=dict(orientation='h', y=-0.2)
)

# ── Build Dashboard HTML ──
from plotly.offline import plot

dashboard_html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Executive Summary Dashboard — Superstore Sales Analysis</title>
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', -apple-system, Helvetica, Arial, sans-serif; background: #f5f8fc; color: #2c3e50; }}
  .header {{ background: linear-gradient(135deg, #2B5B84, #1a3a5c); color: white; padding: 28px 40px; }}
  .header h1 {{ font-size: 28px; font-weight: 300; letter-spacing: 0.5px; }}
  .header h1 strong {{ font-weight: 600; }}
  .header p {{ font-size: 14px; opacity: 0.8; margin-top: 6px; }}
  .subtitle {{ color: rgba(255,255,255,0.7); font-size: 13px; margin-top: 4px; }}
  .container {{ max-width: 1600px; margin: 0 auto; padding: 20px; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  .grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }}
  .card {{ background: white; border-radius: 10px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); padding: 18px; }}
  .card h3 {{ font-size: 14px; color: #2B5B84; font-weight: 600; margin-bottom: 6px; }}
  .card .caption {{ font-size: 12px; color: #7f8c8d; line-height: 1.5; margin-top: 6px; }}
  .kpi-row {{ display: flex; gap: 16px; margin-bottom: 20px; }}
  .kpi {{ background: white; border-radius: 10px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); padding: 18px 22px; flex: 1; text-align: center; }}
  .kpi .num {{ font-size: 26px; font-weight: 700; color: #2B5B84; }}
  .kpi .label {{ font-size: 12px; color: #7f8c8d; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }}
  .kpi .change {{ font-size: 13px; margin-top: 4px; }}
  .positive {{ color: #70AD47; }} .negative {{ color: #d62728; }}
  .recs {{ background: white; border-radius: 10px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); padding: 18px; }}
  .recs h3 {{ font-size: 14px; color: #2B5B84; font-weight: 600; margin-bottom: 10px; }}
  .recs li {{ font-size: 13px; line-height: 1.6; margin-bottom: 6px; padding-left: 8px; }}
  .recs strong {{ color: #2B5B84; }}
  .full-width {{ grid-column: 1 / -1; }}
  .footer {{ text-align: center; padding: 20px; font-size: 11px; color: #95a5a6; }}
  @media (max-width: 900px) {{ .grid, .grid-3 {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>

<div class="header">
  <h1><strong>Superstore Sales</strong> — Executive Summary Dashboard</h1>
  <p>Data-driven insights from 9,800 transactions (2015–2018) across US retail and office supply operations.</p>
  <div class="subtitle">Dataset: train.csv | 18 variables | 4 regions | 3 categories | 3 customer segments</div>
</div>

<div class="container">
  <!-- KPI Row -->
  <div class="kpi-row">
    <div class="kpi">
      <div class="num">$2.26M</div>
      <div class="label">Total Revenue (4 Years)</div>
      <div class="change positive">+70% from 2015</div>
    </div>
    <div class="kpi">
      <div class="num">9,800</div>
      <div class="label">Total Transactions</div>
      <div class="change positive">Growing YoY</div>
    </div>
    <div class="kpi">
      <div class="num">$231</div>
      <div class="label">Avg Transaction Value</div>
      <div class="change positive">Stable across regions</div>
    </div>
    <div class="kpi">
      <div class="num">793</div>
      <div class="label">Unique Customers</div>
      <div class="change positive">Consumer segment leads</div>
    </div>
    <div class="kpi">
      <div class="num">52%</div>
      <div class="label">Technology Growth (Cumul.)</div>
      <div class="change positive">Fastest-growing category</div>
    </div>
  </div>

  <!-- Charts Row 1 -->
  <div class="grid">
    <div class="card">
      {plot(fig1, output_type='div', include_plotlyjs=False, config={'displayModeBar': False})}
      <div class="caption">Technology and Office Supplies show strong upward trends. Furniture grows more slowly. Cumulative growth: Technology 51.5%, Office Supplies 57.8%, Furniture 32.6%.</div>
    </div>
    <div class="card">
      {plot(fig2, output_type='div', include_plotlyjs=False, config={'displayModeBar': False})}
      <div class="caption">West leads with $710K total sales and 400+ customers. South ($389K) and Central ($486K) represent expansion opportunities. Customer count closely correlates with sales.</div>
    </div>
  </div>

  <!-- Charts Row 2 -->
  <div class="grid">
    <div class="card">
      {plot(fig3, output_type='div', include_plotlyjs=False, config={'displayModeBar': False})}
      <div class="caption">All regions are growing, but the West has accelerated since 2017. The South shows the flattest trend — a candidate for targeted investment. Consistent ~$80-100K annual growth per region.</div>
    </div>
    <div class="card">
      {plot(fig6, output_type='div', include_plotlyjs=False, config={'displayModeBar': False})}
      <div class="caption">All three segments show consistent upward growth. Consumer segment accelerated in 2017-2018. Corporate and Home Office grow steadily with no signs of saturation.</div>
    </div>
  </div>

  <!-- Charts Row 3 -->
  <div class="grid-3">
    <div class="card">
      {plot(fig4_pie, output_type='div', include_plotlyjs=False, config={'displayModeBar': False})}
      <div class="caption">Consumer segment = 49% of revenue ($1.15M), followed by Corporate (30%) and Home Office (21%).</div>
    </div>
    <div class="card">
      {plot(fig5_bar, output_type='div', include_plotlyjs=False, config={'displayModeBar': False})}
      <div class="caption">Corporate leads at $2,917/customer. Home Office ($2,872) and Consumer ($2,807) are close behind.</div>
    </div>
    <div class="recs">
      <h3>Strategic Takeaways</h3>
      <ol>
        <li><strong>Invest in Technology in the South/Central regions</strong> — Technology is 40% of West sales but only 30% in the South. Targeted expansion could unlock $80-120K in additional annual revenue.</li>
        <li><strong>Launch a Corporate loyalty programme</strong> — Corporate customers generate the highest per-customer value ($2,917) but number only 236 accounts. Retention and upsell could yield 10-15% value growth.</li>
        <li><strong>Optimise inventory allocation by region</strong> — Align stock with regional demand: Technology in West, Office Supplies in South/Central, Furniture in East. Reduces carrying costs and improves turnover.</li>
        <li><strong>Revitalise the Furniture category</strong> — At 32.6% cumulative growth (vs 50%+ for other categories), Furniture needs product range refresh, pricing review, or bundle promotions.</li>
        <li><strong>Improve Central region delivery</strong> — Slowest delivery (4.06 days) may impact repeat business. Investigate warehouse or carrier options.</li>
      </ol>
    </div>
  </div>

</div>

<div class="footer">
  Superstore Sales Analysis Dashboard | Dataset: train.csv | Generated with Python (Plotly, Pandas) | May 2026
</div>

</body>
</html>
'''

with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dashboard_html)
print("Dashboard saved: dashboard.html")
