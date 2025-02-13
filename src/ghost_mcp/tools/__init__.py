"""Ghost MCP tools package.

This module dynamically imports all tools from Python files in this directory.
It automatically discovers and imports all non-private functions and variables,
making them available at the package level.

When adding new tools:
1. Create new Python files in this directory
2. Define your tools as functions in these files
3. No need to modify this file - tools will be imported automatically
"""

from importlib import import_module
from pathlib import Path
from typing import Dict, Any

def _import_submodules() -> Dict[str, Any]:
    """Dynamically import all modules from the current package.
    
    Returns:
        Dict mapping module names to imported module objects
    
    Raises:
        FileNotFoundError: If the directory doesn't exist
    """
    current_dir = Path(__file__).parent
    
    if not current_dir.exists():
        raise FileNotFoundError(f"Tools directory not found at: {current_dir}")
    
    modules: Dict[str, Any] = {}
    for py_file in current_dir.glob('*.py'):
        if py_file.name.startswith('__'):
            continue
            
        module_name = py_file.stem
        
        # Import the module
        module = import_module(f".{module_name}", package="ghost_mcp.tools")
        modules[module_name] = module
        
        # Get all non-private attributes
        for attr_name in dir(module):
            if not attr_name.startswith('_'):
                # Add to the current module's namespace
                globals()[attr_name] = getattr(module, attr_name)
    
    return modules

# Run the dynamic imports
_import_submodules()

# Create sorted __all__ from the imported attributes for consistent ordering
__all__ = sorted(name for name in globals() if not name.startswith('_'))
