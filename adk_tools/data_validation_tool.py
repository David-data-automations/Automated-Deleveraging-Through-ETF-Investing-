"""
ADK-like Data Validation Tool

Wraps the initial data validation and cashflow analysis logic.
"""

from typing import Dict, Any
from adk_sim.adk_base import Tool, ToolContext
from data_models import UserProfile, DebtPortfolio
from core.cashflow import CashflowAnalyzer


class DataValidationTool(Tool):
    """Validates input data and performs cashflow analysis."""
    
    def __init__(self):
        super().__init__(
            name="DataValidationTool",
            description="Validates user profile and debt data, performs cashflow analysis, and identifies red flags."
        )
        self.context = ToolContext(self.name)
    
    def run(self, profile: UserProfile, debts: DebtPortfolio, **kwargs) -> Dict[str, Any]:
        """
        Runs the data validation and cashflow analysis process.
        
        Input:
            profile: UserProfile object
            debts: DebtPortfolio object
            
        Output:
            profile: UserProfile object (validated)
            debts: DebtPortfolio object (validated)
            cashflow_summary: Dict of cashflow metrics
            validation_warnings: List of warnings/errors
        """
        self.context.log("INFO", "Starting data validation and cashflow analysis.")
        
        # 1. Core Validation
        warnings = []
        warnings.extend(profile.validate())
        warnings.extend(debts.validate())
        
        # 2. Cashflow Analysis
        cashflow_analyzer = CashflowAnalyzer(profile, debts)
        cashflow_summary = cashflow_analyzer.get_cashflow_summary()
        warnings.extend(cashflow_summary['red_flags'])
        
        self.context.log("INFO", "Validation and cashflow analysis complete.", 
                         warnings_count=len(warnings), 
                         surplus=cashflow_summary['monthly_surplus'])
        
        return {
            'profile': profile,
            'debts': debts,
            'cashflow_summary': cashflow_summary,
            'validation_warnings': warnings,
        }
