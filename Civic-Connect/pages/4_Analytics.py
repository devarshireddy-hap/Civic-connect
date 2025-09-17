import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("📊 CivicConnect Analytics Dashboard")
st.write("View statistics and insights from reported civic issues.")

# Example: fake dataset (replace with DB queries)
data = pd.DataFrame({
    "Issue Type": ["Road", "Water", "Electricity", "Waste", "Other"],
    "Reports": [23, 15, 12, 30, 8],
    "Resolved": [10, 8, 5, 20, 3],
})

# Calculate pending issues
data["Pending"] = data["Reports"] - data["Resolved"]

# --- Bar Chart ---
st.subheader("Reports by Issue Type")
st.bar_chart(data.set_index("Issue Type")["Reports"])

# --- Pie Chart ---
st.subheader("Resolved vs Pending Issues")
status_data = pd.DataFrame({
    "Status": ["Resolved", "Pending"],
    "Count": [data["Resolved"].sum(), data["Pending"].sum()]
})

fig, ax = plt.subplots()
ax.pie(status_data["Count"], labels=status_data["Status"], autopct="%1.1f%%", startangle=90)
ax.axis("equal")
st.pyplot(fig)
