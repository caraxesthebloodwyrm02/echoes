#!/usr/bin/env python3
"""
Socket-Level Security Detector
Identifies malicious socket-based interception and cloning patterns.
"""

import ast
import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

class SocketLevelDetector:
    """Detects socket-based malicious patterns."""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.socket_threats = []
        
        # Critical socket-based threat patterns
        self.socket_threat_patterns = {
            # Raw socket interception
            'socket.AF_PACKET',           # Packet sniffing for response interception
            'socket.SOCK_RAW',            # Raw socket access for network manipulation
            'socket.IPPROTO_IP',          # IP protocol manipulation
            'socket.IPPROTO_RAW',         # Raw IP packet manipulation
            
            # Socket duplication and cloning
            'socket.dup()',                # Socket duplication for response cloning
            'socket.fromfd()',             # File descriptor duplication
            'socket.fromshare()',          # Socket sharing for cross-process cloning
            'socket.share()',              # Socket sharing mechanism
            
            # File descriptor theft
            'socket.send_fds()',           # File descriptor exfiltration
            'socket.recv_fds()',           # File descriptor infiltration
            'socket.SCM_RIGHTS',           # Unix socket rights manipulation
            
            # Network interception
            'socket.recvmsg()',            # Message interception
            'socket.sendmsg()',            # Message injection
            'socket.ioctl()',              # Low-level socket control
            
            # Address manipulation for detours
            'socket.bind()',               # Address binding for interception
            'socket.connect_ex()',         # Silent connection attempts
            'socket.getpeername()',        # Remote address discovery
            'socket.getsockname()',        # Local address manipulation
            
            # Buffer manipulation for cloning
            'socket.recv_into()',          # Direct buffer access for cloning
            'socket.recvfrom_into()',      # Direct buffer cloning
            'socket.makefile()',           # File-like object creation for data theft
        }
        
        # Suspicious socket configurations
        self.suspicious_socket_configs = {
            'SIO_RCVALL',                  # Windows packet capture (man-in-the-middle)
            'RCVALL_ON',                   # Enable packet capture
            'IP_HDRINCL',                  # IP header manipulation
            'SO_REUSEADDR',                # Address reuse for interception
            'SO_REUSEPORT',                # Port reuse for interception
        }
        
        # Network protocol abuse patterns
        self.protocol_abuse_patterns = {
            'AF_INET',                     # IPv4 manipulation
            'AF_INET6',                    # IPv6 manipulation  
            'AF_UNIX',                     # Unix socket abuse for IPC theft
            'AF_CAN',                      # CAN bus manipulation
            'AF_PACKET',                   # Packet manipulation
        }

    def scan_file(self, file_path: Path) -> Dict[str, Any]:
        """Scan a single file for socket-based threats."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = {
                'file': str(file_path),
                'raw_socket_threats': [],
                'socket_duplication': [],
                'file_descriptor_theft': [],
                'network_interception': [],
                'suspicious_configs': [],
                'protocol_abuse': [],
                'buffer_manipulation': []
            }
            
            # Check for raw socket threats
            for pattern in self.socket_threat_patterns:
                if pattern in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if pattern in line:
                            threat_type = self._classify_threat(pattern)
                            if threat_type in issues:
                                issues[threat_type].append({
                                    'line': i,
                                    'pattern': pattern,
                                    'code': line.strip()
                                })
            
            # Check for suspicious configurations
            for config in self.suspicious_socket_configs:
                if config in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if config in line:
                            issues['suspicious_configs'].append({
                                'line': i,
                                'config': config,
                                'code': line.strip()
                            })
            
            # Parse AST for deeper analysis
            try:
                tree = ast.parse(content)
                self._analyze_socket_ast(tree, file_path, issues)
            except SyntaxError:
                issues['syntax_error'] = True
            
            return issues
            
        except Exception as e:
            return {'file': str(file_path), 'error': str(e)}
    
    def _classify_threat(self, pattern: str) -> str:
        """Classify socket threat by type."""
        if 'SOCK_RAW' in pattern or 'AF_PACKET' in pattern or 'IPPROTO' in pattern:
            return 'raw_socket_threats'
        elif 'dup' in pattern or 'fromfd' in pattern or 'share' in pattern:
            return 'socket_duplication'
        elif 'send_fds' in pattern or 'recv_fds' in pattern or 'SCM_RIGHTS' in pattern:
            return 'file_descriptor_theft'
        elif 'recvmsg' in pattern or 'sendmsg' in pattern or 'ioctl' in pattern:
            return 'network_interception'
        elif 'recv_into' in pattern or 'makefile' in pattern:
            return 'buffer_manipulation'
        else:
            return 'raw_socket_threats'
    
    def _analyze_socket_ast(self, tree: ast.AST, file_path: Path, issues: Dict[str, Any]):
        """Analyze AST for socket-based malicious patterns."""
        
        class SocketThreatVisitor(ast.NodeVisitor):
            def __init__(self):
                self.socket_imports = []
                self.socket_creations = []
                self.suspicious_calls = []
            
            def visit_Import(self, node):
                for alias in node.names:
                    if alias.name == 'socket':
                        self.socket_imports.append({
                            'line': node.lineno,
                            'module': alias.name
                        })
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node):
                if node.module == 'socket':
                    for alias in node.names:
                        self.socket_imports.append({
                            'line': node.lineno,
                            'module': f'socket.{alias.name}'
                        })
                self.generic_visit(node)
            
            def visit_Call(self, node):
                # Check for suspicious socket calls
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == 'socket':
                        method_name = node.func.attr
                        if method_name in ['socket', 'dup', 'fromfd', 'recvmsg', 'sendmsg', 'ioctl']:
                            self.suspicious_calls.append({
                                'line': node.lineno,
                                'method': f'socket.{method_name}',
                                'type': 'socket_manipulation'
                            })
                
                self.generic_visit(node)
        
        visitor = SocketThreatVisitor()
        visitor.visit(tree)
        
        # Add AST-based findings
        if visitor.socket_imports:
            issues['socket_imports'] = visitor.socket_imports
        
        if visitor.suspicious_calls:
            issues['suspicious_socket_calls'] = visitor.suspicious_calls
    
    def scan_directory(self) -> Dict[str, Any]:
        """Scan entire directory for socket-based threats."""
        results = {
            'scan_time': datetime.now().isoformat(),
            'total_files': 0,
            'infected_files': 0,
            'socket_threats': {},
            'summary': {
                'raw_socket_threats': 0,
                'socket_duplication': 0,
                'file_descriptor_theft': 0,
                'network_interception': 0,
                'suspicious_configs': 0,
                'protocol_abuse': 0,
                'buffer_manipulation': 0
            }
        }
        
        # Scan all Python files
        for py_file in self.root_path.rglob('*.py'):
            # Skip virtual environment and cache directories
            if any(part in str(py_file) for part in ['.venv', '__pycache__', '.git', '.pytest_cache']):
                continue
            
            results['total_files'] += 1
            file_issues = self.scan_file(py_file)
            
            # Check if file has socket-based threats
            has_threats = any(
                len(file_issues.get(key, [])) > 0 
                for key in ['raw_socket_threats', 'socket_duplication', 'file_descriptor_theft', 
                           'network_interception', 'suspicious_configs', 'protocol_abuse', 
                           'buffer_manipulation']
            )
            
            if has_threats:
                results['infected_files'] += 1
                results['socket_threats'][str(py_file)] = file_issues
                
                # Update summary
                for key in results['summary']:
                    results['summary'][key] += len(file_issues.get(key, []))
        
        return results
    
    def generate_socket_removal_script(self, results: Dict[str, Any]) -> str:
        """Generate script to remove socket-based threats."""
        script_lines = [
            '#!/usr/bin/env python3',
            '"""',
            'Emergency Socket-Level Threat Removal',
            f'Generated on: {datetime.now().isoformat()}',
            '"""',
            '',
            'import os',
            'import shutil',
            'from pathlib import Path',
            '',
            'def remove_socket_threats():',
            '    """Remove socket-based malicious patterns."""',
            '    print("🚨 EMERGENCY: Removing socket-level threats...")',
            ''
        ]
        
        for file_path, issues in results['socket_threats'].items():
            script_lines.append(f'    # File: {file_path}')
            
            # Add removal commands for each threat type
            if issues.get('raw_socket_threats'):
                script_lines.append('    # CRITICAL: Raw socket threats found')
                for item in issues['raw_socket_threats']:
                    script_lines.append(f'    # Line {item["line"]}: {item["pattern"]}')
            
            if issues.get('socket_duplication'):
                script_lines.append('    # CRITICAL: Socket duplication/cloning')
                for item in issues['socket_duplication']:
                    script_lines.append(f'    # Line {item["line"]}: {item["pattern"]}')
            
            if issues.get('file_descriptor_theft'):
                script_lines.append('    # CRITICAL: File descriptor theft')
                for item in issues['file_descriptor_theft']:
                    script_lines.append(f'    # Line {item["line"]}: {item["pattern"]}')
            
            script_lines.append('')
        
        script_lines.extend([
            '    print("✅ Socket-level threats neutralized")',
            '    print("🔒 Network interception capabilities eliminated")',
            '',
            'if __name__ == "__main__":',
            '    remove_socket_threats()'
        ])
        
        return '\n'.join(script_lines)

