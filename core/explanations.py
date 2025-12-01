"""
Explanation and Narrative Generation

Generates human-readable explanations, summaries, and action plans.
"""

from typing import List
from data_models import (
    DebtPayoffPlan, ScenarioComparison, PlanOutput, 
    UserProfile, DebtPortfolio, PayoffStrategy
)
from core.cashflow import CashflowAnalyzer
from core.payoff_strategies import PayoffStrategyEngine


class NarrativeGenerator:
    """Generates human-readable explanations and narratives."""
    
    @staticmethod
    def generate_executive_summary(
        plan: DebtPayoffPlan,
        profile: UserProfile,
        debts: DebtPortfolio,
        cashflow: CashflowAnalyzer
    ) -> str:
        """
        Generate executive summary of the plan.
        
        Args:
            plan: The debt payoff plan
            profile: User profile
            debts: User debts
            cashflow: Cashflow analyzer
        
        Returns:
            Executive summary text
        """
        summary_parts = []
        
        # Opening
        summary_parts.append(
            f"Based on your financial profile, we've created a personalized debt "
            f"deleveraging plan using the {plan.strategy.value} strategy. "
        )
        
        # Current situation
        total_debt = debts.total_balance()
        avg_rate = debts.weighted_average_interest_rate()
        monthly_surplus = cashflow.monthly_surplus()
        
        summary_parts.append(
            f"You currently have ${total_debt:,.2f} in total debt across "
            f"{len(debts.debts)} account(s) with a weighted average interest rate "
            f"of {avg_rate:.2%}. Your monthly surplus after all expenses and "
            f"minimum payments is ${monthly_surplus:,.2f}."
        )
        
        # Allocation strategy
        debt_pct = plan.debt_allocation_percentage
        etf_pct = plan.etf_allocation_percentage
        
        if etf_pct > 0:
            summary_parts.append(
                f"We recommend allocating {debt_pct:.0%} of your surplus "
                f"(${plan.monthly_extra_debt_payment:,.2f}) to extra debt payments "
                f"and {etf_pct:.0%} (${plan.monthly_etf_contribution:,.2f}) to "
                f"ETF investing. "
            )
        else:
            summary_parts.append(
                f"We recommend allocating your full surplus "
                f"(${plan.monthly_extra_debt_payment:,.2f}) to extra debt payments. "
                f"Given your current debt profile, focusing on debt elimination "
                f"provides the best guaranteed return."
            )
        
        # Timeline
        if plan.estimated_months_to_debt_free:
            years = plan.estimated_months_to_debt_free / 12
            summary_parts.append(
                f"Following this plan, you could be debt-free in approximately "
                f"{plan.estimated_months_to_debt_free:.0f} months ({years:.1f} years), "
                f"paying an estimated ${plan.total_interest_paid:,.2f} in total interest."
            )
            
            if plan.total_interest_saved > 0:
                summary_parts.append(
                    f"This saves you approximately ${plan.total_interest_saved:,.2f} "
                    f"in interest compared to making only minimum payments."
                )
        
        # ETF projection
        if etf_pct > 0 and plan.estimated_etf_value_medium > 0:
            summary_parts.append(
                f"By the time you're debt-free, your ETF portfolio could grow to "
                f"approximately ${plan.estimated_etf_value_medium:,.2f} "
                f"(medium estimate, not guaranteed)."
            )
        
        return " ".join(summary_parts)
    
    @staticmethod
    def generate_detailed_explanation(
        plan: DebtPayoffPlan,
        profile: UserProfile,
        debts: DebtPortfolio,
        cashflow: CashflowAnalyzer
    ) -> str:
        """
        Generate detailed explanation of the plan and reasoning.
        
        Args:
            plan: The debt payoff plan
            profile: User profile
            debts: User debts
            cashflow: Cashflow analyzer
        
        Returns:
            Detailed explanation text
        """
        sections = []
        
        # Financial Overview
        sections.append("## Financial Overview\n")
        sections.append(
            f"**Monthly Income:** ${cashflow.monthly_gross_income():,.2f}\n"
            f"**Monthly Expenses:** ${cashflow.monthly_total_expenses():,.2f}\n"
            f"**Monthly Debt Minimums:** ${cashflow.monthly_minimum_debt_payments():,.2f}\n"
            f"**Monthly Surplus:** ${cashflow.monthly_surplus():,.2f}\n"
            f"**Cashflow Health:** {cashflow.cashflow_health_score().title()}\n"
        )
        
        # Debt Summary
        sections.append("\n## Debt Summary\n")
        sections.append(
            f"**Total Debt Balance:** ${debts.total_balance():,.2f}\n"
            f"**Number of Debts:** {len(debts.debts)}\n"
            f"**Weighted Avg Interest Rate:** {debts.weighted_average_interest_rate():.2%}\n"
            f"**Total Monthly Interest:** ${debts.total_monthly_interest():,.2f}\n"
        )
        
        # Individual debts
        sections.append("\n**Individual Debts:**\n")
        for debt in debts.debts:
            sections.append(
                f"- **{debt.name}** ({debt.debt_type.value}): "
                f"${debt.current_balance:,.2f} at {debt.annual_interest_rate:.2%} APR, "
                f"${debt.minimum_payment:,.2f} minimum payment\n"
            )
        
        # Strategy Explanation
        sections.append("\n## Payoff Strategy\n")
        sections.append(
            PayoffStrategyEngine.get_strategy_description(plan.strategy) + "\n"
        )
        
        # Allocation Rationale
        sections.append("\n## Allocation Rationale\n")
        if plan.etf_allocation_percentage > 0:
            sections.append(
                f"Your surplus is allocated {plan.debt_allocation_percentage:.0%} to debt "
                f"and {plan.etf_allocation_percentage:.0%} to ETF investing based on:\n"
                f"- Your risk tolerance: {profile.risk_tolerance.value}\n"
                f"- Your debt interest rates (avg {debts.weighted_average_interest_rate():.2%})\n"
                f"- Your emergency fund status\n"
                f"- Expected market returns vs guaranteed debt payoff returns\n"
            )
        else:
            sections.append(
                f"We recommend 100% allocation to debt payoff (no ETF investing) because:\n"
            )
            if not profile.has_adequate_emergency_fund():
                sections.append("- Your emergency fund is below recommended levels\n")
            if debts.has_high_interest_debt(0.15):
                sections.append(
                    f"- You have high-interest debt that exceeds typical market returns\n"
                )
        
        # Timeline and Projections
        sections.append("\n## Timeline and Projections\n")
        if plan.estimated_months_to_debt_free:
            sections.append(
                f"**Estimated Time to Debt-Free:** {plan.estimated_months_to_debt_free:.0f} months "
                f"({plan.estimated_months_to_debt_free/12:.1f} years)\n"
                f"**Total Interest Paid:** ${plan.total_interest_paid:,.2f}\n"
                f"**Interest Saved vs Minimums:** ${plan.total_interest_saved:,.2f}\n"
            )
        
        if plan.etf_allocation_percentage > 0:
            sections.append(
                f"\n**ETF Portfolio Projections** (illustrative, not guaranteed):\n"
                f"- Low estimate: ${plan.estimated_etf_value_low:,.2f}\n"
                f"- Medium estimate: ${plan.estimated_etf_value_medium:,.2f}\n"
                f"- High estimate: ${plan.estimated_etf_value_high:,.2f}\n"
            )
        
        return "".join(sections)
    
    @staticmethod
    def generate_tradeoff_analysis(
        minimum_only: ScenarioComparison,
        debt_only: ScenarioComparison,
        balanced: ScenarioComparison
    ) -> str:
        """
        Generate tradeoff analysis between scenarios.
        
        Args:
            minimum_only: Minimum payment scenario
            debt_only: 100% debt payoff scenario
            balanced: Balanced scenario
        
        Returns:
            Tradeoff analysis text
        """
        sections = []
        
        sections.append("## Scenario Comparison\n\n")
        sections.append(
            "We've analyzed three different approaches to help you understand "
            "the tradeoffs between aggressive debt payoff and building investments:\n\n"
        )
        
        # Minimum Only
        sections.append(f"### 1. {minimum_only.scenario_name}\n")
        sections.append(f"{minimum_only.description}\n\n")
        if minimum_only.months_to_debt_free:
            sections.append(
                f"- **Time to debt-free:** {minimum_only.months_to_debt_free:.0f} months\n"
                f"- **Total interest paid:** ${minimum_only.total_interest_paid:,.2f}\n"
                f"- **ETF value at end:** ${minimum_only.estimated_etf_value_medium:,.2f}\n"
                f"- **Net worth at end:** ${minimum_only.net_worth_at_end_medium:,.2f}\n\n"
            )
        else:
            sections.append("- **Time to debt-free:** Will not pay off with minimums only\n\n")
        
        # Debt Only
        sections.append(f"### 2. {debt_only.scenario_name}\n")
        sections.append(f"{debt_only.description}\n\n")
        if debt_only.months_to_debt_free:
            sections.append(
                f"- **Time to debt-free:** {debt_only.months_to_debt_free:.0f} months\n"
                f"- **Total interest paid:** ${debt_only.total_interest_paid:,.2f}\n"
                f"- **ETF value at end:** ${debt_only.estimated_etf_value_medium:,.2f}\n"
                f"- **Net worth at end:** ${debt_only.net_worth_at_end_medium:,.2f}\n\n"
            )
        
        # Balanced
        sections.append(f"### 3. {balanced.scenario_name}\n")
        sections.append(f"{balanced.description}\n\n")
        if balanced.months_to_debt_free:
            sections.append(
                f"- **Time to debt-free:** {balanced.months_to_debt_free:.0f} months\n"
                f"- **Total interest paid:** ${balanced.total_interest_paid:,.2f}\n"
                f"- **ETF value at end:** ${balanced.estimated_etf_value_medium:,.2f}\n"
                f"- **Net worth at end:** ${balanced.net_worth_at_end_medium:,.2f}\n\n"
            )
        
        # Key Insights
        sections.append("### Key Insights\n\n")
        
        if debt_only.months_to_debt_free and balanced.months_to_debt_free:
            month_diff = balanced.months_to_debt_free - debt_only.months_to_debt_free
            interest_diff = balanced.total_interest_paid - debt_only.total_interest_paid
            etf_diff = balanced.estimated_etf_value_medium - debt_only.estimated_etf_value_medium
            
            sections.append(
                f"The balanced approach takes approximately {month_diff:.0f} more months "
                f"to become debt-free and costs ${interest_diff:,.2f} more in interest, "
                f"but builds ${etf_diff:,.2f} more in ETF investments during the payoff period. "
            )
            
            if balanced.net_worth_at_end_medium > debt_only.net_worth_at_end_medium:
                net_worth_advantage = balanced.net_worth_at_end_medium - debt_only.net_worth_at_end_medium
                sections.append(
                    f"The balanced approach results in approximately ${net_worth_advantage:,.2f} "
                    f"higher net worth at the end (medium estimate, not guaranteed).\n"
                )
            else:
                sections.append(
                    f"The debt-only approach may result in higher net worth if you invest "
                    f"aggressively after becoming debt-free.\n"
                )
        
        return "".join(sections)
    
    @staticmethod
    def generate_action_steps(
        plan: DebtPayoffPlan,
        debts: DebtPortfolio
    ) -> List[str]:
        """
        Generate step-by-step action plan.
        
        Args:
            plan: The debt payoff plan
            debts: User debts
        
        Returns:
            List of action step strings
        """
        steps = []
        
        # Step 1: Set up automatic payments for minimums
        steps.append(
            f"Set up automatic minimum payments for all {len(debts.debts)} debts "
            f"(total ${debts.total_minimum_payments():,.2f}/month) to ensure no missed payments."
        )
        
        # Step 2: Extra debt payments
        if plan.monthly_extra_debt_payment > 0:
            # Determine priority debt
            prioritized = PayoffStrategyEngine.prioritize_debts(
                debts.debts,
                plan.strategy
            )
            if prioritized:
                priority_debt = prioritized[0]
                steps.append(
                    f"Pay an extra ${plan.monthly_extra_debt_payment:,.2f}/month toward "
                    f"{priority_debt.name} (highest priority under {plan.strategy.value} strategy)."
                )
        
        # Step 3: ETF investing
        if plan.monthly_etf_contribution > 0:
            steps.append(
                f"Set up automatic monthly investment of ${plan.monthly_etf_contribution:,.2f} "
                f"into your chosen ETF portfolio. Consider the recommended allocations below."
            )
            
            for allocation in plan.etf_allocations:
                steps.append(
                    f"  - {allocation.percentage:.0%} to {allocation.category} "
                    f"(e.g., {allocation.example_ticker}): {allocation.description}"
                )
        
        # Step 4: Review and adjust
        steps.append(
            "Review your plan monthly and adjust as your financial situation changes. "
            "Update balances, income, and expenses to recalculate your optimal strategy."
        )
        
        # Step 5: After debt payoff
        if plan.estimated_months_to_debt_free:
            total_freed_up = debts.total_minimum_payments() + plan.monthly_extra_debt_payment
            steps.append(
                f"Once debt-free, redirect the ${total_freed_up:,.2f}/month previously "
                f"going to debt payments into investments and other financial goals."
            )
        
        # Step 6: Emergency fund
        steps.append(
            "Maintain and build your emergency fund to cover 3-6 months of essential expenses. "
            "This provides a safety net and prevents new debt accumulation."
        )
        
        return steps
    
    @staticmethod
    def generate_complete_output(
        plan: DebtPayoffPlan,
        profile: UserProfile,
        debts: DebtPortfolio,
        cashflow: CashflowAnalyzer,
        minimum_only: ScenarioComparison,
        debt_only: ScenarioComparison,
        balanced: ScenarioComparison
    ) -> PlanOutput:
        """
        Generate complete plan output with all narratives.
        
        Args:
            plan: The recommended plan
            profile: User profile
            debts: User debts
            cashflow: Cashflow analyzer
            minimum_only: Minimum payment scenario
            debt_only: 100% debt scenario
            balanced: Balanced scenario
        
        Returns:
            Complete PlanOutput object
        """
        return PlanOutput(
            recommended_plan=plan,
            minimum_only_scenario=minimum_only,
            debt_only_scenario=debt_only,
            balanced_scenario=balanced,
            executive_summary=NarrativeGenerator.generate_executive_summary(
                plan, profile, debts, cashflow
            ),
            detailed_explanation=NarrativeGenerator.generate_detailed_explanation(
                plan, profile, debts, cashflow
            ),
            tradeoff_analysis=NarrativeGenerator.generate_tradeoff_analysis(
                minimum_only, debt_only, balanced
            ),
            action_steps=NarrativeGenerator.generate_action_steps(plan, debts)
        )
