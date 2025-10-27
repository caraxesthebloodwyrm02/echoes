import os
import sys
from pathlib import Path

def get_stdlib_modules():
    """Get a set of Python standard library module names"""
    import sysconfig
    import sys
    
    # Get standard library paths
    stdlib_paths = [
        Path(p) for p in sys.path 
        if 'site-packages' not in p and 'dist-packages' not in p
    ]
    
    # Common standard library modules
    stdlib = {
        # Built-in modules
        *sys.builtin_module_names,
        # Standard library modules
        'abc', 'argparse', 'ast', 'asyncio', 'base64', 'bisect', 'calendar', 
        'cmath', 'collections', 'contextlib', 'copy', 'csv', 'dataclasses', 
        'datetime', 'decimal', 'difflib', 'enum', 'functools', 'gc', 'hashlib', 
        'heapq', 'http', 'inspect', 'io', 'itertools', 'json', 'logging', 
        'math', 'os', 'pathlib', 'pickle', 'platform', 'random', 're', 
        'string', 'subprocess', 'sys', 'threading', 'time', 'tokenize', 
        'traceback', 'types', 'typing', 'unicodedata', 'urllib', 'warnings', 
        'weakref', 'xml', 'zipimport'
    }
    
    return stdlib

def find_shadowed_modules(project_path):
    """Find Python files in the project that shadow standard library modules"""
    stdlib = get_stdlib_modules()
    shadowed = []
    
    core_path = os.path.join(project_path, 'core')
    if not os.path.exists(core_path):
        return []
    
    for file in os.listdir(core_path):
        if file.endswith('.py') and not file.startswith('agent_'):
            module_name = file[:-3]  # Remove .py extension
            if module_name in stdlib:
                full_path = os.path.join(core_path, file)
                shadowed.append((module_name, full_path))
    
    return shadowed

def generate_report(shadowed_modules, output_file='shadowed_modules_report.txt'):
    """Generate a report of shadowed modules"""
    if not shadowed_modules:
        report = "No shadowed modules found!"
    else:
        report = [
            "# Shadowed Python Standard Library Modules Report\n",
            f"Found {len(shadowed_modules)} modules in core/ that shadow Python standard library names:\n"
        ]
        
        for module_name, file_path in sorted(shadowed_modules):
            rel_path = os.path.relpath(file_path)
            new_name = f"agent_{os.path.basename(file_path)}"
            new_path = os.path.join(os.path.dirname(file_path), new_name)
            
            report.extend([
                f"- {module_name}: {rel_path}",
                f"  Suggested rename: {os.path.basename(file_path)} -> {new_name}\n"
            ])
        
        report = "\n".join(report)
    
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"Report generated: {os.path.abspath(output_file)}")
    return report

if __name__ == "__main__":
    project_path = os.path.dirname(os.path.abspath(__file__))
    shadowed = find_shadowed_modules(project_path)
    report = generate_report(shadowed)
    print("\n" + report)
