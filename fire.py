import streamlit as st
from objective import render_objective_tab
from disbursement import render_disbursement_tab
from execution import render_execution_tab

st.title("Canadian FI calculator")

objective_tab, execution_tab, disbursement_tab = st.tabs(["Objective", "Execution", "Disbursement"])
with objective_tab:
    render_objective_tab()

with execution_tab:
    render_execution_tab()

with disbursement_tab:
    render_disbursement_tab()
