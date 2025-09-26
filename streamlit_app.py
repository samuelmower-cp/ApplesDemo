import streamlit as st
import pandas as pd
from datetime import timedelta
import altair as alt


st.title("🍎 Stremlit in Conduit")
st.write(
    "Testing how to run a Stremlit app in CP Conduit"
)




# Read CSV
df = pd.read_csv("Apples.csv")
df.columns = [col.title() for col in df.columns]

# Process Periods
df['Periods'] = pd.to_datetime(df['Periods'].astype(str).str[-8:], format='%m/%d/%y')
df['Organic'] = df['Organic Claim'].apply(lambda x: 'CNV' if 'NOT' in str(x) else 'ORG')

# Latest date
max_date = df['Periods'].max()
latest_date_str = max_date.strftime("%-m/%-d/%y")

# Pre-calc periods
recent_4 = max_date - timedelta(weeks=4)
recent_13 = max_date - timedelta(weeks=13)
recent_26 = max_date - timedelta(weeks=26)
recent_52 = max_date - timedelta(weeks=52)
ytd_start = pd.Timestamp(year=max_date.year, month=1, day=1)

# Sidebar filters
st.sidebar.header("Filters")
min_date = df['Periods'].min()
start_date, end_date = st.sidebar.date_input("Select Period Range", [min_date, max_date])

# MR buttons
c1, c2 = st.sidebar.columns(2)
if c1.button(f"MR 4 w/e {latest_date_str}"): start_date, end_date = recent_4, max_date
if c2.button(f"MR 13 w/e {latest_date_str}"): start_date, end_date = recent_13, max_date
c3, c4 = st.sidebar.columns(2)
if c3.button(f"MR 26 w/e {latest_date_str}"): start_date, end_date = recent_26, max_date
if c4.button(f"MR 52 w/e {latest_date_str}"): start_date, end_date = recent_52, max_date
if st.sidebar.button(f"YTD w/e {latest_date_str}"): start_date, end_date = ytd_start, max_date

# Filter by date
df = df[(df['Periods'] >= pd.to_datetime(start_date)) & (df['Periods'] <= pd.to_datetime(end_date))]

# Segment filter
with st.sidebar.expander("Segment", expanded=True):
    all_segments = list(df['Segment'].unique())
    if 'selected_segments' not in st.session_state: st.session_state.selected_segments = all_segments.copy()
    b1, b2 = st.columns(2)
    if b1.button("Select All", key="select_all_segments"): st.session_state.selected_segments = all_segments.copy()
    if b2.button("Clear All", key="clear_all_segments"): st.session_state.selected_segments = []
    selected_segments = [s for s in all_segments if st.checkbox(s, s in st.session_state.selected_segments)]
    st.session_state.selected_segments = selected_segments
df = df[df['Segment'].isin(st.session_state.selected_segments)]

# Sub Category filter
with st.sidebar.expander("Sub Category", expanded=True):
    all_subs = list(df['Sub Category'].unique())
    if 'selected_subs' not in st.session_state: st.session_state.selected_subs = all_subs.copy()
    b1, b2 = st.columns(2)
    if b1.button("Select All", key="select_all_subs"): st.session_state.selected_subs = all_subs.copy()
    if b2.button("Clear All", key="clear_all_subs"): st.session_state.selected_subs = []
    selected_subs = [s for s in all_subs if st.checkbox(s, s in st.session_state.selected_subs)]
    st.session_state.selected_subs = selected_subs
df = df[df['Sub Category'].isin(st.session_state.selected_subs)]

# Metrics
total_dollars = df['$'].sum()
total_units = df['Units'].sum()
total_pounds = df['Eq'].sum()
total_dollars_ya = df['$ Ya'].sum()
total_units_ya = df['Units Ya'].sum()
total_pounds_ya = df['Eq Ya'].sum()
pct_dollars = (total_dollars - total_dollars_ya)/total_dollars_ya if total_dollars_ya else 0
pct_units = (total_units - total_units_ya)/total_units_ya if total_units_ya else 0
pct_pounds = (total_pounds - total_pounds_ya)/total_pounds_ya if total_pounds_ya else 0

