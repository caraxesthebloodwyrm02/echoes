"""
Security Integration Module - Glimpse
Integrates security features from the parent directory's thon.py module
"""

from __future__ import annotations
import sys
import importlib.util
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import logging
import time

# Setup logging
LOG = logging.getLogger("glimpse_security")
LOG.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
LOG.handlers = [handler]


@dataclass
class SecurityContext:
    """Security context for realtime operations"""
    shield_factor: float  # 0-1, from detector
    is_safe: bool
    risk_level: str  # low, medium, high
    allowed_operations: List[str]
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "shield_factor": self.shield_factor,
            "is_safe": self.is_safe,
            "risk_level": self.risk_level,
            "allowed_operations": self.allowed_operations,
            "timestamp": self.timestamp
        }


class SecurityManager:
    """
    Manages security for realtime preview operations.
    Integrates with the parent thon.py security module.
    """
    
    def __init__(self, base_path: Optional[Path] = None, enable_thon_integration: bool = True):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent
        self.thon_module = None
        self.orchestrator = None
        self.detector = None
        self.current_context: Optional[SecurityContext] = None
        
        # Attempt to load thon.py module
        if enable_thon_integration:
            self._load_thon_module()
    
    def _load_thon_module(self):
        """Dynamically load the thon.py security module"""
        try:
            # Look for thon.py in parent directory
            thon_path = self.base_path.parent / "thon.py"
            
            if not thon_path.exists():
                LOG.warning(f"thon.py not found at {thon_path}, using fallback security")
                return
            
            # Load module dynamically
            spec = importlib.util.spec_from_file_location("thon", thon_path)
            if spec and spec.loader:
                self.thon_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(self.thon_module)
                LOG.info(f"Successfully loaded thon.py from {thon_path}")
                
                # Initialize orchestrator and detector
                self._initialize_thon_components()
            else:
                LOG.warning("Failed to load thon.py spec")
                
        except Exception as e:
            LOG.error(f"Error loading thon.py: {e}")
            self.thon_module = None
    
    def _initialize_thon_components(self):
        """Initialize orchestrator and detector from thon module"""
        if not self.thon_module:
            return
        
        try:
            # Create orchestrator
            Orchestrator = getattr(self.thon_module, "Orchestrator", None)
            if Orchestrator:
                self.orchestrator = Orchestrator(base_path=self.base_path)
                LOG.info("Orchestrator initialized")
            
            # Create detector
            StartDetector = getattr(self.thon_module, "StartDetector", None)
            if StartDetector and self.orchestrator:
                self.detector = StartDetector(
                    base_path=self.base_path,
                    orchestrator=self.orchestrator
                )
                LOG.info("StartDetector initialized")
                
        except Exception as e:
            LOG.error(f"Error initializing thon components: {e}")
    
    def assess_security_context(self) -> SecurityContext:
        """Assess current security context using thon detector"""
        
        # If thon integration is available, use it
        if self.detector:
            try:
                should_start, observation = self.detector.should_start()
                
                shield = observation.shield_factor
                
                # Determine risk level
                if shield >= 0.7:
                    risk_level = "low"
                elif shield >= 0.4:
                    risk_level = "medium"
                else:
                    risk_level = "high"
                
                # Determine allowed operations based on shield factor
                allowed_ops = self._determine_allowed_operations(shield)
                
                context = SecurityContext(
                    shield_factor=shield,
                    is_safe=shield >= 0.3,
                    risk_level=risk_level,
                    allowed_operations=allowed_ops,
                    timestamp=time.time()
                )
                
                LOG.info(f"Security assessment: shield={shield:.3f}, risk={risk_level}")
                self.current_context = context
                return context
                
            except Exception as e:
                LOG.error(f"Error assessing security with thon: {e}")
        
        # Fallback: use basic security assessment
        return self._fallback_security_assessment()
    
    def _fallback_security_assessment(self) -> SecurityContext:
        """Fallback security assessment when thon module unavailable"""
        LOG.info("Using fallback security assessment")
        
        context = SecurityContext(
            shield_factor=0.5,
            is_safe=True,
            risk_level="medium",
            allowed_operations=["read", "preview", "visualize"],
            timestamp=time.time()
        )
        
        self.current_context = context
        return context
    
    def _determine_allowed_operations(self, shield_factor: float) -> List[str]:
        """Determine allowed operations based on shield factor"""
        operations = []
        
        # Basic operations always allowed
        operations.extend(["read", "preview", "visualize"])
        
        if shield_factor >= 0.3:
            operations.extend(["track", "analyze"])
        
        if shield_factor >= 0.5:
            operations.extend(["suggest", "adapt"])
        
        if shield_factor >= 0.7:
            operations.extend(["export", "save"])
        
        if shield_factor >= 0.9:
            operations.extend(["execute", "deploy"])
        
        return operations
    
    def validate_operation(self, operation: str) -> bool:
        """Validate if an operation is allowed in current security context"""
        if not self.current_context:
            self.assess_security_context()
        
        if not self.current_context:
            return False
        
        allowed = operation.lower() in self.current_context.allowed_operations
        
        if not allowed:
            LOG.warning(f"Operation '{operation}' not allowed. Shield factor: {self.current_context.shield_factor:.3f}")
        
        return allowed
    
    def validate_command(self, command: str) -> Dict[str, Any]:
        """
        Validate a command using thon's defensive command wrapper.
        Returns result dict with allowed flag and reason.
        """
        if self.orchestrator and hasattr(self.orchestrator, 'run_command'):
            try:
                result = self.orchestrator.run_command(command)
                LOG.info(f"Command validation: {result.get('reason', 'unknown')}")
                return result
            except Exception as e:
                LOG.error(f"Error validating command: {e}")
                return {
                    "cmd": command,
                    "allowed": False,
                    "reason": f"validation_error: {str(e)}"
                }
        
        # Fallback: basic validation
        return self._fallback_command_validation(command)
    
    def _fallback_command_validation(self, command: str) -> Dict[str, Any]:
        """Fallback command validation"""
        # Very conservative - only allow safe read operations
        safe_prefixes = ["ls", "dir", "cat", "type", "echo"]
        
        cmd_lower = command.lower().strip()
        is_safe = any(cmd_lower.startswith(prefix) for prefix in safe_prefixes)
        
        return {
            "cmd": command,
            "allowed": is_safe,
            "reason": "allowed: safe_read" if is_safe else "rejected: not_in_safe_list"
        }
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get current security metrics"""
        if not self.current_context:
            self.assess_security_context()
        
        metrics = {
            "context": self.current_context.to_dict() if self.current_context else None,
            "thon_integrated": self.thon_module is not None,
            "detector_active": self.detector is not None,
            "orchestrator_active": self.orchestrator is not None
        }
        
        # Add thon-specific metrics if available
        if self.detector:
            try:
                avg_strength = self.detector.inspect_attractors()
                high_jammers = self.detector.count_high_jammers()
                consecutive_alert = self.detector.consecutive_jam_alert()
                
                metrics["thon_metrics"] = {
                    "avg_attractor_strength": avg_strength,
                    "high_aggressive_jammers": high_jammers,
                    "consecutive_jam_alert": consecutive_alert
                }
            except Exception as e:
                LOG.error(f"Error getting thon metrics: {e}")
        
        return metrics
    
    def run_security_check(self) -> bool:
        """Run comprehensive security check"""
        context = self.assess_security_context()
        
        # Security passes if shield factor is adequate
        passed = context.shield_factor >= 0.3
        
        if passed:
            LOG.info("✓ Security check passed")
        else:
            LOG.warning("✗ Security check failed - shield factor too low")
        
        return passed
    
    def enhance_shield(self) -> float:
        """Attempt to enhance shield factor by running orchestrator steps"""
        if not self.orchestrator:
            LOG.info("Cannot enhance shield - orchestrator not available")
            return 0.0
        
        try:
            # Run a few orchestrator steps to potentially improve shield
            self.orchestrator.run(steps=3)
            
            # Reassess
            new_context = self.assess_security_context()
            
            LOG.info(f"Shield enhanced to {new_context.shield_factor:.3f}")
            return new_context.shield_factor
            
        except Exception as e:
            LOG.error(f"Error enhancing shield: {e}")
            return 0.0
    
    def export_security_report(self, filepath: str):
        """Export detailed security report"""
        import json
        
        report = {
            "timestamp": time.time(),
            "metrics": self.get_security_metrics(),
            "base_path": str(self.base_path),
            "thon_integration": {
                "enabled": self.thon_module is not None,
                "module_loaded": self.thon_module is not None,
                "orchestrator_initialized": self.orchestrator is not None,
                "detector_initialized": self.detector is not None
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        LOG.info(f"Security report exported to {filepath}")


# Convenience function for quick security check
def quick_security_check(base_path: Optional[Path] = None) -> bool:
    """Quick security check - returns True if safe to proceed"""
    manager = SecurityManager(base_path=base_path)
    return manager.run_security_check()
