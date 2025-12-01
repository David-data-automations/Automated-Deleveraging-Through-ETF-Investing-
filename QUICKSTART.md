# Quick Start Guide

## Get Started in 3 Steps

### 1. Run the Example

```bash
cd debt-deleveraging-bot
python3 interfaces/cli.py
```

This will run a complete example scenario and show you:
- Your financial overview
- Recommended debt payoff strategy
- ETF investment allocation
- Scenario comparisons
- Step-by-step action plan

### 2. Run the Tests

```bash
python3 -m unittest discover tests -v
```

All 30 tests should pass, demonstrating that the system is working correctly.

### 3. Try the API (Optional)

Install Flask:
```bash
pip3 install flask
```

Start the API server:
```bash
python3 interfaces/api.py
```

Test the API:
```bash
curl -X POST http://localhost:5000/api/v1/plan \
  -H "Content-Type: application/json" \
  -d @examples/sample_input.json
```

## What You'll See

The bot will analyze your financial situation and provide:

1. **Executive Summary**: A high-level overview of your situation and recommended plan
2. **Detailed Analysis**: Complete breakdown of income, expenses, debts, and cashflow
3. **Recommended Plan**: Specific monthly amounts for debt payments and ETF investing
4. **Scenario Comparison**: Side-by-side comparison of different approaches
5. **Action Steps**: Clear, numbered steps to implement your plan

## Customizing for Your Situation

To use with your own data, modify the example in `interfaces/cli.py` or create a JSON file following the format in `examples/sample_input.json`.

### Key Data Points Needed

**Income:**
- Source name
- Amount per pay period
- Pay frequency (weekly, bi-weekly, monthly, etc.)

**Expenses:**
- Name
- Monthly amount
- Whether it's essential or discretionary

**Debts:**
- Name and type
- Current balance
- Annual interest rate (as decimal, e.g., 0.18 for 18%)
- Minimum monthly payment

**Profile:**
- Current savings
- Current investments
- Risk tolerance (conservative, moderate, aggressive)
- Time horizon in months

## Understanding the Output

**Avalanche Strategy**: Pays highest interest rate debts first (mathematically optimal)

**Snowball Strategy**: Pays smallest balances first (psychological wins)

**Hybrid Strategy**: Combines both approaches

**Allocation Percentages**: The bot automatically determines how much of your surplus should go to debt vs. ETF investing based on:
- Your debt interest rates
- Your risk tolerance
- Your emergency fund status
- Expected market returns

## Important Notes

⚠️ **This is educational planning only** - not financial advice

✓ All projections are estimates and not guaranteed

✓ The bot will warn you about red flags like negative cashflow or inadequate emergency funds

✓ ETF tickers shown are examples only - do your own research before investing

## Need Help?

See the full README.md for complete documentation, or review PROJECT_SUMMARY.md for an overview of how the system works.
