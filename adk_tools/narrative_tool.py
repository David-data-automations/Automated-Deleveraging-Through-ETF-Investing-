"""
ADK-like Narrative Tool

Wraps the final narrative generation logic.
"""

from typing import Dict, Any
from adk_sim.adk_base import Tool, ToolContext
from data_models import PlanOutput


class NarrativeTool(Tool):
    """Generates the final human-readable narrative from the PlanOutput object."""
    
    def __init__(self):
        super().__init__(
            name="NarrativeTool",
            description="Generates the final human-readable narrative, including the comparison table and action steps."
        )
        self.context = ToolContext(self.name)
    
    def run(self, plan_output: PlanOutput, llm_financial_summary: str, **kwargs) -> Dict[str, Any]:
        """
        Runs the narrative generation process.
        
        Input:
            plan_output: PlanOutput object
            llm_financial_summary: LLM-generated summary from the Data Validation step
            
        Output:
            final_narrative: Dict containing the final, polished text elements
        """
        self.context.log("INFO", "Starting final narrative generation.")
        
        # In a real ADK, this tool would call the LLM-Wrapper Tool.
        # For simulation, we'll use the structured data from the PlanOutput
        # and the LLM summary passed from the previous step.
        
        plan = plan_output.recommended_plan
        
        # Simulate the final narrative structure
        final_narrative = {
            'executive_summary': f"LLM Summary: {llm_financial_summary}\n\n{plan_output.executive_summary}",
            'tradeoff_analysis_summary': plan_output.tradeoff_analysis,
            'action_steps': plan_output.action_steps,
            'comparison_table': plan_output.get_comparison_table(),
            'disclaimer': plan_output.disclaimer,
            'warnings': plan.warnings,
        }
        
        self.context.log("INFO", "Narrative generation complete.")
        
        return {
            'final_narrative': final_narrative
        }
