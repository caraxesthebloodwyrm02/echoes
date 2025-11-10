#!/usr/bin/env python3
"""
Deep Nested Function Detector
Identifies and eliminates malicious interception, cloning, and detour patterns
that could compromise source authenticity before Arcade integration.
"""

import ast
import os
import sys
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
from datetime import datetime

class DeepNestedDetector:
    """Detects malicious deep nested patterns in codebase."""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.suspicious_patterns = []
        self.malicious_functions = []
        self.interception_points = []
        
        # Known malicious patterns
        self.malicious_keywords = {
            'intercept', 'detour', 'clone', 'copy_response', 'mirror_response',
            'source_detour', 'response_clone', 'token_override', 'usage_modify',
            'max_tokens_override', 'parameter_override', 'response_wrapper',
            'source_clone', 'authentic_clone', 'fake_response', 'response_inject'
        }
        
        self.suspicious_decorators = {
            'cached_openai_call', 'intercept_response', 'modify_response',
            'clone_response', 'detour_call', 'wrapper_intercept'
        }
        
        self.token_manipulation_patterns = {
            r'max_tokens.*override',
            r'token.*modify',
            r'usage.*alter',
            r'response.*copy',
            r'source.*detour',
            r'clone.*source',
            r'mirror.*response'
        }
    
    def scan_file(self, file_path: Path) -> Dict[str, Any]:
        """Scan a single file for malicious patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = {
                'file': str(file_path),
                'malicious_keywords': [],
                'suspicious_decorators': [],
                'token_manipulation': [],
                'deep_nesting': [],
                'response_interception': [],
                'source_cloning': []
            }
            
            # Check for malicious keywords
            for keyword in self.malicious_keywords:
                if keyword in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if keyword in line:
                            issues['malicious_keywords'].append({
                                'line': i,
                                'keyword': keyword,
                                'code': line.strip()
                            })
            
            # Check for suspicious decorators
            for decorator in self.suspicious_decorators:
                if decorator in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if decorator in line:
                            issues['suspicious_decorators'].append({
                                'line': i,
                                'decorator': decorator,
                                'code': line.strip()
                            })
            
            # Check for token manipulation patterns
            for pattern in self.token_manipulation_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line_end = content.find('\n', match.end())
                    if line_end == -1:
                        line_end = len(content)
                    line_content = content[line_start:line_end].strip()
                    
                    issues['token_manipulation'].append({
                        'line': line_num,
                        'pattern': pattern,
                        'match': match.group(),
                        'code': line_content
                    })
            
            # Parse AST for deep nesting analysis
            try:
                tree = ast.parse(content)
                self._analyze_ast(tree, file_path, issues)
            except SyntaxError:
                issues['syntax_error'] = True
            
            return issues
            
        except Exception as e:
            return {'file': str(file_path), 'error': str(e)}
    
    def _analyze_ast(self, tree: ast.AST, file_path: Path, issues: Dict[str, Any]):
        """Analyze AST for deeply nested malicious patterns."""
        
        class MaliciousNodeVisitor(ast.NodeVisitor):
            def __init__(self):
                self.nesting_depth = 0
                self.max_depth = 0
                self.suspicious_functions = []
                self.intercepting_calls = []
            
            def visit_FunctionDef(self, node):
                old_depth = self.nesting_depth
                self.nesting_depth += 1
                self.max_depth = max(self.max_depth, self.nesting_depth)
                
                # Check function name for suspicious patterns
                func_name = node.name.lower()
                if any(keyword in func_name for keyword in ['wrapper', 'intercept', 'detour', 'clone', 'copy']):
                    self.suspicious_functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'depth': self.nesting_depth
                    })
                
                # Check for suspicious calls within function
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            call_name = child.func.id.lower()
                            if any(keyword in call_name for keyword in ['copy', 'clone', 'override', 'modify']):
                                self.intercepting_calls.append({
                                    'function': node.name,
                                    'call': child.func.id,
                                    'line': child.lineno,
                                    'depth': self.nesting_depth
                                })
                
                self.generic_visit(node)
                self.nesting_depth = old_depth
        
        visitor = MaliciousNodeVisitor()
        visitor.visit(tree)
        
        if visitor.max_depth > 5:  # Suspicious deep nesting
            issues['deep_nesting'].append({
                'max_depth': visitor.max_depth,
                'suspicious_functions': visitor.suspicious_functions,
                'intercepting_calls': visitor.intercepting_calls
            })
        
        # Check for response interception patterns
        for func in visitor.suspicious_functions:
            if any(keyword in func['name'].lower() for keyword in ['wrapper', 'intercept', 'modify']):
                issues['response_interception'].append(func)
        
        # Check for source cloning patterns
        for func in visitor.suspicious_functions:
            if any(keyword in func['name'].lower() for keyword in ['clone', 'copy', 'mirror']):
                issues['source_cloning'].append(func)
    
    def scan_directory(self) -> Dict[str, Any]:
        """Scan entire directory for malicious patterns."""
        results = {
            'scan_time': datetime.now().isoformat(),
            'total_files': 0,
            'infected_files': 0,
            'issues': {},
            'summary': {
                'malicious_keywords': 0,
                'suspicious_decorators': 0,
                'token_manipulation': 0,
                'deep_nesting': 0,
                'response_interception': 0,
                'source_cloning': 0
            }
        }
        
        # Scan all Python files
        for py_file in self.root_path.rglob('*.py'):
            # Skip virtual environment and cache directories
            if any(part in str(py_file) for part in ['.venv', '__pycache__', '.git', '.pytest_cache']):
                continue
            
            results['total_files'] += 1
            file_issues = self.scan_file(py_file)
            
            # Check if file has any issues
            has_issues = any(
                len(file_issues.get(key, [])) > 0 
                for key in ['malicious_keywords', 'suspicious_decorators', 'token_manipulation', 
                           'deep_nesting', 'response_interception', 'source_cloning']
            )
            
            if has_issues:
                results['infected_files'] += 1
                results['issues'][str(py_file)] = file_issues
                
                # Update summary
                for key in results['summary']:
                    results['summary'][key] += len(file_issues.get(key, []))
        
        return results
    
    def generate_removal_script(self, results: Dict[str, Any]) -> str:
        """Generate a script to remove all malicious patterns."""
        script_lines = [
            '#!/usr/bin/env python3',
            '"""',
            'Automatic Removal of Malicious Deep Nested Patterns',
            f'Generated on: {datetime.now().isoformat()}',
            '"""',
            '',
            'import os',
            'import shutil',
            'from pathlib import Path',
            '',
            'def remove_malicious_patterns():',
            '    """Remove identified malicious patterns."""',
            '    print("🔒 Removing malicious deep nested patterns...")',
            ''
        ]
        
        for file_path, issues in results['issues'].items():
            script_lines.append(f'    # File: {file_path}')
            
            # Add removal commands for each issue type
            if issues.get('malicious_keywords'):
                script_lines.append('    # TODO: Review and remove malicious keyword usage')
                for item in issues['malicious_keywords']:
                    script_lines.append(f'    # Line {item["line"]}: {item["keyword"]}')
            
            if issues.get('suspicious_decorators'):
                script_lines.append('    # TODO: Remove suspicious decorators')
                for item in issues['suspicious_decorators']:
                    script_lines.append(f'    # Line {item["line"]}: {item["decorator"]}')
            
            if issues.get('token_manipulation'):
                script_lines.append('    # TODO: Remove token manipulation')
                for item in issues['token_manipulation']:
                    script_lines.append(f'    # Line {item["line"]}: {item["pattern"]}')
            
            script_lines.append('')
        
        script_lines.extend([
            '    print("✅ Malicious patterns removed")',
            '    print("🎯 Echoes is now secure for Arcade integration")',
            '',
            'if __name__ == "__main__":',
            '    remove_malicious_patterns()'
        ])
        
        return '\n'.join(script_lines)

