"""
REST API Interface

Provides a simple REST API for the debt deleveraging bot using Flask.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify
from data_models import (
    UserProfile, IncomeStream, Expense, Debt, DebtPortfolio,
    RiskTolerance, PayFrequency, DebtType, PayoffStrategy
)
from core import MultiAgentOrchestrator

app = Flask(__name__)


def parse_user_profile(data: dict) -> UserProfile:
    """Parse user profile from JSON data."""
    income_streams = [
        IncomeStream(
            name=stream['name'],
            amount=stream['amount'],
            frequency=PayFrequency(stream['frequency'])
        )
        for stream in data.get('income_streams', [])
    ]
    
    expenses = [
        Expense(
            name=exp['name'],
            amount=exp['amount'],
            is_essential=exp.get('is_essential', True)
        )
        for exp in data.get('expenses', [])
    ]
    
    return UserProfile(
        income_streams=income_streams,
        expenses=expenses,
        current_savings=data.get('current_savings', 0.0),
        current_investments=data.get('current_investments', 0.0),
        risk_tolerance=RiskTolerance(data.get('risk_tolerance', 'conservative')),
        time_horizon_months=data.get('time_horizon_months', 60),
        emergency_fund_months=data.get('emergency_fund_months', 3.0)
    )


def parse_debt_portfolio(data: dict) -> DebtPortfolio:
    """Parse debt portfolio from JSON data."""
    debts = [
        Debt(
            name=debt['name'],
            debt_type=DebtType(debt['debt_type']),
            current_balance=debt['current_balance'],
            annual_interest_rate=debt['annual_interest_rate'],
            minimum_payment=debt['minimum_payment'],
            due_day=debt.get('due_day', 1)
        )
        for debt in data.get('debts', [])
    ]
    
    return DebtPortfolio(debts=debts)


def serialize_orchestrator_output(output) -> dict:
    """Serialize the MultiAgentOrchestrator output to JSON-compatible dict."""
    
    if 'error' in output:
        return {
            'status': 'error',
            'message': output['error'],
            'validation_warnings': output['warnings'],
            'llm_financial_summary': output['llm_summary']
        }
    
    # Extract data from the Orchestrator output
    narrative = output['final_narrative']
    plan_output = output['full_plan_output']
    plan = plan_output.recommended_plan
    
    return {
        'status': 'success',
        'disclaimer': plan_output.disclaimer,
        'executive_summary': narrative['executive_summary'],
        'detailed_explanation': plan_output.detailed_explanation,
        'tradeoff_analysis_summary': narrative['tradeoff_analysis_summary'],
        'action_steps': narrative['action_steps'],
        'validation_warnings': output['validation_warnings'],
        'recommended_plan': {
            'strategy': plan.strategy.value,
            'monthly_surplus': plan.monthly_surplus,
            'debt_allocation_percentage': plan.debt_allocation_percentage,
            'etf_allocation_percentage': plan.etf_allocation_percentage,
            'monthly_extra_debt_payment': plan.monthly_extra_debt_payment,
            'monthly_etf_contribution': plan.monthly_etf_contribution,
            'estimated_months_to_debt_free': plan.estimated_months_to_debt_free,
            'total_interest_paid': plan.total_interest_paid,
            'total_interest_saved': plan.total_interest_saved,
            'estimated_etf_value_low': plan.estimated_etf_value_low,
            'estimated_etf_value_medium': plan.estimated_etf_value_medium,
            'estimated_etf_value_high': plan.estimated_etf_value_high,
            'etf_allocations': [
                {
                    'category': alloc.category,
                    'percentage': alloc.percentage,
                    'example_ticker': alloc.example_ticker,
                    'description': alloc.description
                }
                for alloc in plan.etf_allocations
            ],
            'recommendations': plan.recommendations,
        },
        'scenarios': {
            'minimum_only': serialize_scenario(plan_output.minimum_only_scenario) if plan_output.minimum_only_scenario else None,
            'debt_only': serialize_scenario(plan_output.debt_only_scenario) if plan_output.debt_only_scenario else None,
            'balanced': serialize_scenario(plan_output.balanced_scenario) if plan_output.balanced_scenario else None,
        }
    }


def serialize_scenario(scenario) -> dict:
    """Serialize ScenarioComparison to JSON-compatible dict."""
    return {
        'scenario_name': scenario.scenario_name,
        'months_to_debt_free': scenario.months_to_debt_free,
        'total_interest_paid': scenario.total_interest_paid,
        'total_debt_payments': scenario.total_debt_payments,
        'total_etf_contributions': scenario.total_etf_contributions,
        'estimated_etf_value_low': scenario.estimated_etf_value_low,
        'estimated_etf_value_medium': scenario.estimated_etf_value_medium,
        'estimated_etf_value_high': scenario.estimated_etf_value_high,
        'net_worth_at_end_low': scenario.net_worth_at_end_low,
        'net_worth_at_end_medium': scenario.net_worth_at_end_medium,
        'net_worth_at_end_high': scenario.net_worth_at_end_high,
        'description': scenario.description,
    }


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'debt-deleveraging-bot'})


@app.route('/api/v1/plan', methods=['POST'])
def create_plan():
    """
    Create a debt deleveraging plan.
    
    Expected JSON body:
    {
        "profile": { ... user profile data ... },
        "debts": { ... debt portfolio data ... },
        "strategy": "avalanche" | "snowball" | "hybrid"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Parse inputs
        profile = parse_user_profile(data.get('profile', {}))
        debts = parse_debt_portfolio(data.get('debts', {}))
        strategy = PayoffStrategy(data.get('strategy', 'avalanche'))
        
        # Create orchestrator
        orchestrator = MultiAgentOrchestrator()
        
        # Generate plan
        output = orchestrator.run_plan(profile, debts, strategy)
        
        # Serialize and return
        result = serialize_orchestrator_output(output)
        
        if result['status'] == 'error':
            return jsonify(result), 400
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# The cashflow and debt analysis endpoints are removed as the MultiAgentOrchestrator
# now handles the entire planning process, including validation and analysis.
# Users should use the /api/v1/plan endpoint for all requests.


if __name__ == '__main__':
    # Run in development mode
    # For production, use a proper WSGI server like gunicorn
    app.run(host='0.0.0.0', port=5000, debug=True)
