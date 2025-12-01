"""
Tests for Cashflow Engine

Tests income, expense, and debt payment calculations.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from data_models import (
    UserProfile, IncomeStream, Expense, Debt, DebtPortfolio,
    RiskTolerance, PayFrequency, DebtType
)
from core.cashflow import CashflowAnalyzer, calculate_amortization_schedule, calculate_total_interest


class TestCashflowAnalyzer(unittest.TestCase):
    """Test cases for CashflowAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.profile = UserProfile(
            income_streams=[
                IncomeStream(name="Salary", amount=5000.0, frequency=PayFrequency.MONTHLY)
            ],
            expenses=[
                Expense(name="Rent", amount=1500.0, is_essential=True),
                Expense(name="Food", amount=500.0, is_essential=True),
                Expense(name="Entertainment", amount=200.0, is_essential=False),
            ],
            current_savings=3000.0,
            emergency_fund_months=3.0
        )
        
        self.debts = DebtPortfolio(
            debts=[
                Debt(
                    name="Credit Card",
                    debt_type=DebtType.CREDIT_CARD,
                    current_balance=5000.0,
                    annual_interest_rate=0.18,
                    minimum_payment=150.0
                ),
                Debt(
                    name="Student Loan",
                    debt_type=DebtType.STUDENT_LOAN,
                    current_balance=10000.0,
                    annual_interest_rate=0.06,
                    minimum_payment=120.0
                ),
            ]
        )
        
        self.analyzer = CashflowAnalyzer(self.profile, self.debts)
    
    def test_monthly_income(self):
        """Test monthly income calculation."""
        self.assertEqual(self.analyzer.monthly_gross_income(), 5000.0)
    
    def test_monthly_expenses(self):
        """Test monthly expense calculation."""
        self.assertEqual(self.analyzer.monthly_total_expenses(), 2200.0)
    
    def test_essential_expenses(self):
        """Test essential expense calculation."""
        self.assertEqual(self.analyzer.monthly_essential_expenses(), 2000.0)
    
    def test_minimum_debt_payments(self):
        """Test minimum debt payment calculation."""
        self.assertEqual(self.analyzer.monthly_minimum_debt_payments(), 270.0)
    
    def test_monthly_surplus(self):
        """Test monthly surplus calculation."""
        # 5000 - 2200 - 270 = 2530
        self.assertEqual(self.analyzer.monthly_surplus(), 2530.0)
    
    def test_positive_cashflow(self):
        """Test positive cashflow detection."""
        self.assertTrue(self.analyzer.has_positive_cashflow())
    
    def test_negative_cashflow(self):
        """Test negative cashflow detection."""
        # Create profile with high expenses
        profile = UserProfile(
            income_streams=[
                IncomeStream(name="Salary", amount=2000.0, frequency=PayFrequency.MONTHLY)
            ],
            expenses=[
                Expense(name="Rent", amount=1500.0, is_essential=True),
                Expense(name="Food", amount=800.0, is_essential=True),
            ],
            current_savings=1000.0
        )
        
        analyzer = CashflowAnalyzer(profile, self.debts)
        self.assertFalse(analyzer.has_positive_cashflow())
    
    def test_debt_to_income_ratio(self):
        """Test debt-to-income ratio calculation."""
        # Total debt: 15000, Annual income: 60000
        # DTI = 15000 / 60000 = 0.25
        dti = self.analyzer.debt_to_income_ratio()
        self.assertAlmostEqual(dti, 0.25, places=2)
    
    def test_debt_service_ratio(self):
        """Test debt service ratio calculation."""
        # Monthly debt payments: 270, Monthly income: 5000
        # DSR = 270 / 5000 = 0.054
        dsr = self.analyzer.debt_service_ratio()
        self.assertAlmostEqual(dsr, 0.054, places=3)
    
    def test_safe_surplus(self):
        """Test safe surplus calculation with margin."""
        surplus = self.analyzer.monthly_surplus()
        safe = self.analyzer.calculate_safe_surplus(safety_margin=0.1)
        self.assertAlmostEqual(safe, surplus * 0.9, places=2)
    
    def test_emergency_fund_check(self):
        """Test emergency fund adequacy check."""
        # Essential expenses: 2000, Target: 3 months = 6000
        # Current savings: 3000 < 6000
        self.assertFalse(self.profile.has_adequate_emergency_fund())
        
        # Increase savings
        self.profile.current_savings = 7000.0
        self.assertTrue(self.profile.has_adequate_emergency_fund())


