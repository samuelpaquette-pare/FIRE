"""
This module contains functions to simulate financial time series.
"""

from datetime import datetime
from typing import List
import pandas as pd
import os
from financial_calculation import calculate_month_values


def simulate_time_series(
    net_worth: float,
    base_monthly_deposit: float,
    monthly_deposit_yearly_growth: float,
    years: int = 35,
    historical_returns: List[float] = None,
) -> pd.DataFrame:
    """
    Simulates the financial time series based on net worth, deposits, and growth rates.

    Args:
        net_worth (float): Starting net worth.
        base_monthly_deposit (float): Initial monthly deposit.
        yearly_interest_rate (float): Annual interest rate (as a decimal).
        monthly_deposit_yearly_growth (float): Yearly growth of monthly deposits (as a decimal).
        years (int, optional): Horizon for the simulation in years. Defaults to 35.
        historical_returns (List[float], optional): List of historical returns for each year.

    Returns:
        pd.DataFrame: DataFrame containing the financial time series.
    """
    # Initialize variables
    current_net_worth = net_worth
    current_monthly_deposit = base_monthly_deposit
    historical_returns = historical_returns or [7] * years

    data = []
    for year in range(years):
        yearly_interest_rate = historical_returns[year]

        for _ in range(12):
            current_val = calculate_month_values(
                current_net_worth,
                yearly_interest_rate,
                current_monthly_deposit,
                monthly_deposit_yearly_growth,
            )
            current_net_worth = current_val["new_amount"]
            current_monthly_deposit = current_val["new_monthly_deposit"]
            data.append([current_net_worth, current_val["interest_made"], current_monthly_deposit])

    dates = pd.date_range(start=datetime.now(), periods=years * 12, freq="MS")
    df = pd.DataFrame(data, index=dates, columns=["Net Worth", "Interest", "Monthly Investment"])

    df["Monthly Investment - Cumulative Sum"] = df["Monthly Investment"].cumsum()
    df["Interest - Cumulative Sum"] = df["Interest"].cumsum()

    return df


def monte_carlo_accruing_wealth(
    current_net_worth: float,
    base_monthly_investment: float,
    monthly_deposit_growth: float,
    simulations: int = 1000,
    years: int = 35,
) -> pd.DataFrame:
    """
    Simulates accruing wealth over 35 years on a monthly basis using a Monte Carlo approach.

    Args:
        current_net_worth (float): Starting net worth.
        base_monthly_investment (float): Initial monthly investment.
        monthly_deposit_growth (float): Yearly growth of monthly deposits (as a decimal).
        simulations (int): Number of Monte Carlo simulations to run.
        years (int): Number of years to simulate.

    Returns:
        pd.DataFrame: A DataFrame with columns "Net Worth", "Interest", "Monthly Investment",
                      "Monthly Investment - Cumulative Sum", and "Interest - Cumulative Sum"
    """
    historical_returns = pd.read_csv(f"{os.getcwd()}/sp-500-historical-annual-returns.csv")

    # Storage for simulation results
    simulation_results = [
        simulate_time_series(
            current_net_worth,
            base_monthly_investment,
            monthly_deposit_growth,
            years,
            historical_returns.sample(n=years)["value"].to_list(),
        ) for _ in range(simulations)
    ]
    
    # Combine all simulation results
    for i, df in enumerate(simulation_results):
        df['Iteration'] = i
    combined_results = pd.concat(simulation_results, ignore_index=False)

    return combined_results
