"""
ADK-like Sequential Agent Orchestrator

Defines the top-level SequentialAgent for the debt deleveraging bot.
"""

from adk_sim.adk_base import SequentialAgent, Tool
from adk_tools.llm_wrapper_tool import LLMWrapperTool, DataValidationToolWithLLM, NarrativeToolWithLLM
from adk_tools.planning_simulation_tool import PlanningSimulationTool
from typing import List

def create_deleveraging_agent() -> SequentialAgent:
    """
    Creates and configures the SequentialAgent with all necessary tools.
    
    The agent is defined by the sequence of tools it will execute.
    """
    
    # 1. Initialize the shared LLM Tool
    llm_tool = LLMWrapperTool()
    
    # 2. Initialize the core tools
    tools: List[Tool] = [
        # Tool 1: Data Validation and LLM Summary
        DataValidationToolWithLLM(llm_tool=llm_tool),
        
        # Tool 2: Core Financial Planning and Simulation
        PlanningSimulationTool(),
        
        # Tool 3: Final Narrative Generation (uses LLM)
        NarrativeToolWithLLM(llm_tool=llm_tool),
    ]
    
    # 3. Create the SequentialAgent
    deleveraging_agent = SequentialAgent(
        name="DeleveragingCoachAgent",
        tools=tools
    )
    
    return deleveraging_agent