def format_metric(value, unit=""):
    if abs(value) >= 1_000_000_000: return f"{value/1_000_000_000:.1f}B {unit}".strip()
    if abs(value) >= 1_000_000: return f"{value/1_000_000:.1f}M {unit}".strip()
    if abs(value) >= 1_000: return f"{value/1_000:.1f}K {unit}".strip()
    return f"{value:,.0f} {unit}".strip() if unit else f"{value:,.0f}"

# Donut chart (smaller, normal hole size)
org_cnv = df['Organic'].value_counts().reset_index()
org_cnv.columns = ['Type','Count']

color_scale = alt.Scale(domain=['ORG','CNV'], range=['#099C6F','#E1A528'])

donut = alt.Chart(org_cnv).mark_arc(innerRadius=50).encode(
    theta=alt.Theta(field='Count', type='quantitative'),
    color=alt.Color('Type:N', scale=color_scale, legend=alt.Legend(title="ORG vs CNV"))
).properties(
    width=300,
    height=200
)

# Display metrics + donut in a single row
c1, c2, c3, c4 = st.columns([1,1,1,1])
c1.metric("Dollars", format_metric(total_dollars), f"{pct_dollars:.1%} vs YA")
c2.metric("Units", format_metric(total_units), f"{pct_units:.1%} vs YA")
c3.metric("Pounds", format_metric(total_pounds, "lbs"), f"{pct_pounds:.1%} vs YA")
c4.altair_chart(donut, use_container_width=True)

# Layout: line chart full width
line_chart_df = df.groupby('Periods')[['$', '$ Ya']].sum().reset_index()

area = alt.Chart(line_chart_df).mark_area(color='#FED7D7', opacity=0.5).encode(
    x='Periods:T',
    y=alt.Y('$ Ya:Q', title='Dollars'),
    tooltip=['Periods', alt.Tooltip('$ Ya', title='Dollars YA')]
)

line = alt.Chart(line_chart_df).mark_line(color='#AA0404', strokeWidth=3).encode(
    x='Periods:T',
    y=alt.Y('$:Q', title='Dollars'),
    tooltip=['Periods', alt.Tooltip('$', title='Dollars')]
)

line_chart = alt.layer(area, line).resolve_scale(y='shared')

st.altair_chart(line_chart, use_container_width=True)

# Segment summary table
seg_summary = df.groupby('Segment').agg({
    '$':'sum',
    '$ Ya':'sum',
    'Units':'sum',
    'Units Ya':'sum',
    'Eq':'sum',
    'Eq Ya':'sum'
}).reset_index()

seg_summary['Dollars % Change'] = ((seg_summary['$'] - seg_summary['$ Ya']) / seg_summary['$ Ya']).fillna(0)
seg_summary['Units % Change'] = ((seg_summary['Units'] - seg_summary['Units Ya']) / seg_summary['Units Ya']).fillna(0)
seg_summary['Pounds % Change'] = ((seg_summary['Eq'] - seg_summary['Eq Ya']) / seg_summary['Eq Ya']).fillna(0)

seg_summary = seg_summary[['Segment', '$', 'Dollars % Change', 'Eq', 'Pounds % Change', 'Units', 'Units % Change']]
seg_summary = seg_summary.rename(columns={'$':'Dollars', 'Eq':'Pounds'})
seg_summary = seg_summary.sort_values('Dollars', ascending=False)

st.dataframe(seg_summary.style.format({
    'Dollars':'${:,.0f}',
    'Dollars % Change':'{:.1%}',
    'Pounds':'{:,.0f}',
    'Pounds % Change':'{:.1%}',
    'Units':'{:,.0f}',
    'Units % Change':'{:.1%}'
}))
