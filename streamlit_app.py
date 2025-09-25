import streamlit as st
import pandas as pd
from datetime import timedelta

st.title("🍎 Stremlit in Conduit Apples Demo")
st.write(
    "Testing how to run a Stremlit app in CP Conduit"
)






# Read CSV
df = pd.read_csv("Apples.csv")
df['Periods'] = pd.to_datetime(df['Periods'].astype(str).str[-8:], format='%m/%d/%y')
df['Organic'] = df['ORGANIC CLAIM'].apply(lambda x: 'CNV' if 'NOT' in str(x) else 'ORG')

# Sidebar filters
st.sidebar.header("Filters")

# Determine min/max for slider
min_date = df['Periods'].min()
max_date = df['Periods'].max()

# Format latest date like 9/13/25
latest_date_str = max_date.strftime("%-m/%-d/%y")  # Use "%#m/%#d/%y" on Windows if needed

# Pre-calculate common periods
recent_4 = max_date - timedelta(weeks=4)
recent_13 = max_date - timedelta(weeks=13)
recent_26 = max_date - timedelta(weeks=26)
recent_52 = max_date - timedelta(weeks=52)
ytd_start = pd.Timestamp(year=max_date.year, month=1, day=1)

# Date range slider
start_date, end_date = st.sidebar.date_input(
    "Select Period Range",
    [min_date, max_date]
)

# Quick buttons stacked vertically with formatted labels
if st.sidebar.button(f"MR 4 weeks ending {latest_date_str}"):
    start_date = recent_4
    end_date = max_date
if st.sidebar.button(f"MR 13 weeks ending {latest_date_str}"):
    start_date = recent_13
    end_date = max_date
if st.sidebar.button(f"MR 26 weeks ending {latest_date_str}"):
    start_date = recent_26
    end_date = max_date
if st.sidebar.button(f"MR 52 weeks ending {latest_date_str}"):
    start_date = recent_52
    end_date = max_date
if st.sidebar.button(f"YTD ending {latest_date_str}"):
    start_date = ytd_start
    end_date = max_date

df = df[(df['Periods'] >= pd.to_datetime(start_date)) & (df['Periods'] <= pd.to_datetime(end_date))]

# SEGMENT checkboxes
with st.sidebar.expander("SEGMENT", expanded=True):
    all_segments = list(df['SEGMENT'].unique())
    if 'selected_segments' not in st.session_state:
        st.session_state.selected_segments = all_segments.copy()
    if st.sidebar.button("Select All", key="select_all_segments"):
        st.session_state.selected_segments = all_segments.copy()
    if st.sidebar.button("Clear All", key="clear_all_segments"):
        st.session_state.selected_segments = []
    selected_segments = [seg for seg in all_segments if st.checkbox(seg, value=(seg in st.session_state.selected_segments))]
    st.session_state.selected_segments = selected_segments

df = df[df['SEGMENT'].isin(st.session_state.selected_segments)]

# SUB CATEGORY checkboxes
with st.sidebar.expander("SUB CATEGORY", expanded=True):
    all_subs = list(df['SUB CATEGORY'].unique())
    if 'selected_subs' not in st.session_state:
        st.session_state.selected_subs = all_subs.copy()
    if st.sidebar.button("Select All", key="select_all_subs"):
        st.session_state.selected_subs = all_subs.copy()
    if st.sidebar.button("Clear All", key="clear_all_subs"):
        st.session_state.selected_subs = []
    selected_subs = [cat for cat in all_subs if st.checkbox(cat, value=(cat in st.session_state.selected_subs))]
    st.session_state.selected_subs = selected_subs

df = df[df['SUB CATEGORY'].isin(st.session_state.selected_subs)]

# Keep only PERIODS and $ columns
df_filtered = df[['Periods', '$']]
df_grouped = df_filtered.groupby('Periods', as_index=True).sum()
st.line_chart(df_grouped)