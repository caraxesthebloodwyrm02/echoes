#!/usr/bin/env python3
"""
Token Blocking Function Detector
Identifies and eliminates functions that block iteration through token level limiting.
"""

import ast
import sys
import re
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

class TokenBlockingDetector:
    """Detects token blocking patterns that prevent proper token iteration."""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.token_blockers = []
        
        # Critical token blocking patterns
        self.token_blocking_patterns = {
            # Direct token overrides
            'DEFAULT_MAX_TOKENS',
            'default_max_tokens',
            'max_tokens.*default',
            'default.*max_tokens',
            
            # Token blocking logic
            'opts.max_tokens or DEFAULT',
            'max_tokens.*or.*DEFAULT',
            'max_tokens.*or.*default',
            'or DEFAULT_MAX_TOKENS',
            'or default_max_tokens',
            
            # Token limiting functions
            'limit.*token',
            'token.*limit',
            'block.*token',
            'token.*block',
            
            # Token iteration blocking
            'iteration.*block',
            'block.*iteration',
            'for.*token.*break',
            'while.*token.*break',
            
            # Token override mechanisms
            'override.*token',
            'token.*override',
            'parameter.*override',
            'override.*parameter'
        }
        
        # Suspicious token manipulation patterns
        self.suspicious_token_patterns = {
            'max_tokens.*=.*None',
            'max_tokens.*=.*4000',
            'max_tokens.*=.*DEFAULT',
            'Field.*default.*max_tokens',
            'description.*override.*default'
        }

    def scan_file(self, file_path: Path) -> Dict[str, Any]:
        """Scan a single file for token blocking patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = {
                'file': str(file_path),
                'token_constants': [],
                'token_blocking_logic': [],
                'token_override_patterns': [],
                'suspicious_patterns': []
            }
            
            # Check for token constants
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                # Check for DEFAULT_MAX_TOKENS constants
                if 'DEFAULT_MAX_TOKENS' in line and '=' in line:
                    issues['token_constants'].append({
                        'line': i,
                        'pattern': 'DEFAULT_MAX_TOKENS constant',
                        'code': line.strip()
                    })
                
                # Check for token blocking logic
                for pattern in self.token_blocking_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues['token_blocking_logic'].append({
                            'line': i,
                            'pattern': pattern,
                            'code': line.strip()
                        })
                
                # Check for suspicious token patterns
                for pattern in self.suspicious_token_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues['suspicious_patterns'].append({
                            'line': i,
                            'pattern': pattern,
                            'code': line.strip()
                        })
            
            # Parse AST for deeper analysis
            try:
                tree = ast.parse(content)
                self._analyze_token_ast(tree, file_path, issues)
            except SyntaxError:
                issues['syntax_error'] = True
            
            return issues
            
        except Exception as e:
            return {'file': str(file_path), 'error': str(e)}
    
    def _analyze_token_ast(self, tree: ast.AST, file_path: Path, issues: Dict[str, Any]):
        """Analyze AST for token blocking patterns."""
        
        class TokenBlockingVisitor(ast.NodeVisitor):
            def __init__(self):
                self.token_assignments = []
                self.token_or_operations = []
                self.token_defaults = []
            
            def visit_Assign(self, node):
                # Check for token assignments with defaults
                if isinstance(node.value, ast.NameConstant) and node.value.value == 4000:
                    for target in node.targets:
                        if isinstance(target, ast.Name) and 'token' in target.id.lower():
                            self.token_assignments.append({
                                'line': node.lineno,
                                'variable': target.id,
                                'value': 4000
                            })
                
                # Check for "or" operations with tokens
                if isinstance(node.value, ast.BoolOp) and isinstance(node.value.op, ast.Or):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and 'token' in target.id.lower():
                            self.token_or_operations.append({
                                'line': node.lineno,
                                'variable': target.id,
                                'has_or_logic': True
                            })
                
                self.generic_visit(node)
            
            def visit_If(self, node):
                # Check for token-related conditions
                if hasattr(node.test, 'left') and hasattr(node.test, 'ops'):
                    if isinstance(node.test.left, ast.Name) and 'token' in node.test.left.id.lower():
                        self.token_defaults.append({
                            'line': node.lineno,
                            'condition': 'token_if_condition'
                        })
                
                self.generic_visit(node)
        
        visitor = TokenBlockingVisitor()
        visitor.visit(tree)
        
        # Add AST-based findings
        if visitor.token_assignments:
            issues['token_assignments'] = visitor.token_assignments
        
        if visitor.token_or_operations:
            issues['token_or_operations'] = visitor.token_or_operations
        
        if visitor.token_defaults:
            issues['token_defaults'] = visitor.token_defaults
    
    def scan_directory(self) -> Dict[str, Any]:
        """Scan entire directory for token blocking patterns."""
        results = {
            'scan_time': datetime.now().isoformat(),
            'total_files': 0,
            'infected_files': 0,
            'token_blockers': {},
            'summary': {
                'token_constants': 0,
                'token_blocking_logic': 0,
                'token_override_patterns': 0,
                'suspicious_patterns': 0
            }
        }
        
        # Scan all Python files
        for py_file in self.root_path.rglob('*.py'):
            # Skip virtual environment and cache directories
            if any(part in str(py_file) for part in ['.venv', '__pycache__', '.git', '.pytest_cache']):
                continue
            
            results['total_files'] += 1
            file_issues = self.scan_file(py_file)
            
            # Check if file has token blocking patterns
            has_blockers = any(
                len(file_issues.get(key, [])) > 0 
                for key in ['token_constants', 'token_blocking_logic', 'token_override_patterns', 
                           'suspicious_patterns']
            )
            
            if has_blockers:
                results['infected_files'] += 1
                results['token_blockers'][str(py_file)] = file_issues
                
                # Update summary
                for key in results['summary']:
                    results['summary'][key] += len(file_issues.get(key, []))
        
        return results
    
    def generate_token_unblocker_script(self, results: Dict[str, Any]) -> str:
        """Generate script to remove token blocking patterns."""
        script_lines = [
            '#!/usr/bin/env python3',
            '"""',
            'Emergency Token Blocking Pattern Removal',
            f'Generated on: {datetime.now().isoformat()}',
            '"""',
            '',
            'import os',
            'import re',
            'from pathlib import Path',
            '',
            'def remove_token_blocking_patterns():',
            '    """Remove token blocking patterns that prevent iteration."""',
            '    print("🚨 REMOVING TOKEN BLOCKING PATTERNS...")',
            ''
        ]
        
        for file_path, issues in results['token_blockers'].items():
            script_lines.append(f'    # File: {file_path}')
            
            # Add removal commands for token constants
            if issues.get('token_constants'):
                script_lines.append('    # CRITICAL: Token constant blocking')
                for item in issues['token_constants']:
                    script_lines.append(f'    # Line {item["line"]}: {item["code"]}')
                    script_lines.append('    # Remove DEFAULT_MAX_TOKENS = 4000')
            
            # Add removal commands for token blocking logic
            if issues.get('token_blocking_logic'):
                script_lines.append('    # CRITICAL: Token blocking logic')
                for item in issues['token_blocking_logic']:
                    script_lines.append(f'    # Line {item["line"]}: {item["pattern"]}')
            
            script_lines.append('')
        
        script_lines.extend([
            '    print("✅ Token blocking patterns removed")',
            '    print("🔄 Token iteration now unblocked")',
            '',
            'if __name__ == "__main__":',
            '    remove_token_blocking_patterns()'
        ])
        
        return '\n'.join(script_lines)

