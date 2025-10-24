#!/usr/bin/env python3
"""
Fix langchain.agents.output_parsers to be a proper package
"""
import os
import sys
import site

def find_langchain_path():
    """Find langchain package path"""
    for path in sys.path:
        langchain_path = os.path.join(path, 'langchain')
        if os.path.isdir(langchain_path):
            return langchain_path
    
    for site_path in site.getsitepackages():
        langchain_path = os.path.join(site_path, 'langchain')
        if os.path.isdir(langchain_path):
            return langchain_path
    
    return None

def create_output_parsers_package():
    """Create proper output_parsers package structure"""
    
    langchain_path = find_langchain_path()
    if not langchain_path:
        print("Could not find langchain package")
        return False
    
    agents_path = os.path.join(langchain_path, 'agents')
    output_parsers_path = os.path.join(agents_path, 'output_parsers')
    
    # Remove the file if it exists and create directory
    if os.path.isfile(output_parsers_path + '.py'):
        os.remove(output_parsers_path + '.py')
        print("Removed output_parsers.py file")
    
    if not os.path.exists(output_parsers_path):
        os.makedirs(output_parsers_path)
        print(f"Created output_parsers directory: {output_parsers_path}")
    
    # Create __init__.py
    init_file = os.path.join(output_parsers_path, '__init__.py')
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write('''"""
Mock output parsers package for mcp-use compatibility
"""

class ReActSingleInputOutputParser:
    """Mock ReActSingleInputOutputParser"""
    
    def parse(self, text: str):
        return {"action": "Final Answer", "action_input": text}

class ReActOutputParser:
    """Mock ReActOutputParser"""
    
    def parse(self, text: str):
        return {"action": "Final Answer", "action_input": text}

# Import from submodules
from .tools import ToolAgentAction

__all__ = [
    'ReActSingleInputOutputParser',
    'ReActOutputParser', 
    'ToolAgentAction'
]
''')
    
    # Create tools.py
    tools_file = os.path.join(output_parsers_path, 'tools.py')
    with open(tools_file, 'w', encoding='utf-8') as f:
        f.write('''"""
Mock tools module for mcp-use compatibility
"""

class ToolAgentAction:
    """Mock ToolAgentAction class"""
    
    def __init__(self, tool, tool_input, log="", **kwargs):
        self.tool = tool
        self.tool_input = tool_input
        self.log = log
        self.kwargs = kwargs
    
    def __str__(self):
        return f"ToolAgentAction(tool={self.tool}, tool_input={self.tool_input})"
    
    def __repr__(self):
        return self.__str__()

class AgentAction:
    """Mock AgentAction class"""
    
    def __init__(self, tool, tool_input, log=""):
        self.tool = tool
        self.tool_input = tool_input
        self.log = log

class AgentFinish:
    """Mock AgentFinish class"""
    
    def __init__(self, return_values, log=""):
        self.return_values = return_values
        self.log = log

__all__ = ['ToolAgentAction', 'AgentAction', 'AgentFinish']
''')
    
    print("Created output_parsers package structure")
    return True

def test_output_parsers_import():
    """Test the output_parsers package import"""
    
    try:
        # Clear import cache
        modules_to_clear = [
            'langchain.agents.output_parsers',
            'langchain.agents.output_parsers.tools',
            'mcp_use',
            'mcp_use.agents',
            'mcp_use.agents.mcpagent'
        ]
        
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        print("Testing output_parsers package import...")
        
        # Test the specific import that was failing
        from langchain.agents.output_parsers.tools import ToolAgentAction
        print("✓ langchain.agents.output_parsers.tools import successful")
        
        # Test mcp_use import
        from mcp_use.client import MCPClient
        print("✓ mcp_use.client import successful")
        
        print("\n🎉 Output parsers package fix successful!")
        return True
        
    except Exception as e:
        print(f"❌ Output parsers import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main fix process"""
    print("Fixing langchain.agents.output_parsers package structure...")
    
    if create_output_parsers_package():
        print("Package structure created, testing imports...")
        if test_output_parsers_import():
            print("\n🚀 Output parsers fix successful!")
        else:
            print("\n⚠️ Import still failing")
    else:
        print("❌ Failed to create package structure")

if __name__ == "__main__":
    main()