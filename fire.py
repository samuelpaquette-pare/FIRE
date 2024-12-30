import streamlit as st
from objective import render_objective_tab
from disbursement import render_disbursement_tab
from execution import render_execution_tab


# TODO: per REER and CELI
# TODO: Prendre en compte des grosses dépenses prévu
# TODO: simulation Monte carlo pour le rendement des stocks.
# TODO: Check part about perfect calculator https://milliondollarjourney.com/5-useful-retirement-calculators-how-much-do-you-need-to-retire.htm


st.title("Canadian FI calculator")

objective_tab, execution_tab, disbursement_tab = st.tabs(["Objective", "Execution", "Disbursement"])
with objective_tab:
    render_objective_tab()

with execution_tab:
    render_execution_tab()

with disbursement_tab:
    render_disbursement_tab()