def main():
    """Main token blocking detection function."""
    print("🚨 TOKEN BLOCKING FUNCTION DETECTOR")
    print("=" * 60)
    print("Scanning for functions that block iteration through token level limiting...")
    print("")
    
    # Initialize detector
    echoes_root = Path(__file__).parent.parent
    detector = TokenBlockingDetector(echoes_root)
    
    # Scan directory
    results = detector.scan_directory()
    
    # Display results
    print("📊 Token Blocking Scan Results:")
    print(f"   • Total files scanned: {results['total_files']}")
    print(f"   • Files with token blockers: {results['infected_files']}")
    print("")
    
    print("🚨 Token Blocking Threats Summary:")
    for threat_type, count in results['summary'].items():
        if count > 0:
            print(f"   • {threat_type.replace('_', ' ').title()}: {count}")
    
    if results['infected_files'] > 0:
        print("\n🔥 CRITICAL TOKEN BLOCKING PATTERNS DETECTED:")
        for file_path, issues in results['token_blockers'].items():
            print(f"\n📁 {file_path}:")
            for threat_type, items in issues.items():
                if threat_type not in ['file', 'error'] and items:
                    if isinstance(items, list):
                        print(f"   🚨 {threat_type}: {len(items)} instances")
                        for item in items[:3]:  # Show first 3
                            if isinstance(item, dict) and 'line' in item:
                                print(f"      Line {item['line']}: {item.get('code', item.get('pattern', 'suspicious'))}")
                    elif items and isinstance(items, list):
                        print(f"   🚨 {threat_type}: {len(items)} instances")
                        for item in items[:3]:  # Show first 3
                            if isinstance(item, dict) and 'line' in item:
                                print(f"      Line {item['line']}: {item.get('code', item.get('pattern', 'suspicious'))}")
        
        # Generate removal script
        removal_script = detector.generate_token_unblocker_script(results)
        script_path = echoes_root / 'security_audit' / 'remove_token_blockers.py'
        
        with open(script_path, 'w') as f:
            f.write(removal_script)
        
        print(f"\n🔧 Token blocker removal script generated: {script_path}")
        print("⚠️ RUN IMMEDIATELY - CRITICAL TOKEN ITERATION BLOCKAGE!")
        
        return False
    else:
        print("\n✅ No token blocking patterns detected!")
        print("🔄 Token iteration is unblocked")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
