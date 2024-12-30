"""
This module contains the functions to render the execution tabs of the Streamlit app.
"""

import altair as alt
import pandas as pd
pd.options.display.float_format = '${:,.2f}'.format
import streamlit as st
from financial_calculation import calculate_required_monthly_investment
from simulation import simulate_time_series, monte_carlo_accruing_wealth

def plot_results(data_df: pd.DataFrame) -> None:
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

    st.session_state.current_net_worth = current_net_worth

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

    simulation_mode = st.radio(
        "Choose one of the following simulation.",
        options=[
            "Monte Carlo",
            "Fixed return rate",
        ],
        captions=[
            "This will simulate the path to FI based on random real returns of the stock market in the past. Several iteration will be done to give you a range of possible outcomes.",
            "This will simulate the path to FI based on a fixed return rate you will provide.",
        ],
        index=None,
        help="Choose the simulation mode you want to use to simulate your path to FI. Monte Carlo gives you more of a realistic range of outcomes, while Fixed return rate gives you a simple and deterministic path based on the average return rate you expect.",
    )

    if simulation_mode == "Fixed return rate":
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
        st.session_state.expected_interest_rate = expected_interest_rate

        data_df = simulate_time_series(
            st.session_state.current_net_worth,
            base_monthly_investment,
            monthly_deposit_growth,
            35,
            [expected_interest_rate] * 35,
        )

        plot_results(data_df)

        date_exceeding = data_df[
            data_df["Net Worth"] >= st.session_state.get("fire_objective", 0)
        ].index.min()
        if date_exceeding is pd.NaT:
            st.warning("Net worth will not exceed fire objective in the next 35 years.")
        else:
            st.info(f"Net worth exceeds fire objective at: {date_exceeding.date()}")

    elif simulation_mode == "Monte Carlo":
        simulation_df = monte_carlo_accruing_wealth(
            st.session_state.current_net_worth,
            base_monthly_investment,
            monthly_deposit_growth,
            100,
            35
        )

        simulation_df = simulation_df.reset_index(names="Year")
        simulation_df["Year"] = simulation_df["Year"].dt.date
        net_worth_df = simulation_df.drop(columns=["Interest", "Monthly Investment", "Monthly Investment - Cumulative Sum", "Interest - Cumulative Sum"])

        chart = alt.Chart(net_worth_df).mark_line().encode(
            x="Year:T",
            y="Net Worth:Q",
            detail="Iteration:N",
            tooltip=["Year", "Net Worth", "Iteration"],
            opacity=alt.value(0.2),
        ).properties(
            title="Monte Carlo simulation of net worth over time",
        )
        objective_line = (
            alt.Chart(pd.DataFrame({"Objective": [st.session_state.get("fire_objective", 0)]}))
            .mark_rule()
            .encode(y="Objective:Q")
        )
        st.altair_chart(chart + objective_line, use_container_width=True)

        result_avg = simulation_df.groupby("Year").agg({
            "Net Worth": "mean", 
            "Interest - Cumulative Sum": "mean",
            "Monthly Investment - Cumulative Sum": "mean",
            "Interest": "mean",
            "Monthly Investment": "mean",
        })
        plot_results(result_avg)


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
        expected_interest_rate,
        fire_objective,
    )

    st.info(
        f"To reach your FI objective of \${fire_objective:,.0f} by age {target_age}, you need to invest \${required_monthly_investment:,.0f} each month."
    )

    st.session_state.expected_interest_rate = expected_interest_rate
    st.session_state.current_age = current_age
    st.session_state.target_age = target_age
    st.session_state.base_monthly_investment = required_monthly_investment

    data_df = simulate_time_series(
        st.session_state.current_net_worth,
        required_monthly_investment,
        st.session_state.get("monthly_deposit_growth", 3),
        35,
        [expected_interest_rate] * 35,
    )

    plot_results(data_df)
    
    date_exceeding = data_df[
        data_df["Net Worth"] >= fire_objective
    ].index.min()
    if date_exceeding is pd.NaT:
        st.warning("Net worth will not exceed fire objective in the next 35 years.")
    else:
        st.info(f"Net worth exceeds fire objective at: {date_exceeding.date()}")
