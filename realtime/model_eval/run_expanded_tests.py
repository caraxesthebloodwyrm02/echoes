#!/usr/bin/env python3
"""
Quick Start Script for Expanded Model Evaluation

This script provides an easy way to run the expanded test suite with rate limiting.
"""

import argparse
import json
import sys
from pathlib import Path

def load_config(config_file: Path) -> dict:
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file {config_file} not found. Using defaults.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in config file: {e}")
        sys.exit(1)

def run_evaluation(config: dict):
    """Run the expanded evaluation suite"""
    print("🚀 Starting Expanded Model Evaluation with Rate Limiting")
    print("=" * 60)

    # Import here to avoid issues if dependencies aren't installed
    try:
        from expanded_evaluation_suite import ModelEvaluator
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("  pip install psutil gputil")
        sys.exit(1)

    # Setup paths
    questions_dir = Path(config.get('evaluation', {}).get('questions_directory', 'questions'))
    output_dir = Path(config.get('evaluation', {}).get('output_directory', 'evaluations'))
    models = config.get('models', ['mistral:7b-instruct'])

    if not questions_dir.exists():
        print(f"❌ Questions directory not found: {questions_dir}")
        sys.exit(1)

    # Create evaluator
    evaluator = ModelEvaluator(models, questions_dir, output_dir)

    # Run evaluation
    try:
        report = evaluator.run_comprehensive_evaluation()

        # Print summary
        print(f"\n📊 Evaluation Complete!")
        print(f"Total Evaluations: {report['total_evaluations']}")
        print(f"Overall Success Rate: {report['overall_success_rate']:.1%}")
        print(f"Rate Limit Hits: {report['rate_limiting_metrics']['rate_limit_hits']}")
        print(f"Average Response Time: {report['rate_limiting_metrics']['average_response_time']:.2f}s")
        print(f"Retries Attempted: {report['rate_limiting_metrics']['retries_attempted']}")

        print(f"\n📁 Results saved to: {output_dir.absolute()}")

    except KeyboardInterrupt:
        print("\n⏹️  Evaluation interrupted by user")
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        sys.exit(1)

def run_load_test(config: dict):
    """Run load testing"""
    print("🔥 Starting Load Testing for Rate Limiting")
    print("=" * 60)

    try:
        from load_tester import LoadTester, LoadTestConfig
    except ImportError as e:
        print(f"❌ Import error: {e}")
        sys.exit(1)

    models = config.get('models', ['mistral:7b-instruct'])
    load_config = config.get('load_testing', {})

    for model in models:
        print(f"\nTesting model: {model}")

        test_config = LoadTestConfig(
            model=model,
            concurrent_requests=load_config.get('max_concurrent_requests', 3),
            total_requests=load_config.get('requests_per_model', 30)
        )

        tester = LoadTester(test_config)
        result = tester.run_load_test()

        # Print results
        print(f"✅ Successful: {result.successful_requests}/{result.total_requests}")
        print(f"🚫 Rate Limited: {result.rate_limited_requests}")
        print(f"Throughput: {result.throughput_rps:.1f} RPS")
        print(f"Avg Response Time: {result.avg_response_time:.2f}s")

def main():
    parser = argparse.ArgumentParser(description="Expanded Model Evaluation Test Suite")
    parser.add_argument('--config', '-c', type=Path, default=Path('evaluation_config.json'),
                       help='Configuration file path')
    parser.add_argument('--mode', '-m', choices=['evaluate', 'load-test', 'both'],
                       default='evaluate', help='Test mode to run')
    parser.add_argument('--models', nargs='+', help='Override models to test')

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Override models if specified
    if args.models:
        config['models'] = args.models

    # Run selected mode
    if args.mode in ['evaluate', 'both']:
        run_evaluation(config)

    if args.mode in ['load-test', 'both']:
        if args.mode == 'both':
            print("\n" + "="*60)
        run_load_test(config)

    print("\n✨ Test suite execution complete!")

if __name__ == "__main__":
    main()
