"""
ADK-like LLM Wrapper Tool

This tool simulates an ADK-compliant way to access an LLM, replacing direct
calls within the agents.
"""

from typing import Dict, Any
from adk_sim.adk_base import Tool, ToolContext
from openai import OpenAI
import json

class LLMWrapperTool(Tool):
    """
    Wraps the OpenAI-compatible client to provide an ADK-compliant LLM access tool.
    """
    
    def __init__(self):
        super().__init__(
            name="LLMWrapperTool",
            description="Accesses the LLM to generate natural language summaries or narratives based on a provided prompt."
        )
        self.context = ToolContext(self.name)
        self.llm_client = OpenAI()
        self.model = "gpt-4.1-mini"
    
    def run(self, system_prompt: str, user_prompt: str, is_json_output: bool = False, **kwargs) -> str:
        """
        Calls the LLM with the given prompts.
        
        Input:
            system_prompt: The system message for the LLM.
            user_prompt: The user message/task for the LLM.
            is_json_output: Whether the LLM should return a JSON object.
            
        Output:
            The LLM's response as a string (or JSON string if requested).
        """
        self.context.log("INFO", "Starting LLM call.", 
                         model=self.model, 
                         json_output=is_json_output)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        config = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
        }
        
        if is_json_output:
            config["response_format"] = {"type": "json_object"}
            
        try:
            response = self.llm_client.chat.completions.create(**config)
            llm_output = response.choices[0].message.content.strip()
            
            self.context.log("INFO", "LLM call complete.", 
                             tokens_used=response.usage.total_tokens)
            
            return llm_output
            
        except Exception as e:
            self.context.log("ERROR", "LLM call failed.", error=str(e))
            return f"LLM_ERROR: {str(e)}"

# --- Update DataValidationTool to use LLMWrapperTool ---

from adk_tools.data_validation_tool import DataValidationTool
from data_models import UserProfile, DebtPortfolio
from core.cashflow import CashflowAnalyzer

class DataValidationToolWithLLM(DataValidationTool):
    """DataValidationTool that uses the LLMWrapperTool for the summary."""
    
    def __init__(self, llm_tool: LLMWrapperTool):
        super().__init__()
        self.llm_tool = llm_tool
        self.name = "DataValidationTool" # Reset name after super() call
        self.context = ToolContext(self.name)
    
    def run(self, profile: UserProfile, debts: DebtPortfolio, **kwargs) -> Dict[str, Any]:
        
        # Run the base validation and cashflow analysis
        base_output = super().run(profile, debts, **kwargs)
        
        # Generate LLM-Powered Summary
        llm_summary = self._generate_llm_summary(
            profile, 
            debts, 
            base_output['cashflow_summary']
        )
        
        base_output['llm_financial_summary'] = llm_summary
        return base_output
    
    def _generate_llm_summary(
        self, 
        profile: UserProfile, 
        debts: DebtPortfolio, 
        cashflow_summary: Dict[str, Any]
    ) -> str:
        """
        Uses the LLMWrapperTool to generate a natural language summary.
        """
        
        # Prepare a concise prompt with key data
        user_prompt = f"""
        Analyze the following financial data for a user seeking debt deleveraging advice.
        
        **User Profile:**
        - Risk Tolerance: {profile.risk_tolerance.value}
        - Current Savings: ${profile.current_savings:,.2f}
        - Emergency Fund Target: ${profile.emergency_fund_target():,.2f}
        
        **Cashflow Summary:**
        - Monthly Income: ${cashflow_summary['monthly_income']:,.2f}
        - Monthly Obligations (Expenses + Minimum Payments): ${cashflow_summary['monthly_obligations']:,.2f}
        - Monthly Surplus: ${cashflow_summary['monthly_surplus']:,.2f}
        - Cashflow Health: {cashflow_summary['cashflow_health']}
        - Debt-to-Income Ratio (DTI): {cashflow_summary['debt_to_income_ratio']:.2f}
        
        **Debt Portfolio:**
        - Total Debt Balance: ${debts.total_balance():,.2f}
        - Weighted Avg. Interest Rate: {debts.weighted_average_interest_rate():.2%}
        - Red Flags: {cashflow_summary['red_flags']}
        
        **Task:** Write a concise, professional, and encouraging paragraph (max 4 sentences) summarizing the user's financial health. Highlight the main strength and the most critical area for improvement (e.g., high-interest debt or low emergency fund).
        """
        
        system_prompt = "You are a professional financial analyst. Your tone is objective, encouraging, and focused on actionable insights."
        
        return self.llm_tool.run(system_prompt, user_prompt, is_json_output=False)