class TestAmortization(unittest.TestCase):
    """Test cases for amortization calculations."""
    
    def test_simple_amortization(self):
        """Test basic amortization schedule."""
        # $1000 at 12% APR, $100/month payment
        schedule = calculate_amortization_schedule(
            principal=1000.0,
            annual_rate=0.12,
            monthly_payment=100.0
        )
        
        self.assertGreater(len(schedule), 0)
        
        # First payment
        month, payment, interest, principal, balance = schedule[0]
        self.assertEqual(month, 1)
        self.assertAlmostEqual(interest, 10.0, places=2)  # 1000 * 0.01
        self.assertAlmostEqual(principal, 90.0, places=2)  # 100 - 10
        
        # Last payment should have near-zero balance
        final_balance = schedule[-1][4]
        self.assertLess(final_balance, 1.0)
    
    def test_total_interest(self):
        """Test total interest calculation."""
        # $1000 at 12% APR, $100/month payment
        total_interest = calculate_total_interest(
            principal=1000.0,
            annual_rate=0.12,
            monthly_payment=100.0
        )
        
        self.assertIsNotNone(total_interest)
        self.assertGreater(total_interest, 0)
        self.assertLess(total_interest, 1000.0)  # Interest should be less than principal
    
    def test_insufficient_payment(self):
        """Test when payment doesn't cover interest."""
        # $1000 at 12% APR, $5/month payment (less than $10 interest)
        total_interest = calculate_total_interest(
            principal=1000.0,
            annual_rate=0.12,
            monthly_payment=5.0
        )
        
        # Should return None because debt won't pay off
        self.assertIsNone(total_interest)
    
    def test_zero_interest(self):
        """Test amortization with zero interest."""
        schedule = calculate_amortization_schedule(
            principal=1000.0,
            annual_rate=0.0,
            monthly_payment=100.0
        )
        
        # Should take exactly 10 months
        self.assertEqual(len(schedule), 10)
        
        # Each payment should be all principal
        for month, payment, interest, principal, balance in schedule:
            self.assertEqual(interest, 0.0)
            self.assertAlmostEqual(principal, 100.0, places=2)


class TestIncomeConversions(unittest.TestCase):
    """Test income frequency conversions."""
    
    def test_weekly_to_monthly(self):
        """Test weekly income conversion."""
        income = IncomeStream(
            name="Weekly Pay",
            amount=500.0,
            frequency=PayFrequency.WEEKLY
        )
        # 500 * 52 / 12 ≈ 2166.67
        self.assertAlmostEqual(income.monthly_amount(), 2166.67, places=2)
    
    def test_biweekly_to_monthly(self):
        """Test bi-weekly income conversion."""
        income = IncomeStream(
            name="Bi-weekly Pay",
            amount=1000.0,
            frequency=PayFrequency.BI_WEEKLY
        )
        # 1000 * 26 / 12 ≈ 2166.67
        self.assertAlmostEqual(income.monthly_amount(), 2166.67, places=2)
    
    def test_annual_to_monthly(self):
        """Test annual income conversion."""
        income = IncomeStream(
            name="Annual Bonus",
            amount=12000.0,
            frequency=PayFrequency.ANNUALLY
        )
        # 12000 / 12 = 1000
        self.assertEqual(income.monthly_amount(), 1000.0)


if __name__ == '__main__':
    unittest.main()
