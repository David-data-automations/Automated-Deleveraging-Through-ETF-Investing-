"""
Configuration Settings

Configurable parameters for the debt deleveraging bot.
"""

# Interest rate thresholds
HIGH_INTEREST_THRESHOLD = 0.20  # 20% APR - very high interest
VERY_HIGH_INTEREST_THRESHOLD = 0.15  # 15% APR - high interest
MODERATE_INTEREST_THRESHOLD = 0.10  # 10% APR - moderate interest

# Expected market returns (annual)
CONSERVATIVE_MARKET_RETURN = 0.06  # 6%
MODERATE_MARKET_RETURN = 0.08      # 8%
AGGRESSIVE_MARKET_RETURN = 0.10    # 10%

# Conservative return estimates for simulations
CONSERVATIVE_RETURN_LOW = 0.03     # 3%
CONSERVATIVE_RETURN_MED = 0.05     # 5%
CONSERVATIVE_RETURN_HIGH = 0.07    # 7%

MODERATE_RETURN_LOW = 0.04         # 4%
MODERATE_RETURN_MED = 0.07         # 7%
MODERATE_RETURN_HIGH = 0.10        # 10%

AGGRESSIVE_RETURN_LOW = 0.05       # 5%
AGGRESSIVE_RETURN_MED = 0.08       # 8%
AGGRESSIVE_RETURN_HIGH = 0.12      # 12%

# Safety margins
DEFAULT_SAFETY_MARGIN = 0.10       # 10% safety margin on surplus
EMERGENCY_FUND_MONTHS = 3.0        # Recommended emergency fund

# Simulation parameters
MAX_SIMULATION_MONTHS = 600        # 50 years maximum

# Hybrid strategy threshold
HYBRID_BALANCE_THRESHOLD = 1000.0  # Balance threshold for hybrid strategy

# Disclaimer text
DISCLAIMER = (
    "IMPORTANT DISCLAIMER: This tool provides educational planning estimates only "
    "and is not financial, investment, tax, or legal advice. All projections are "
    "hypothetical and not guaranteed. Actual results may vary significantly. "
    "Consider consulting a qualified financial professional before making financial decisions."
)

# ETF recommendations by risk tolerance
ETF_RECOMMENDATIONS = {
    'conservative': [
        {
            'category': 'Bond Index',
            'percentage': 0.50,
            'example_ticker': 'BND',
            'description': 'Broad U.S. investment-grade bonds for stability'
        },
        {
            'category': 'Total Market Index',
            'percentage': 0.40,
            'example_ticker': 'VTI',
            'description': 'Broad U.S. stock market exposure'
        },
        {
            'category': 'International Bonds',
            'percentage': 0.10,
            'example_ticker': 'BNDX',
            'description': 'International investment-grade bonds for diversification'
        },
    ],
    'moderate': [
        {
            'category': 'Total Market Index',
            'percentage': 0.50,
            'example_ticker': 'VTI',
            'description': 'Broad U.S. stock market exposure'
        },
        {
            'category': 'Bond Index',
            'percentage': 0.30,
            'example_ticker': 'BND',
            'description': 'U.S. investment-grade bonds for stability'
        },
        {
            'category': 'International Stock Index',
            'percentage': 0.20,
            'example_ticker': 'VXUS',
            'description': 'International stock market diversification'
        },
    ],
    'aggressive': [
        {
            'category': 'Total Market Index',
            'percentage': 0.60,
            'example_ticker': 'VTI',
            'description': 'Broad U.S. stock market exposure'
        },
        {
            'category': 'International Stock Index',
            'percentage': 0.25,
            'example_ticker': 'VXUS',
            'description': 'International stock market diversification'
        },
        {
            'category': 'Bond Index',
            'percentage': 0.15,
            'example_ticker': 'BND',
            'description': 'U.S. investment-grade bonds for some stability'
        },
    ],
}