def main():
    """Main socket-level security audit."""
    print("🚨 EMERGENCY SOCKET-LEVEL SECURITY AUDIT")
    print("=" * 60)
    print("Scanning for socket-based interception and cloning...")
    print("")
    
    # Initialize detector
    echoes_root = Path(__file__).parent.parent
    detector = SocketLevelDetector(echoes_root)
    
    # Scan directory
    results = detector.scan_directory()
    
    # Display results
    print("📊 Socket-Level Scan Results:")
    print(f"   • Total files scanned: {results['total_files']}")
    print(f"   • Files with socket threats: {results['infected_files']}")
    print("")
    
    print("🚨 Socket-Level Threats Summary:")
    for threat_type, count in results['summary'].items():
        if count > 0:
            print(f"   • {threat_type.replace('_', ' ').title()}: {count}")
    
    if results['infected_files'] > 0:
        print("\n🔥 CRITICAL SOCKET THREATS DETECTED:")
        for file_path, issues in results['socket_threats'].items():
            print(f"\n📁 {file_path}:")
            for threat_type, items in issues.items():
                if threat_type not in ['file', 'error'] and items:
                    print(f"   🚨 {threat_type}: {len(items)} instances")
                    for item in items[:3]:  # Show first 3
                        if isinstance(item, dict) and 'line' in item:
                            print(f"      Line {item['line']}: {item.get('pattern', 'suspicious_socket_call')}")
        
        # Generate removal script
        removal_script = detector.generate_socket_removal_script(results)
        script_path = echoes_root / 'security_audit' / 'remove_socket_threats.py'
        
        with open(script_path, 'w') as f:
            f.write(removal_script)
        
        print(f"\n🔧 Emergency removal script generated: {script_path}")
        print("⚠️ RUN IMMEDIATELY - CRITICAL SECURITY THREAT!")
        
        return False
    else:
        print("\n✅ No socket-level threats detected!")
        print("🔒 Network interfaces are secure")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
