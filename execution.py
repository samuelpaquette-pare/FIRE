"""
This module contains the functions to render the execution tabs of the Streamlit app.
"""

import altair as alt
import pandas as pd
import streamlit as st
from financial_calculation import calculate_required_monthly_investment
from simulation import simulate_time_series

def render_execution_tab():
    """
    Render the tab for the user to input their current net worth, expected interest rate, and FI mode.
    """
    current_net_worth = st.number_input(
        "Current net worth ($)",
        step=100,
        format="%d",
        value=0,
        help="The amount of money you currently have in your investment accounts (e.g., RRSP, TFSA, "
            "non-registered accounts). This does not include your primary residence but DO include other residences equity.",
    )

    expected_interest_rate = st.slider(
        "Interest Rate (% per year)",
        min_value=0.0,
        max_value=15.0,
        step=0.1,
        value=7.0,
        help=(
            "Average yearly return expected on your investments. For a diversified portfolio of stocks and bonds, this typically ranges between 5% and 7%."
        )
    )

    st.session_state.current_net_worth = current_net_worth
    st.session_state.expected_interest_rate = expected_interest_rate

    fi_mode = st.radio(
        "Choose one of the following options to simulate your path to FI.",
        options=[
            "I want to know when I can be FI",
            "I want to retire at a specific age",
        ],
        captions=[
            "Time until objective is met based on what you can put aside",
            "How much to put aside to meet objective at age x",
        ],
        index=None,
        help="Choose the mode you want to use to simulate your path to FI. If you want to explore or know what you can put aside/invest, choose the first option. If you have a specific age in mind, choose the second option.",
    )

    if fi_mode == "I want to know when I can be FI":
        render_time_until_tab()
        
    elif fi_mode == "I want to retire at a specific age":
        render_age_tab()

    if st.session_state.get("base_monthly_investment") is not None:
        data_df = simulate_time_series(
            st.session_state.current_net_worth,
            st.session_state.base_monthly_investment,
            st.session_state.expected_interest_rate,
            st.session_state.get("monthly_deposit_growth", 3),
        )

        monthly_amounts_df = pd.melt(
            data_df.reset_index(names="Year"),
            id_vars=["Year"],
            value_vars=[
                "Net Worth",
                "Interest",
                "Monthly Investment",
                "Interest - Cumulative Sum",
                "Monthly Investment - Cumulative Sum",
            ],
            var_name="Amount Type",
            value_name="Amount",
        )

        criterion = monthly_amounts_df["Amount Type"].isin(
            [
                "Net Worth",
                "Interest - Cumulative Sum",
                "Monthly Investment - Cumulative Sum",
            ]
        )

        monthly_amounts_chart = (
            alt.Chart(monthly_amounts_df[criterion])
            .mark_line()
            .encode(
                x="Year:T",
                y=alt.Y("Amount:Q", title="Financial Amount (in $)"),
                color=alt.Color("Amount Type:N", title="Type of Amount"),
            )
        )
        objective_line = (
            alt.Chart(pd.DataFrame({"Amount": [st.session_state.get("fire_objective", 0)]}))
            .mark_rule()
            .encode(y="Amount:Q")
        )
        st.altair_chart(monthly_amounts_chart + objective_line, use_container_width=True)

        date_exceeding = data_df[
            data_df["Net Worth"] >= st.session_state.get("fire_objective", 0)
        ].index.min()
        if date_exceeding is pd.NaT:
            st.warning("Net worth will not exceed fire objective in the next 35 years.")
        else:
            st.info(f"Net worth exceeds fire objective at: {date_exceeding.date()}")

def render_time_until_tab():
    """
    Render the tab for the user to input their monthly investment and growth rate.
    """
    st.header("Time until objective is met")

    base_monthly_investment = st.number_input(
        "Monthly investment ($)",
        step=10,
        format="%d",
        help="The amount of money you expect to invest each month.",
    )
    monthly_deposit_growth = st.number_input(
        "Monthly investment growth (% per year)",
        step=0.1,
        help="Expected yearly growth of your monthly investment. As time goes on, you may be able to increase monthly contributions.",
    )

    st.session_state.base_monthly_investment = base_monthly_investment
    st.session_state.monthly_deposit_growth = monthly_deposit_growth


def render_age_tab():
    """
    Render the tab for the user to input their current age and the age at which they want to reach FI.
    """
    st.header("How much to put aside to meet objective at age x")

    current_age = st.number_input(
        "Current Age", min_value=18, max_value=120, step=1, format="%d"
    )
    target_age = st.number_input(
        "Target Age to Reach FI",
        min_value=current_age + 1,
        max_value=120,
        step=1,
        format="%d",
    )

    # Ensure target age is greater than current age
    if target_age <= current_age:
        st.error("Target age must be greater than current age.")
        return

    fire_objective = st.session_state.get("fire_objective", 0)

    # Calculate the required monthly investment
    required_monthly_investment = calculate_required_monthly_investment(
        st.session_state.get("current_net_worth", 0),
        target_age,
        current_age,
        st.session_state.get("expected_interest_rate", 0),
        fire_objective,
    )

    st.info(
        f"To reach your FI objective of \${fire_objective:,.0f} by age {target_age}, you need to invest \${required_monthly_investment:,.0f} each month."
    )

    st.session_state.current_age = current_age
    st.session_state.target_age = target_age
    st.session_state.base_monthly_investment = required_monthly_investment