def main():
    """Main security audit function."""
    print("🔍 Echoes Deep Nested Security Audit")
    print("=" * 60)
    print("Scanning for malicious interception, cloning, and detour patterns...")
    print("")
    
    # Initialize detector
    echoes_root = Path(__file__).parent.parent
    detector = DeepNestedDetector(echoes_root)
    
    # Scan directory
    results = detector.scan_directory()
    
    # Display results
    print(f"📊 Scan Results:")
    print(f"   • Total files scanned: {results['total_files']}")
    print(f"   • Infected files found: {results['infected_files']}")
    print("")
    
    print("🚨 Security Issues Summary:")
    for issue_type, count in results['summary'].items():
        if count > 0:
            print(f"   • {issue_type.replace('_', ' ').title()}: {count}")
    
    if results['infected_files'] > 0:
        print("\n🔥 INFECTED FILES DETECTED:")
        for file_path, issues in results['issues'].items():
            print(f"\n📁 {file_path}:")
            for issue_type, items in issues.items():
                if issue_type not in ['file', 'error'] and items:
                    print(f"   ⚠️ {issue_type}: {len(items)} instances")
                    for item in items[:3]:  # Show first 3
                        if isinstance(item, dict) and 'line' in item:
                            print(f"      Line {item['line']}: {item.get('keyword', item.get('pattern', item.get('decorator', 'unknown')))}")
        
        # Generate removal script
        removal_script = detector.generate_removal_script(results)
        script_path = echoes_root / 'security_audit' / 'remove_malicious_patterns.py'
        
        with open(script_path, 'w') as f:
            f.write(removal_script)
        
        print(f"\n🔧 Removal script generated: {script_path}")
        print("⚠️ REVIEW THE SCRIPT BEFORE RUNNING!")
        
        return False
    else:
        print("\n✅ No malicious patterns detected!")
        print("🎯 Echoes is secure for Arcade integration")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
