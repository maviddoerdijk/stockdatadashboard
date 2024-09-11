import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.title("Track Your Investments")

# Inputs
col1, col2 = st.columns(2)
current_total_investments = col1.number_input("Current Total Investments ($)")
expected_growth_percentage = col2.number_input("Expected Yearly Growth Percentage (%)")
monthly_investment = col1.number_input("Monthly Investments ($)")
age = col2.number_input("Your Age (yrs)", min_value=0, max_value=100)


# Based on the 3 inputs, calculate yearly data for total portfolio worth.
current_year = datetime.now().year
yearly_data = []
total_investments = current_total_investments
for current_age in range(age, 100):
    yearly_data.append({
        'Year': current_age,
        'Total Portfolio Worth ($)': total_investments
    })
    total_investments += (total_investments * (expected_growth_percentage / 100)) + (monthly_investment * 12)
df = pd.DataFrame(yearly_data)
df.set_index('Year', inplace=True)

st.line_chart(df)