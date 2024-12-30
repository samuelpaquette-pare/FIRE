"""
This module contains functions to simulate financial time series.
"""

from datetime import datetime
import pandas as pd
from financial_calculation import calculate_month_values


def simulate_time_series(
    net_worth: float,
    base_monthly_deposit: float,
    yearly_interest_rate: float,
    monthly_deposit_yearly_growth: float,
    years: int = 35,
) -> pd.DataFrame:
    """
    Simulates the financial time series based on net worth, deposits, and growth rates.

    Args:
        net_worth (float): Starting net worth.
        base_monthly_deposit (float): Initial monthly deposit.
        yearly_interest_rate (float): Annual interest rate (as a decimal).
        monthly_deposit_yearly_growth (float): Yearly growth of monthly deposits (as a decimal).
        years (int, optional): Horizon for the simulation in years. Defaults to 35.

    Returns:
        pd.DataFrame: DataFrame containing the financial time series.
    """
    # Initialize variables
    calculation_horizon = years * 12
    current_net_worth = net_worth
    current_monthly_deposit = base_monthly_deposit

    data = []
    for _ in range(calculation_horizon):
        current_val = calculate_month_values(
            current_net_worth,
            yearly_interest_rate,
            current_monthly_deposit,
            monthly_deposit_yearly_growth,
        )
        current_net_worth = current_val["new_amount"]
        current_monthly_deposit = current_val["new_monthly_deposit"]
        data.append([current_net_worth, current_val["interest_made"], current_monthly_deposit])

    dates = pd.date_range(start=datetime.now(), periods=calculation_horizon, freq="MS")
    df = pd.DataFrame(data, index=dates, columns=["Net Worth", "Interest", "Monthly Investment"])

    df["Monthly Investment - Cumulative Sum"] = df["Monthly Investment"].cumsum()
    df["Interest - Cumulative Sum"] = df["Interest"].cumsum()

    return df

def monte_carlo_disbursement(initial_assets: float) -> pd.DataFrame:
    pass