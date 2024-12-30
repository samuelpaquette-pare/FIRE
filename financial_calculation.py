def calculate_FI_objective(
    safe_withdrawal_rate: int, expected_spending: float, expected_revenue: float
) -> float:
    """Used to find the amount needed in order to be financially independent.

    Args:
        safe_withdrawal_rate (int): Percentage of the assets withdrawn each year once FIREd.
        expected_spending (float): Expected expenses per year once FIREd.
        expected_revenue (float): Expected revenue per year after taxes once FIREd.

    Returns:
        float: Returns the amount in $ needed to be FIREd given the circumstances.
    """
    diff_to_compensate = expected_spending - expected_revenue
    return diff_to_compensate / (safe_withdrawal_rate / 100)


def calculate_month_values(
    current_amount: float,
    yearly_interest_rate: float,
    current_monthly_deposit_amount: float,
    monthly_deposit_yearly_growth: float,
) -> dict:
    """Used to calculates monthly modifications in parameters of FI calculations

    Args:
        current_amount (float): Amount of total investment.
        yearly_interest_rate (float): Interest rate made on investments.
        current_monthly_deposit_amount (float): New amount added to the investment account
            as a monthly deposit.
        monthly_deposit_yearly_growth (float): Yearly rate at which the monthly deposit grows.

    Returns:
        dict: Returns new_amount, interest_made in the last month
            and new_monthly_deposit.
    """
    new_monthly_deposit = current_monthly_deposit_amount + (
        current_monthly_deposit_amount
        * (monthly_deposit_yearly_growth / (12.0 * 100.0))
    )
    interest_made = current_amount * (yearly_interest_rate / (12.0 * 100.0))
    new_amount = current_amount + interest_made + new_monthly_deposit

    return {
        "new_amount": new_amount, 
        "interest_made": interest_made, 
        "new_monthly_deposit": new_monthly_deposit,
    }

def calculate_required_monthly_investment(
        current_net_worth: float, 
        target_age: int, 
        current_age: int, 
        yearly_interest_rate: float, 
        fire_objective: float
    ) -> float:
    """
    "P" is the principal.
    "i" is the annual interest rate.
    "c" is the compounding frequency and represents how many times the interest is compounded each year.
    "n" is the number of years.
    "R" is the amount of the monthly contribution.
    FV = (P * ((1 + (i / c)) ** (n*c))) + ((R * (((1 + (i / c)) ** (n * c)) - 1)) / (i / c))
    (FV) - (P * ((1 + (i / c)) ** (n*c))) = ((R * (((1 + (i / c)) ** (n * c)) - 1)) / (i / c))
    (((FV) - (P * ((1 + (i / c)) ** (n*c)))) * (i / c)) = ((R * (((1 + (i / c)) ** (n * c)) - 1)))
    R * (((1 + (i / c)) ** (n * c)) - 1) = (((FV) - (P * ((1 + (i / c)) ** (n*c)))) * (i / c))
    R = (((FV) - (P * ((1 + (i / c)) ** (n*c)))) * (i / c)) / (((1 + (i / c)) ** (n * c)) - 1)
    
    Calculates the monthly investment required to reach the FI objective by the target age.

    Args:
        current_net_worth (float): The current net worth of the user.
        target_age (int): The target age to reach the FI objective.
        current_age (int): The current age of the user.
        yearly_interest_rate (float): The expected yearly interest rate (as a decimal).
        fire_objective (float): The financial independence objective (the amount the user wants to have).

    Returns:
        float: The monthly investment required to reach the FI objective by the target age.
    """
    months_to_target = (target_age - current_age) * 12
    monthly_interest_rate = 1 + ((yearly_interest_rate / 100) / 12)
    required_monthly_investment = ((fire_objective - (current_net_worth * (monthly_interest_rate ** months_to_target))) * (monthly_interest_rate - 1)) / ((monthly_interest_rate ** months_to_target) - 1)

    return max(required_monthly_investment, 0)
