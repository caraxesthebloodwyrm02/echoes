# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# MIT License
# Copyright (c) 2025 Echoes Project

"""
Windows-specific integrations
Registry, COM objects, DLL calls, Credential Manager
"""

import logging
import platform
import sys
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Platform detection
IS_WINDOWS = platform.system() == "Windows"

# Windows-specific imports (conditional)
if IS_WINDOWS:
    try:
        import ctypes
        import winreg
        from ctypes import windll

        import pywintypes
        import win32com.client
        import win32cred
        import wmi

        WINDOWS_MODULES_AVAILABLE = True
    except ImportError as e:
        logger.warning(f"Windows modules not available: {e}")
        WINDOWS_MODULES_AVAILABLE = False
else:
    WINDOWS_MODULES_AVAILABLE = False


class WindowsRegistry:
    """Windows Registry operations"""

    def __init__(self):
        if not IS_WINDOWS or not WINDOWS_MODULES_AVAILABLE:
            raise RuntimeError("Windows registry only available on Windows")
        self.logger = logging.getLogger(__name__)

    def read_value(
        self, key_path: str, value_name: str, root=winreg.HKEY_LOCAL_MACHINE
    ) -> Optional[Any]:
        """Read value from registry"""
        try:
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return value
        except FileNotFoundError:
            self.logger.debug(f"Registry key not found: {key_path}\\{value_name}")
            return None
        except Exception as e:
            self.logger.error(f"Error reading registry: {e}")
            return None

    def write_value(
        self, key_path: str, value_name: str, value: Any, root=winreg.HKEY_LOCAL_MACHINE
    ):
        """Write value to registry (requires admin)"""
        try:
            key = winreg.CreateKey(root, key_path)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, str(value))
            winreg.CloseKey(key)
            self.logger.info(f"Registry value written: {key_path}\\{value_name}")
        except PermissionError:
            self.logger.error("Permission denied - requires administrator privileges")
        except Exception as e:
            self.logger.error(f"Error writing registry: {e}")


class WindowsCOM:
    """Windows COM object interactions"""

    def __init__(self):
        if not IS_WINDOWS or not WINDOWS_MODULES_AVAILABLE:
            raise RuntimeError("COM only available on Windows")
        self.logger = logging.getLogger(__name__)

    def create_object(self, prog_id: str) -> Any:
        """Create COM object"""
        try:
            return win32com.client.Dispatch(prog_id)
        except Exception as e:
            self.logger.error(f"Failed to create COM object {prog_id}: {e}")
            raise

    def get_wmi(self) -> Any:
        """Get WMI interface"""
        try:
            return wmi.WMI()
        except Exception as e:
            self.logger.error(f"Failed to get WMI: {e}")
            raise


class WindowsDLL:
    """Windows DLL calls via ctypes"""

    def __init__(self):
        if not IS_WINDOWS or not WINDOWS_MODULES_AVAILABLE:
            raise RuntimeError("DLL calls only available on Windows")
        self.logger = logging.getLogger(__name__)

    def is_admin(self) -> bool:
        """Check if running as administrator"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception as e:
            self.logger.error(f"Failed to check admin status: {e}")
            return False

    def get_computer_name(self) -> str:
        """Get computer name via DLL"""
        try:
            buffer = ctypes.create_unicode_buffer(256)
            size = ctypes.c_ulong(256)
            ctypes.windll.kernel32.GetComputerNameW(buffer, ctypes.byref(size))
            return buffer.value
        except Exception as e:
            self.logger.error(f"Failed to get computer name: {e}")
            return "UNKNOWN"


class WindowsCredentialManager:
    """Windows Credential Manager for secure storage"""

    def __init__(self):
        if not IS_WINDOWS or not WINDOWS_MODULES_AVAILABLE:
            raise RuntimeError("Credential Manager only available on Windows")
        self.logger = logging.getLogger(__name__)

    def store_credential(self, target: str, username: str, password: str):
        """Store credential in Windows Credential Manager"""
        try:
            credential = {
                "Type": win32cred.CRED_TYPE_GENERIC,
                "TargetName": target,
                "UserName": username,
                "CredentialBlob": password,
                "Comment": "Stored by System Orchestrator",
                "Persist": win32cred.CRED_PERSIST_LOCAL_MACHINE,
            }
            win32cred.CredWrite(credential, 0)
            self.logger.info(f"Credential stored: {target}")
        except pywintypes.error as e:
            self.logger.error(f"Failed to store credential: {e}")

    def retrieve_credential(self, target: str) -> Optional[Dict[str, str]]:
        """Retrieve credential from Windows Credential Manager"""
        try:
            cred = win32cred.CredRead(target, win32cred.CRED_TYPE_GENERIC, 0)
            return {
                "username": cred["UserName"],
                "password": cred["CredentialBlob"].decode("utf-16-le"),
            }
        except pywintypes.error:
            self.logger.debug(f"Credential not found: {target}")
            return None

    def delete_credential(self, target: str):
        """Delete credential from Windows Credential Manager"""
        try:
            win32cred.CredDelete(target, win32cred.CRED_TYPE_GENERIC, 0)
            self.logger.info(f"Credential deleted: {target}")
        except pywintypes.error as e:
            self.logger.error(f"Failed to delete credential: {e}")


class PlatformDetector:
    """Platform detection and system information"""

    @staticmethod
    def get_platform_info() -> Dict[str, Any]:
        """Get comprehensive platform information"""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version,
            "python_implementation": platform.python_implementation(),
            "is_windows": IS_WINDOWS,
            "is_64bit": sys.maxsize > 2**32,
        }

    @staticmethod
    def is_windows_11() -> bool:
        """Check if running Windows 11"""
        if not IS_WINDOWS:
            return False
        version = platform.version()
        # Windows 11 has build number >= 22000
        try:
            build = int(version.split(".")[-1])
            return build >= 22000
        except:
            return False


__all__ = [
    "WindowsRegistry",
    "WindowsCOM",
    "WindowsDLL",
    "WindowsCredentialManager",
    "PlatformDetector",
    "IS_WINDOWS",
    "WINDOWS_MODULES_AVAILABLE",
]