# --- Update NarrativeTool to use LLMWrapperTool ---

from adk_tools.narrative_tool import NarrativeTool
from data_models import PlanOutput

class NarrativeToolWithLLM(NarrativeTool):
    """NarrativeTool that uses the LLMWrapperTool for the final narrative."""
    
    def __init__(self, llm_tool: LLMWrapperTool):
        super().__init__()
        self.llm_tool = llm_tool
        self.name = "NarrativeTool" # Reset name after super() call
        self.context = ToolContext(self.name)
    
    def run(self, plan_output: PlanOutput, llm_financial_summary: str, **kwargs) -> Dict[str, Any]:
        
        # Generate LLM-Powered Narrative
        llm_narrative_output = self._generate_llm_narrative(
            plan_output, 
            llm_financial_summary
        )
        
        # Combine with structured data
        final_narrative = {
            'executive_summary': llm_narrative_output.get('executive_summary', plan_output.executive_summary),
            'tradeoff_analysis_summary': llm_narrative_output.get('tradeoff_analysis_summary', plan_output.tradeoff_analysis),
            'action_steps': plan_output.action_steps,
            'comparison_table': plan_output.get_comparison_table(),
            'disclaimer': plan_output.disclaimer,
            'warnings': plan_output.recommended_plan.warnings,
        }
        
        self.context.log("INFO", "Narrative generation complete.")
        
        return {
            'final_narrative': final_narrative
        }
    
    def _generate_llm_narrative(
        self, 
        plan_output: PlanOutput, 
        llm_financial_summary: str
    ) -> Dict[str, str]:
        """
        Uses the LLMWrapperTool to generate the final executive summary and tradeoff analysis.
        """
        
        plan = plan_output.recommended_plan
        
        # Prepare the prompt with all the structured data
        user_prompt = f"""
        You are a financial coach writing the final report for a client. Your goal is to be clear, compliant, and persuasive.
        
        **Financial Health Summary (from Data Validation Agent):**
        {llm_financial_summary}
        
        **Recommended Plan Details:**
        - Strategy: {plan.strategy.value.title()}
        - Monthly Surplus: ${plan.monthly_surplus:,.2f}
        - Allocation: {plan.debt_allocation_percentage:.0%} Debt / {plan.etf_allocation_percentage:.0%} ETF
        - Extra Debt Payment: ${plan.monthly_extra_debt_payment:,.2f}
        - ETF Contribution: ${plan.monthly_etf_contribution:,.2f}
        - Estimated Months to Debt-Free: {plan.estimated_months_to_debt_free:.0f}
        - Total Interest Saved (vs. minimums): ${plan.total_interest_saved:,.2f}
        - Estimated ETF Value (Medium): ${plan.estimated_etf_value_medium:,.2f}
        
        **Scenario Comparison (Key Metrics):**
        - Debt-Only (100% Debt): {plan_output.debt_only_scenario.months_to_debt_free:.0f} months to debt-free, ${plan_output.debt_only_scenario.net_worth_at_end_medium:,.2f} estimated net worth.
        - Balanced (70/30 Split): {plan_output.balanced_scenario.months_to_debt_free:.0f} months to debt-free, ${plan_output.balanced_scenario.net_worth_at_end_medium:,.2f} estimated net worth.
        
        **Tasks:**
        1. **Executive Summary:** Write a 3-4 sentence executive summary that combines the financial health summary with the key outcomes of the recommended plan. Emphasize the benefit (e.g., time saved, interest saved).
        2. **Tradeoff Analysis Summary:** Write a 2-3 sentence summary of the tradeoff between the Debt-Only and Balanced scenarios. Explain the cost (time/interest) of investing early versus the potential benefit (net worth).
        
        **Output Format:** Return a JSON object with two keys: "executive_summary" and "tradeoff_analysis_summary". Do not include any other text.
        """
        
        system_prompt = "You are a professional financial coach. Your output must be a valid JSON object with the keys 'executive_summary' and 'tradeoff_analysis_summary'. All numbers must be formatted with commas and two decimal places (e.g., $1,234.56)."
        
        llm_response = self.llm_tool.run(system_prompt, user_prompt, is_json_output=True)
        
        try:
            return json.loads(llm_response)
        except json.JSONDecodeError:
            self.context.log("ERROR", "Failed to parse LLM JSON response.")
            return {}
