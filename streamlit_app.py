import streamlit as st
import pandas as pd

st.title("🍎 Stremlit in Conduit Apples Demo")
st.write(
    "Testing how to run a Stremlit app in CP Conduit"
)


# Read CSV
df = pd.read_csv("Apples.csv")

# Keep rightmost 8 characters of PERIODS

df['Periods'] = df['Periods'].astype(str).str[-8:]

# Convert to datetime
df['Periods'] = pd.to_datetime(df['Periods'], format='%m/%d/%y')

# Keep only PERIODS and $ columns
df = df[['Periods', '$']]

# Group by date and sum $
df_grouped = df.groupby('Periods', as_index=True).sum()

# Plot line chart
st.line_chart(df_grouped)