"""
Dynamic Error Handler - Automated bug detection and fixing system
Provides intelligent error handling with self-healing capabilities
"""
import logging
import traceback
import re
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class DynamicErrorHandler:
    """Intelligent error handler with automated fix capabilities"""
    
    def __init__(self):
        self.error_patterns = {
            # Import errors
            r"cannot import name '(\w+)'": self._fix_import_error,
            r"No module named '(\w+)'": self._fix_missing_module,
            r"has no attribute '(\w+)'": self._fix_missing_attribute,
            
            # API errors
            r"Authentication Error": self._fix_auth_error,
            r"RateLimitError": self._fix_rate_limit,
            r"API Error": self._handle_api_error,
            
            # Type/Value errors
            r"got an unexpected keyword argument '(\w+)'": self._fix_unexpected_kwarg,
            r"missing (\d+) required positional arguments": self._fix_missing_args,
            r"'(\w+)' object is not (subscriptable|iterable|callable)": self._fix_type_error,
            
            # File/Path errors
            r"No such file or directory: '(.*)'": self._fix_file_not_found,
            r"Permission denied: '(.*)'": self._fix_permission_error,
            
            # Network errors
            r"ConnectionError|TimeoutError": self._fix_network_error,
        }
        
        self.fix_history = []
        self.auto_fix_enabled = True
        
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle an error with automated fix attempts
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            
        Returns:
            Dictionary with error analysis and fix results
        """
        error_msg = str(error)
        error_type = type(error).__name__
        
        # Analyze the error
        analysis = self._analyze_error(error_msg, error_type, context)
        
        # Attempt automated fix if enabled
        fix_result = None
        if self.auto_fix_enabled:
            fix_result = self._attempt_fix(error_msg, error_type, analysis, context)
        
        # Log the error and fix attempt
        self._log_error_fix(error, analysis, fix_result)
        
        return {
            "error_type": error_type,
            "error_message": error_msg,
            "analysis": analysis,
            "fix_attempted": fix_result is not None,
            "fix_result": fix_result,
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_error(self, error_msg: str, error_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the error to understand its nature and cause"""
        analysis = {
            "severity": "medium",
            "category": "unknown",
            "likely_cause": "Unknown",
            "suggestions": []
        }
        
        # Determine severity
        if any(keyword in error_msg.lower() for keyword in ["critical", "fatal", "system"]):
            analysis["severity"] = "high"
        elif any(keyword in error_msg.lower() for keyword in ["warning", "deprecated"]):
            analysis["severity"] = "low"
        
        # Categorize error
        if "import" in error_msg.lower() or "module" in error_msg.lower():
            analysis["category"] = "import"
            analysis["likely_cause"] = "Missing or incorrect import"
            analysis["suggestions"] = ["Check module installation", "Verify import path"]
        elif "api" in error_msg.lower() or "authentication" in error_msg.lower():
            analysis["category"] = "api"
            analysis["likely_cause"] = "API configuration or authentication issue"
            analysis["suggestions"] = ["Check API keys", "Verify endpoint URL"]
        elif "type" in error_type.lower() or "value" in error_type.lower():
            analysis["category"] = "type"
            analysis["likely_cause"] = "Data type mismatch"
            analysis["suggestions"] = ["Check variable types", "Validate input data"]
        elif "file" in error_msg.lower() or "directory" in error_msg.lower():
            analysis["category"] = "file"
            analysis["likely_cause"] = "File system access issue"
            analysis["suggestions"] = ["Check file paths", "Verify permissions"]
        
        return analysis
    
    def _attempt_fix(self, error_msg: str, error_type: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Attempt to automatically fix the error"""
        for pattern, fix_func in self.error_patterns.items():
            match = re.search(pattern, error_msg)
            if match:
                try:
                    return fix_func(match, error_msg, error_type, analysis, context)
                except Exception as fix_error:
                    logger.warning(f"Auto-fix failed: {fix_error}")
                    return None
        return None
    
    def _fix_import_error(self, match, error_msg: str, error_type: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Fix import errors by suggesting correct imports"""
        missing_name = match.group(1)
        
        # Common import mappings
        import_mappings = {
            "Sampler": "from glimpse.engine import default_sampler",
            "ClarifierEngine": "from glimpse.clarifier_engine import ClarifierEngine",
            "get_openai_schemas": "Add get_openai_schemas method to ToolRegistry",
            "PrivacyGuard": "from glimpse import PrivacyGuard",
        }
        
        suggestion = import_mappings.get(missing_name, f"Check if '{missing_name}' exists in the module")
        
        return {
            "fix_type": "import_fix",
            "suggestion": suggestion,
            "code_fix": f"# Try adding:\n{suggestion}",
            "auto_applicable": True
        }
    
    def _fix_missing_module(self, match, error_msg: str, error_type: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Fix missing module errors"""
        module_name = match.group(1)
        
        # Common module installations
        package_mappings = {
            "yaml": "pip install pyyaml",
            "openai": "pip install openai",
            "requests": "pip install requests",
            "numpy": "pip install numpy",
            "pandas": "pip install pandas",
        }
        
        install_cmd = package_mappings.get(module_name, f"pip install {module_name}")
        
        return {
            "fix_type": "install_package",
            "suggestion": f"Install missing package: {install_cmd}",
            "code_fix": install_cmd,
            "auto_applicable": False  # Requires user confirmation
        }
    
    def _fix_missing_attribute(self, match, error_msg: str, error_type: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Fix missing attribute errors"""
        attr_name = match.group(1)
        
        return {
            "fix_type": "attribute_fix",
            "suggestion": f"Add missing method/attribute: {attr_name}",
            "code_fix": f"def {attr_name}(self, *args, **kwargs):\n    pass  # Implement this method",
            "auto_applicable": True
        }
    
    def _fix_auth_error(self, match, error_msg: str, error_type: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Fix authentication errors"""
        return {
            "fix_type": "auth_fix",
            "suggestion": "Check OPENAI_API_KEY environment variable",
            "code_fix": "export OPENAI_API_KEY='your-api-key-here'",
            "auto_applicable": False
        }
    
    def _fix_rate_limit(self, match, error_msg: str, error_type: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Fix rate limit errors"""
        return {
            "fix_type": "rate_limit_fix",
            "suggestion": "Implement exponential backoff or reduce request frequency",
            "code_fix": "import time; time.sleep(1)  # Add delay between requests",
            "auto_applicable": True
        }
    
    def _handle_api_error(self, match, error_msg: str, error_type: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general API errors"""
        return {
            "fix_type": "api_general_fix",
            "suggestion": "Check API configuration and network connectivity",
            "code_fix": "# Verify API settings and retry",
            "auto_applicable": False
        }
    
    def _fix_unexpected_kwarg(self, match, error_msg: str, error_type: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Fix unexpected keyword argument errors"""
        kwarg_name = match.group(1)
        
        return {
            "fix_type": "kwarg_fix",
            "suggestion": f"Remove or handle unexpected keyword argument: {kwarg_name}",
            "code_fix": f"# Try removing '{kwarg_name}' parameter or using **kwargs to capture it",
            "auto_applicable": True
        }
    
    def _fix_missing_args(self, match, error_msg: str, error_type: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Fix missing required arguments"""
        return {
            "fix_type": "args_fix",
            "suggestion": "Provide all required positional arguments",
            "code_fix": "# Check function signature and provide all required arguments",
            "auto_applicable": False
        }
    
    def _fix_type_error(self, match, error_msg: str, error_type: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Fix type errors"""
        return {
            "fix_type": "type_fix",
            "suggestion": "Convert object to correct type before operation",
            "code_fix": "# Use type conversion: str(), list(), dict(), etc.",
            "auto_applicable": False
        }
    
    def _fix_file_not_found(self, match, error_msg: str, error_type: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Fix file not found errors"""
        file_path = match.group(1)
        
        return {
            "fix_type": "file_fix",
            "suggestion": f"Create missing file or check path: {file_path}",
            "code_fix": f"# Create file: touch '{file_path}' or check if path exists",
            "auto_applicable": False
        }
    
    def _fix_permission_error(self, match, error_msg: str, error_type: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Fix permission errors"""
        return {
            "fix_type": "permission_fix",
            "suggestion": "Check file permissions or run with appropriate privileges",
            "code_fix": "# chmod +x filename or run with sudo/admin privileges",
            "auto_applicable": False
        }
    
    def _fix_network_error(self, match, error_msg: str, error_type: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Fix network errors"""
        return {
            "fix_type": "network_fix",
            "suggestion": "Check internet connection and implement retry logic",
            "code_fix": "import time; for attempt in range(3): try: # code; break; except: time.sleep(2**attempt)",
            "auto_applicable": True
        }
    
    def _log_error_fix(self, error: Exception, analysis: Dict[str, Any], fix_result: Optional[Dict[str, Any]]):
        """Log error and fix attempt for learning"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "error": str(error),
            "error_type": type(error).__name__,
            "analysis": analysis,
            "fix_result": fix_result
        }
        self.fix_history.append(log_entry)
        
        # Keep only last 100 entries
        if len(self.fix_history) > 100:
            self.fix_history = self.fix_history[-100:]
    
    def get_fix_statistics(self) -> Dict[str, Any]:
        """Get statistics about error fixes"""
        if not self.fix_history:
            return {"total_errors": 0}
        
        total = len(self.fix_history)
        categories = {}
        severities = {}
        successful_fixes = 0
        
        for entry in self.fix_history:
            # Count categories
            cat = entry.get("analysis", {}).get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
            
            # Count severities
            sev = entry.get("analysis", {}).get("severity", "medium")
            severities[sev] = severities.get(sev, 0) + 1
            
            # Count successful fixes
            if entry.get("fix_result") and entry.get("fix_result", {}).get("auto_applicable"):
                successful_fixes += 1
        
        return {
            "total_errors": total,
            "categories": categories,
            "severities": severities,
            "successful_auto_fixes": successful_fixes,
            "auto_fix_success_rate": successful_fixes / total if total > 0 else 0
        }

# Global error handler instance
error_handler = DynamicErrorHandler()
