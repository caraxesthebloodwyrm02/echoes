import os
import re
from pathlib import Path

renamed_modules = {
    'capnproto': 'agent_capnproto',
    'code': 'agent_code',
    'crystal': 'agent_crystal',
    'discord': 'agent_discord',
    'erlang': 'agent_erlang',
    'fortran': 'agent_fortran',
    'go': 'agent_go',
    'graphql': 'agent_graphql',
    'gzip': 'agent_gzip',
    'haskell': 'agent_haskell',
    'irc': 'agent_irc',
    'iterTools': 'agent_iterTools',
    'javascript': 'agent_javascript',
    'julia': 'agent_julia',
    'lisp': 'agent_lisp',
    'matlab': 'agent_matlab',
    'mips': 'agent_mips',
    'orc': 'agent_orc',
    'parquet': 'agent_parquet',
    'perl': 'agent_perl',
    'php': 'agent_php',
    'plistlib': 'agent_plistlib',
    'pony': 'agent_pony',
    'python': 'agent_python',
    'r': 'agent_r',
    'resource': 'agent_resource',
    'ruby': 'agent_ruby',
    'rust': 'agent_rust',
    'scheme': 'agent_scheme',
    'secrets': 'agent_secrets',
    'slack': 'agent_slack',
    'solidity': 'agent_solidity',
    'spectral': 'agent_spectral',
    'sql': 'agent_sql',
    'statistics': 'agent_statistics',
    'telegram': 'agent_telegram',
    'tls': 'agent_tls',
    'toml': 'agent_toml',
    'validators': 'agent_validators',
    'vector': 'agent_vector',
    'vyper': 'agent_vyper',
    'wren': 'agent_wren',
    'zig': 'agent_zig',
def update_imports_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    original_content = content
    changes_made = []
    
    patterns = [
        (r'import\s+({})\b', r'import agent_\1'),
        (r'import\s+({}),', r'import agent_\1,'),
        (r'from\s+({})\s+import', r'from agent_\1 import'),
        (r'from\s+({})\.', r'from agent_\1.'),
    ]
    
    for old_name, new_name in renamed_modules.items():
        for pattern, replacement in patterns:
            actual_pattern = pattern.format(re.escape(old_name))
            actual_replacement = replacement.replace('agent_', f'agent_')
            content, count = re.subn(actual_pattern, actual_replacement, content)
            if count > 0:
                changes_made.append(f"Updated {count} import(s) of '{old_name}' to '{new_name}'")
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, changes_made
    
    return False, []

def find_and_update_imports(project_path):
    updated_files = []
    total_changes = []
    
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', '.venv', 'venv']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                updated, changes = update_imports_in_file(file_path)
                if updated:
                    updated_files.append(file_path)
                    total_changes.extend(changes)
    
    return updated_files, total_changes

if __name__ == "__main__":
    project_path = os.path.dirname(os.path.abspath(__file__))
    print("Updating import statements...")
    
    updated_files, changes = find_and_update_imports(project_path)
    
    if updated_files:
        print(f"\nUpdated {len(updated_files)} files:")
        for file in updated_files:
            print(f"  - {os.path.relpath(file)}")
        
        print(f"\nTotal import changes: {len(changes)}")
        for change in changes:
            print(f"  {change}")
    else:
        print("No import statements needed updating.")
