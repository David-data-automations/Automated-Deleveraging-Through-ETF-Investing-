"""
ADK Simulation Base Classes

These classes simulate the core interface of the Google Agent Development Kit (ADK)
to demonstrate the required structure and compliance without needing the actual library.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable, Optional
import json

# --- ADK Tool Simulation ---

class Tool(ABC):
    """Simulates the base Tool class from ADK."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        
    @abstractmethod
    def run(self, **kwargs) -> Any:
        """The main execution method for the tool."""
        pass

class FunctionTool(Tool):
    """Simulates the FunctionTool class from ADK."""
    
    def __init__(self, name: str, description: str, func: Callable, input_schema: Dict[str, Any]):
        super().__init__(name, description)
        self.func = func
        self.input_schema = input_schema
        
    def run(self, **kwargs) -> Any:
        """Executes the wrapped function."""
        # In a real ADK, validation against the schema would happen here.
        # We'll just call the function for simulation.
        return self.func(**kwargs)

# --- ADK Agent Simulation ---

class SequentialAgent:
    """Simulates the SequentialAgent class from ADK."""
    
    def __init__(self, name: str, tools: List[Tool]):
        self.name = name
        self.tools = tools
        
    def run(self, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the tools sequentially, passing the output of one as the input
        to the next. This simulates the sequential agent workflow.
        """
        print(f"ADK_SIM: SequentialAgent '{self.name}' starting...")
        current_output = initial_input
        
        for tool in self.tools:
            print(f"ADK_SIM: Running Tool '{tool.name}'...")
            
            # Simulate input mapping: pass all previous output to the next tool
            # The tool itself must know which keys it needs.
            try:
                tool_output = tool.run(**current_output)
                
                # Merge the tool's output into the current state
                if isinstance(tool_output, dict):
                    current_output.update(tool_output)
                else:
                    # Handle non-dict output by wrapping it
                    current_output[f"{tool.name}_result"] = tool_output
                    
            except Exception as e:
                print(f"ADK_SIM: Tool '{tool.name}' failed with error: {e}")
                current_output['error'] = f"Tool {tool.name} failed: {e}"
                return current_output # Stop on error
                
        print(f"ADK_SIM: SequentialAgent '{self.name}' finished.")
        return current_output

# --- ADK Runner Simulation ---

class Runner:
    """Simulates the Runner class from ADK, which executes the top-level agent."""
    
    def __init__(self, agent: SequentialAgent):
        self.agent = agent
        
    def run(self, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        """Starts the agent execution."""
        print("ADK_SIM: Runner starting execution...")
        return self.agent.run(initial_input)

# --- ADK Session/Context Simulation ---

class ToolContext:
    """Simulates the ToolContext object passed to ADK tools."""
    
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.session_id = "simulated_session_123"
        self.log = self._log
        
    def _log(self, level: str, message: str, **kwargs):
        """Simulates ADK logging/tracing."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "level": level.upper(),
            "tool": self.tool_name,
            "message": message,
            "details": kwargs
        }
        # Print to console to simulate Cloud Trace/ADK logging
        print(f"ADK_TRACE: {json.dumps(log_entry)}")

from datetime import datetime

# Cleanup the old logging module as we are replacing it
import os
if os.path.exists("/home/ubuntu/debt-deleveraging-bot/core/logger.py"):
    os.remove("/home/ubuntu/debt-deleveraging-bot/core/logger.py")
if os.path.exists("/home/ubuntu/debt-deleveraging-bot/agent_execution.log"):
    os.remove("/home/ubuntu/debt-deleveraging-bot/agent_execution.log")

# Create the adk_sim directory
import subprocess
subprocess.run(["mkdir", "-p", "/home/ubuntu/debt-deleveraging-bot/adk_sim"])
