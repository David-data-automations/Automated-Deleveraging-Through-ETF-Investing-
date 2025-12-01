"""
Command Line Interface

Provides a simple CLI for running the debt deleveraging bot.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_models import (
    UserProfile, IncomeStream, Expense, Debt, DebtPortfolio,
    RiskTolerance, PayFrequency, DebtType, PayoffStrategy
)
from adk_sim.adk_base import Runner
from adk_sim.deleveraging_agent import create_deleveraging_agent


def print_separator(char="=", length=80):
    """Print a separator line."""
    print(char * length)


def print_section_header(title: str):
    """Print a formatted section header."""
    print_separator()
    print(f"  {title}")
    print_separator()
    print()


def format_currency(amount: float) -> str:
    """Format amount as currency."""
    return f"${amount:,.2f}"


def format_percentage(rate: float) -> str:
    """Format rate as percentage."""
    return f"{rate:.2%}"


def print_plan_output(output):
    """
    Print the complete plan output in a readable format from the ADK Runner.
    
    Args:
        output: Dict from Runner.run
    """
    
    # Check for critical errors
    if 'error' in output:
        print_section_header("CRITICAL ERROR - PLANNING HALTED")
        print(output['error'])
        print("\nValidation Warnings:")
        for warning in output.get('validation_warnings', []):
            print(f"  • {warning}")
        print_separator()
        return
    
    # Extract data from the Runner output
    narrative = output['final_narrative']
    plan_output = output['plan_output']
    plan = plan_output.recommended_plan
    
    # Disclaimer (always first)
    print_section_header("IMPORTANT DISCLAIMER")
    print(plan.disclaimer)
    print("\n")
    
    # Executive Summary (LLM-Generated)
    print_section_header("EXECUTIVE SUMMARY")
    print(narrative['executive_summary'])
    print("\n")
    
    # Detailed Explanation (Structured, from core logic)
    print_section_header("DETAILED ANALYSIS")
    print(plan_output.detailed_explanation)
    print("\n")
    
    # Recommended Plan Details
    print_section_header("YOUR RECOMMENDED PLAN")
    
    print(f"Strategy: {plan.strategy.value.title()}")
    print(f"Monthly Surplus: {format_currency(plan.monthly_surplus)}")
    print(f"Allocation: {plan.debt_allocation_percentage:.0%} Debt / "
          f"{plan.etf_allocation_percentage:.0%} ETF")
    print()
    print(f"Monthly Extra Debt Payment: {format_currency(plan.monthly_extra_debt_payment)}")
    print(f"Monthly ETF Contribution: {format_currency(plan.monthly_etf_contribution)}")
    print()
    
    if plan.estimated_months_to_debt_free:
        print(f"Estimated Months to Debt-Free: {plan.estimated_months_to_debt_free:.0f} "
              f"({plan.estimated_months_to_debt_free/12:.1f} years)")
        print(f"Total Interest Paid: {format_currency(plan.total_interest_paid)}")
        print(f"Interest Saved: {format_currency(plan.total_interest_saved)}")
    print()
    
    # ETF Allocations
    if plan.etf_allocations:
        print("Recommended ETF Allocation:")
        for allocation in plan.etf_allocations:
            print(f"  • {allocation.percentage:.0%} - {allocation.category} "
                  f"(e.g., {allocation.example_ticker})")
            print(f"    {allocation.description}")
        print()
    
    # Warnings
    if output.get('validation_warnings'):
        print("⚠️  WARNINGS:")
        for warning in output['validation_warnings']:
            print(f"  • {warning}")
        print()
    
    # Scenario Comparison (LLM-Generated Summary + Table)
    print_section_header("SCENARIO COMPARISON")
    print(narrative['tradeoff_analysis_summary'])
    print()
    
    # Comparison Table
    if narrative['comparison_table']:
        print("Quick Comparison Table:")
        print()
        
        # Header
        print(f"{'Scenario':<30} {'Months':<10} {'Interest':<15} {'ETF Value':<15} {'Net Worth':<15}")
        print("-" * 85)
        
        # Rows
        for scenario in narrative['comparison_table']:
            months = scenario['Months to Debt-Free']
            interest = scenario['Total Interest Paid']
            etf = scenario['Est. ETF Value (Medium)']
            net_worth = scenario['Est. Net Worth (Medium)']
            
            print(f"{scenario['Scenario']:<30} {months:<10} {interest:<15} {etf:<15} {net_worth:<15}")
        print()
    
    # Action Steps
    print_section_header("YOUR ACTION PLAN")
    print("Follow these steps to implement your debt deleveraging plan:\n")
    
    for i, step in enumerate(narrative['action_steps'], 1):
        print(f"{i}. {step}\n")
    
    print_separator()


def run_example():
    """Run an example scenario with sample data."""
    print_section_header("DEBT DELEVERAGING BOT - EXAMPLE SCENARIO")
    
    # Create sample user profile
    profile = UserProfile(
        income_streams=[
            IncomeStream(
                name="Salary",
                amount=5000.0,
                frequency=PayFrequency.MONTHLY
            )
        ],
        expenses=[
            Expense(name="Rent", amount=1500.0, is_essential=True),
            Expense(name="Utilities", amount=200.0, is_essential=True),
            Expense(name="Groceries", amount=400.0, is_essential=True),
            Expense(name="Transportation", amount=300.0, is_essential=True),
            Expense(name="Insurance", amount=200.0, is_essential=True),
            Expense(name="Entertainment", amount=200.0, is_essential=False),
            Expense(name="Dining Out", amount=150.0, is_essential=False),
        ],
        current_savings=5000.0,
        current_investments=2000.0,
        risk_tolerance=RiskTolerance.MODERATE,
        time_horizon_months=60,
        emergency_fund_months=3.0
    )
    
    # Create sample debts
    debts = DebtPortfolio(
        debts=[
            Debt(
                name="Credit Card A",
                debt_type=DebtType.CREDIT_CARD,
                current_balance=8000.0,
                annual_interest_rate=0.1899,  # 18.99%
                minimum_payment=200.0,
                due_day=15
            ),
            Debt(
                name="Credit Card B",
                debt_type=DebtType.CREDIT_CARD,
                current_balance=3500.0,
                annual_interest_rate=0.2399,  # 23.99%
                minimum_payment=100.0,
                due_day=20
            ),
            Debt(
                name="Student Loan",
                debt_type=DebtType.STUDENT_LOAN,
                current_balance=15000.0,
                annual_interest_rate=0.0549,  # 5.49%
                minimum_payment=180.0,
                due_day=1
            ),
            Debt(
                name="Auto Loan",
                debt_type=DebtType.AUTO_LOAN,
                current_balance=12000.0,
                annual_interest_rate=0.0649,  # 6.49%
                minimum_payment=250.0,
                due_day=10
            ),
        ]
    )
    
    print("Sample User Profile Created:")
    print(f"  Monthly Income: {format_currency(profile.total_monthly_income())}")
    print(f"  Monthly Expenses: {format_currency(profile.total_monthly_expenses())}")
    print(f"  Current Savings: {format_currency(profile.current_savings)}")
    print(f"  Risk Tolerance: {profile.risk_tolerance.value}")
    print()
    
    print("Sample Debts Created:")
    print(f"  Total Debt: {format_currency(debts.total_balance())}")
    print(f"  Total Minimum Payments: {format_currency(debts.total_minimum_payments())}")
    print(f"  Number of Debts: {len(debts.debts)}")
    print()
    
    # Create ADK-like SequentialAgent and Runner
    print("Creating debt deleveraging plan using ADK-like SequentialAgent...")
    print()
    
    agent = create_deleveraging_agent()
    runner = Runner(agent)
    
    # Prepare initial input for the Runner
    initial_input = {
        'profile': profile,
        'debts': debts,
        'strategy': PayoffStrategy.AVALANCHE.value
    }
    
    # Run the agent
    output = runner.run(initial_input)
    
    # Print results
    print_plan_output(output)


def main():
    """Main CLI entry point."""
    if len(sys.argv) > 1:
        # Future: Load from JSON file
        print("Loading from file not yet implemented.")
        print("Running example scenario instead...\n")
    
    run_example()


if __name__ == "__main__":
    main()
