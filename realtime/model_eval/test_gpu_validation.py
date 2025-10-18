#!/usr/bin/env python3
"""Quick test for GPU model validation"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Ensure stdout is unbuffered
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

from run_gpu_tests import GPUModelConfig

def test_gpu_validation():
    print("Testing GPU Model Validation")
    print("=" * 40)
    sys.stdout.flush()

    config = GPUModelConfig('gpt-oss:20b-cloud', search_enabled=True)
    print(f"Created config for model: {config.model_name}")
    print(f"Search enabled: {config.search_enabled}")
    print(f"GPU memory: {config.gpu_memory_gb}GB")
    sys.stdout.flush()

    print("\nRunning validation...")
    sys.stdout.flush()
    result = config.validate_gpu_setup()

    print(f"Validation result: {result}")
    if result:
        print("✅ SUCCESS: GPU validation passed!")
    else:
        print("❌ FAILED: GPU validation failed")

    sys.stdout.flush()
    return result

if __name__ == "__main__":
    test_gpu_validation()
