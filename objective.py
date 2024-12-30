import streamlit as st
from financial_calculation import calculate_FI_objective


def render_objective_tab():
    """
    Render the objective tab of the FI calculator.
    """
    st.header("What is your objective?")
    st.write(
        "Remember that the all the values are in today's dollars to keep it relatable. Adjust the inputs below to calculate your financial independence (FI) objective."
    )

    swr = st.slider(
        "Safe withdrawal rate (%)",
        min_value=1,
        max_value=10,
        value=4,
        help="The percentage of your portfolio you plan to withdraw annually after achieving financial independence. Typically ranges from 3-4%.",
    )
    expected_spending = st.number_input(
        "Expected spending after FI ($ per year)",
        value=60000,
        step=100,
        format="%d",
        help="The total amount you plan to spend annually after achieving financial independence.",
    )
    expected_revenue = st.number_input(
        "Expected revenue after FI ($ per year)",
        value=20000,
        step=100,
        format="%d",
        help="The total amount you expect to receive annually (e.g., from pensions, rentals, or other sources) after achieving financial independence.",
    )
    fire_objective = calculate_FI_objective(swr, expected_spending, expected_revenue)
    st.info(
        f"Your FI objective is of {fire_objective:,.0f}\$ which should be enough to cover the {expected_spending - expected_revenue:,.0f}\$ difference between your expected spending and revenue with the interest alone."
    )

    # Keep the values in the session state for access in other tabs
    st.session_state.fire_objective = fire_objective
    st.session_state.expected_spending = expected_spending
    st.session_state.expected_revenue = expected_revenue
    st.session_state.swr = swr
