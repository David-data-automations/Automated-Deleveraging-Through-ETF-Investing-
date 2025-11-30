# Automated-Deleveraging-Through-ETF-Investing-
An autonomous agent that analyzes a user’s debt, income, and cashflow, then generates an optimized payoff plan powered by safe ETF-based automation. It validates inputs, simulates scenarios, and produces a clear narrative plan designed to accelerate deleveraging and improve long-term financial stability.

Automated Deleveraging Through ETF Investing

This project implements a Google-native, ADK-compatible, multi-agent system designed to analyze a user’s financial profile, simulate debt payoff strategies, and generate an accelerated deleveraging plan using ETF-based compounding.
All logic is organized using the Agent Developer Kit (ADK), with tools, workflows, agents, and orchestration patterns aligned to Google’s recommended architecture for production-grade agentic systems.

This repository serves as the primary codebase for the Kaggle Agents Intensive Capstone Project submission.

⸻

1. Overview

Traditional debt-payoff tools treat budgeting and investing as separate processes.
This agent system asks a fundamental question:

Can debt payoff be accelerated by allocating a portion of surplus income into diversified ETFs, compounding the growth, and recycling gains back into principal reduction?

The system:
	•	Collects and validates user inputs
	•	Analyzes income, expenses, and liabilities using deterministic ADK tools
	•	Simulates multiple debt payoff strategies (snowball, avalanche, hybrid)
	•	Runs ETF allocation and growth modeling
	•	Compares baseline versus ETF-accelerated payoff timelines
	•	Produces a structured narrative plan using a Google LLM agent
	•	Executes all reasoning inside a modular, domain-agnostic ADK workflow

⸻

2. Built for Google’s ADK and Agent Engine

The system adheres to the full ADK structure:
	•	FunctionTools for deterministic financial calculations
	•	Long-running tools for multi-step simulations
	•	Sequential and loop-based agent workflows
	•	Structured events, tool responses, and models
	•	Session handling via the ADK Runner and SessionService
	•	Memory-ready (searchable memory bank)
	•	Built-in logging hooks and future Cloud Trace compatibility
	•	Modular, domain-agnostic architecture for portability

  project-root/
│
├── config/                     
│   ├── adk_config.yaml          # Agent Engine / ADK settings
│   ├── domain_config.yaml       # Active domain: personal finance
│   └── risk_profiles.yaml
│
├── core/
│   ├── tools/                   # ADK FunctionTools
│   │   ├── cashflow_tool.py
│   │   ├── payoff_tool.py
│   │   ├── etf_allocation_tool.py
│   │   ├── simulation_tool.py
│   │   └── validation_tool.py
│   │
│   ├── agents/                  # LLM Agents + Workflow Agents
│   │   ├── validation_agent.py
│   │   ├── planning_agent.py
│   │   ├── simulation_agent.py
│   │   ├── narrative_agent.py
│   │   └── orchestrator_agent.py
│   │
│   ├── workflows/
│   │   ├── sequential_workflow.py
│   │   └── simulation_workflow.py
│   │
│   └── utils/
│       ├── data_models.py
│       ├── calculators.py
│       └── logger.py
│
├── interfaces/
│   ├── notebook_demo.ipynb      # Kaggle-facing entrypoint
│   └── cli.py
│
├── tests/
│   ├── test_cashflow.py
│   ├── test_payoff.py
│   ├── test_etf_allocation.py
│   └── test_simulation.py
│
├── requirements.txt
└── README.md

4. System Components

4.1. ADK Tools

Deterministic, testable financial functions:
	•	cashflow_tool
Computes surplus income, debt-to-income ratios, and feasibility metrics.
	•	payoff_tool
Avalanche, snowball, and hybrid payoff logic.
	•	etf_allocation_tool
Maps risk tolerance to ETF allocations and constraints.
	•	simulation_tool
Simulates month-by-month payoff with ETF growth recycling.
	•	validation_tool
Ensures debt, income, and risk data meet safety rules applied by the system.

All tools return structured dictionaries using ADK schema conventions.

4.2. Agents
	•	Validation Agent: Handles input validation through ADK event-driven checks.
	•	Planning Agent: Prepares parameters, computes strategy, chooses payoff method.
	•	Simulation Agent: Uses long-running tool calls for multi-month simulation.
	•	Narrative Agent: Generates a final explanation summarizing the results.
	•	Orchestrator Agent: Controls the sequential workflow and tool call order.

4.3. Workflows

The complete user flow is implemented as a Sequential Workflow Agent:
	1.	Validate user inputs
	2.	Compute cashflow
	3.	Evaluate debt strategies
	4.	Apply ETF allocation rules
	5.	Run payoff simulation (baseline vs ETF-accelerated)
	6.	Generate narrative output

All of the above follow ADK best practices for large workflows.

5. Running the System

Local execution
interfaces/notebook_demo.ipynb

The notebook walks the user through the full interaction pipeline.

6. For Kaggle Reviewers: Competition Context

This project is submitted to the Agents Intensive – Capstone Project, and satisfies the required elements:
	•	Clear problem definition
	•	Google-aligned multi-agent architecture
	•	ADK tools and workflows
	•	Detailing of system design, reasoning structure, and safety constraints
	•	Notebook-based demo
	•	Public GitHub repository supporting reproducibility

The repository demonstrates the application of ADK design patterns to a real-world financial use case with measurable user impact.

⸻

7. Limitations and Safety
	•	This system is for research and educational use.
	•	ETF performance is simulated, not predicted.
	•	Debt reduction paths are mathematical models, not financial advice.
	•	Real-world application would require significant regulatory review.
	•	Safety constraints ensure emergency fund preservation and input sanity checks.

⸻

8. Roadmap
	•	Add memory integration via ADK MemoryService
	•	Add Cloud Trace observability
	•	Connect to live ETF APIs
	•	Add multi-session longitudinal tracking
	•	Add progressive risk-based rebalancing logic
	•	Integrate with Google Agent Engine for deployment

⸻

9. License

MIT License

Copyright (c) 2025 David Ortiz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
