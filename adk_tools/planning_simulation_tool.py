"""
ADK-like Planning and Simulation Tool

Wraps the core financial planning, allocation, and simulation logic.
"""

from typing import Dict, Any
from adk_sim.adk_base import Tool, ToolContext
from data_models import UserProfile, DebtPortfolio, PayoffStrategy, PlanOutput
from core.planner import DeleveragingPlanner


class PlanningSimulationTool(Tool):
    """Performs the core financial planning, allocation, and simulation."""
    
    def __init__(self):
        super().__init__(
            name="PlanningSimulationTool",
            description="Executes the core financial planning logic, including allocation, payoff strategy, and multi-scenario simulation."
        )
        self.context = ToolContext(self.name)
    
    def run(self, profile: UserProfile, debts: DebtPortfolio, strategy: str, **kwargs) -> Dict[str, Any]:
        """
        Runs the planning and simulation process.
        
        Input:
            profile: UserProfile object
            debts: DebtPortfolio object
            strategy: PayoffStrategy enum value (e.g., 'avalanche')
            
        Output:
            plan_output: PlanOutput object containing all simulation results
        """
        self.context.log("INFO", "Starting core planning and simulation.")
        
        try:
            strategy_enum = PayoffStrategy(strategy)
        except ValueError:
            self.context.log("ERROR", f"Invalid strategy provided: {strategy}", strategy=strategy)
            raise
            
        # The DeleveragingPlanner already handles the orchestration of
        # cashflow, allocation, and simulation engines.
        planner = DeleveragingPlanner(profile, debts, strategy_enum)
        
        # The planner's create_plan method generates the PlanOutput object
        plan_output: PlanOutput = planner.create_plan()
        
        self.context.log("INFO", "Planning and simulation complete.", 
                         months_to_debt_free=plan_output.recommended_plan.estimated_months_to_debt_free)
        
        return {
            'plan_output': plan_output,
        }
