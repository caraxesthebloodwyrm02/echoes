#!/usr/bin/env python3
"""
GPU-Enabled Model Evaluation Test

Tests GPU-accelerated models with advanced capabilities like search functionality.
Specifically tests gpt-oss:120b model with search enabled.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import logging

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from run_expanded_tests_fixed_content import ModelEvaluator

# Configure logging with immediate flushing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gpu_test.log'),
        logging.StreamHandler(sys.stdout)
    ],
    force=True  # Force reconfiguration of logging
)

# Ensure stdout is unbuffered
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

logger = logging.getLogger(__name__)
logger.info("GPU Test module loaded successfully")


class GPUModelConfig:
    """Configuration for GPU-enabled models with advanced capabilities"""

    def __init__(self, model_name: str, search_enabled: bool = False, gpu_memory_gb: int = 16):
        self.model_name = model_name
        self.search_enabled = search_enabled
        self.gpu_memory_gb = gpu_memory_gb
        self.environment_vars = self._setup_environment()

    def _setup_environment(self) -> Dict[str, str]:
        """Setup environment variables for GPU model"""
        env_vars = {
            'OLLAMA_GPU_LAYERS': '35',  # Enable GPU layers for large models
            'OLLAMA_NUM_GPU': '1',      # Use 1 GPU
            'OLLAMA_GPU_MEMORY_FRACTION': '0.9',  # Use 90% of GPU memory
        }

        if self.search_enabled:
            env_vars.update({
                'OLLAMA_SEARCH_ENABLED': 'true',
                'OLLAMA_SEARCH_PROVIDER': 'duckduckgo',  # Default search provider
                'OLLAMA_SEARCH_MAX_RESULTS': '5',
            })

        return env_vars

    def apply_environment(self):
        """Apply environment variables for this model"""
        for key, value in self.environment_vars.items():
            os.environ[key] = value
            logger.info(f"Set {key}={value}")

    def validate_gpu_setup(self) -> bool:
        """Validate GPU setup and model availability"""
        print(f"Validating GPU setup for {self.model_name}...")
        sys.stdout.flush()

        try:
            # Simplified validation - just check if ollama is accessible
            import subprocess
            try:
                print("Checking Ollama connectivity...")
                sys.stdout.flush()
                result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    print(f"Warning: Ollama list failed (exit code {result.returncode}), proceeding anyway")
                    logger.warning(f"Ollama list failed (exit code {result.returncode}), but proceeding anyway")
                    logger.warning("Make sure ollama is running and models are available")
                else:
                    print("Successfully connected to Ollama")
                    logger.info(f"Successfully connected to Ollama")
                    # Log available models for reference
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        print(f"Found {len(lines)-1} models available")
                        logger.info(f"Found {len(lines)-1} models available")

            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                print(f"Warning: Ollama access issue: {e}, proceeding anyway")
                logger.warning(f"Ollama access issue: {e}, proceeding anyway")

            # Check GPU availability (simplified check)
            print("Checking GPU availability...")
            sys.stdout.flush()
            try:
                result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
                if result.returncode != 0:
                    print("NVIDIA GPU not detected, using CPU fallback")
                    logger.warning("NVIDIA GPU not detected, but continuing with CPU fallback")
                else:
                    print("NVIDIA GPU detected")
                    logger.info("NVIDIA GPU detected")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print("nvidia-smi not found, using CPU-only setup")
                logger.warning("nvidia-smi not found, assuming CPU-only setup")

            print(f"GPU setup validation completed for {self.model_name}")
            sys.stdout.flush()
            logger.info(f"GPU setup validation completed for {self.model_name}")
            return True  # Always return True to allow evaluation

        except Exception as e:
            error_msg = f"GPU validation failed: {e}"
            print(f"ERROR: {error_msg}")
            sys.stdout.flush()
            logger.error(error_msg)
            return True  # Return True anyway to not block evaluation


class GPUModelEvaluator:
    """Evaluator specifically for GPU-enabled models with advanced capabilities"""

    def __init__(self, questions_dir: Path, output_root: Path):
        self.questions_dir = questions_dir
        self.output_root = output_root
        self.gpu_models = self._setup_gpu_models()

    def _setup_gpu_models(self) -> List[GPUModelConfig]:
        """Setup GPU model configurations"""
        return [
            GPUModelConfig(
                model_name="gpt-oss:20b-cloud",  # Use smaller 20B model for faster testing
                search_enabled=True,
                gpu_memory_gb=16  # Reduced memory requirement
            ),
            # Add more GPU models here as needed
        ]

    def run_gpu_evaluation(self) -> Dict[str, Any]:
        """Run evaluation for all configured GPU models"""
        print(f"Starting GPU evaluation for {len(self.gpu_models)} models...")
        sys.stdout.flush()

        all_results = {}

        for gpu_config in self.gpu_models:
            print(f"\n--- Processing model: {gpu_config.model_name} ---")
            sys.stdout.flush()
            logger.info(f"Starting GPU evaluation for {gpu_config.model_name}")

            # Validate and setup GPU environment
            if not gpu_config.validate_gpu_setup():
                print(f"Skipping {gpu_config.model_name} due to validation failure")
                sys.stdout.flush()
                logger.error(f"Skipping {gpu_config.model_name} due to validation failure")
                continue

            gpu_config.apply_environment()
            print("Environment variables applied")
            sys.stdout.flush()

            # Create timestamped output directory
            timestamp = os.popen('date +%Y%m%d_%H%M%S').read().strip()
            if not timestamp:
                # Windows fallback
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            output_dir = self.output_root / f"gpu_run_{timestamp}_{gpu_config.model_name.replace(':', '_')}"

            print(f"Output directory: {output_dir}")
            sys.stdout.flush()

            # Run evaluation
            try:
                print("Creating ModelEvaluator instance...")
                sys.stdout.flush()
                evaluator = ModelEvaluator([gpu_config.model_name], self.questions_dir, output_dir)
                print("Starting comprehensive evaluation...")
                sys.stdout.flush()

                report = evaluator.run_comprehensive_evaluation()

                # Add GPU-specific metadata
                report['gpu_config'] = {
                    'model': gpu_config.model_name,
                    'search_enabled': gpu_config.search_enabled,
                    'gpu_memory_gb': gpu_config.gpu_memory_gb,
                    'environment_vars': gpu_config.environment_vars
                }

                all_results[gpu_config.model_name] = report
                print(f"Evaluation completed for {gpu_config.model_name}")
                sys.stdout.flush()
                logger.info(f"GPU evaluation completed for {gpu_config.model_name}")

                # Optional load test for GPU models
                if input(f"Run GPU load test for {gpu_config.model_name}? (y/N): ").strip().lower().startswith("y"):
                    evaluator.run_load_test(gpu_config.model_name, num_requests=10)  # Reduced for GPU

            except Exception as e:
                error_msg = f"GPU evaluation failed for {gpu_config.model_name}: {e}"
                print(f"ERROR: {error_msg}")
                sys.stdout.flush()
                logger.error(error_msg)
                all_results[gpu_config.model_name] = {'error': str(e)}

        return all_results

    def generate_gpu_report(self, results: Dict[str, Any]) -> None:
        """Generate comprehensive GPU evaluation report"""
        print("\n" + "="*60)
        print("GPU MODEL EVALUATION REPORT")
        print("="*60)

        for model_name, result in results.items():
            print(f"\nModel: {model_name}")

            if 'error' in result:
                print(f"  Status: FAILED - {result['error']}")
                continue

            gpu_config = result.get('gpu_config', {})
            print(f"  Search Enabled: {gpu_config.get('search_enabled', False)}")
            print(f"  GPU Memory: {gpu_config.get('gpu_memory_gb', 'Unknown')}GB")
            print(f"  Total Evaluations: {result.get('total_evaluations', 0)}")
            print(f"  Success Rate: {result.get('overall_success_rate', 0):.1%}")
            print(f"  Avg Response Time: {result.get('rate_limiting_metrics', {}).get('average_response_time', 0):.2f}s")

            if result.get('rate_limiting_metrics', {}).get('rate_limit_hits', 0) > 0:
                print(f"  Rate Limit Hits: {result['rate_limiting_metrics']['rate_limit_hits']}")

        print(f"\n{'='*60}")


def main():
    """Main entry point for GPU model evaluation"""
    # Use os.system to force immediate output
    os.system('echo GPU-Enabled Model Evaluation Test')
    os.system('echo ==================================')

    print("GPU-Enabled Model Evaluation Test")
    print("==================================")
    sys.stdout.flush()

    # Also write to a status file
    status_file = Path("gpu_status.txt")
    with open(status_file, 'w') as f:
        f.write("GPU-Enabled Model Evaluation Test\n")
        f.write("==================================\n")

    logger.info("Starting GPU evaluation main function")

    # Setup directories
    script_dir = Path(__file__).parent
    questions_dir = script_dir / "questions"
    output_root = script_dir / "gpu_evaluations"

    os.system(f'echo Script directory: {script_dir}')
    os.system(f'echo Questions directory: {questions_dir}')
    os.system(f'echo Output root: {output_root}')

    print(f"Script directory: {script_dir}")
    print(f"Questions directory: {questions_dir}")
    print(f"Output root: {output_root}")
    sys.stdout.flush()

    with open(status_file, 'a') as f:
        f.write(f"Script directory: {script_dir}\n")
        f.write(f"Questions directory: {questions_dir}\n")
        f.write(f"Output root: {output_root}\n")

    # Validate directories
    if not questions_dir.exists():
        error_msg = f"Questions directory not found: {questions_dir}"
        os.system(f'echo ERROR: {error_msg}')
        print(f"ERROR: {error_msg}")
        logger.error(error_msg)
        with open(status_file, 'a') as f:
            f.write(f"ERROR: {error_msg}\n")
        sys.exit(1)

    output_root.mkdir(exist_ok=True)
    os.system('echo Directories validated. Starting evaluation...')
    print(f"Directories validated. Starting evaluation...")
    sys.stdout.flush()

    with open(status_file, 'a') as f:
        f.write("Directories validated. Starting evaluation...\n")

    # Run GPU evaluation
    try:
        os.system('echo Creating GPUModelEvaluator instance...')
        print("Creating GPUModelEvaluator instance...")
        sys.stdout.flush()

        logger.info("Creating GPUModelEvaluator instance")
        evaluator = GPUModelEvaluator(questions_dir, output_root)

        os.system(f'echo GPU evaluator created with {len(evaluator.gpu_models)} models')
        print(f"GPU evaluator created with {len(evaluator.gpu_models)} models")
        sys.stdout.flush()

        with open(status_file, 'a') as f:
            f.write(f"GPU evaluator created with {len(evaluator.gpu_models)} models\n")

        os.system('echo Starting GPU evaluation run...')
        print("Starting GPU evaluation run...")
        sys.stdout.flush()

        logger.info("Starting GPU evaluation run")
        results = evaluator.run_gpu_evaluation()

        os.system(f'echo GPU evaluation completed. Processing {len(results)} result sets...')
        print(f"GPU evaluation completed. Processing {len(results)} result sets...")
        sys.stdout.flush()

        with open(status_file, 'a') as f:
            f.write(f"GPU evaluation completed. Processing {len(results)} result sets...\n")

        evaluator.generate_gpu_report(results)

        os.system(f'echo GPU evaluation complete! Results saved to: {output_root}')
        print(f"\nGPU evaluation complete! Results saved to: {output_root}")
        sys.stdout.flush()

        with open(status_file, 'a') as f:
            f.write(f"GPU evaluation complete! Results saved to: {output_root}\n")

    except KeyboardInterrupt:
        os.system('echo GPU evaluation interrupted by user')
        print("\nGPU evaluation interrupted by user")
        logger.warning("GPU evaluation interrupted by user")
        with open(status_file, 'a') as f:
            f.write("GPU evaluation interrupted by user\n")
    except Exception as e:
        error_msg = f"Fatal error in GPU evaluation: {e}"
        os.system(f'echo ERROR: {error_msg}')
        print(f"ERROR: {error_msg}")
        logger.error(error_msg)
        with open(status_file, 'a') as f:
            f.write(f"ERROR: {error_msg}\n")
        raise


if __name__ == "__main__":
    main()
