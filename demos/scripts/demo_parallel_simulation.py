#!/usr/bin/env python3
"""
Demo script showcasing the Parallel Simulation Engine for possibility exploration
Demonstrates concurrent simulation instances to understand possibilities and enhance cross-references
"""

import os
import sys
import time

# Load environment variables
os.environ.setdefault("PYTHONPATH", os.path.dirname(os.path.abspath(__file__)))

try:
    from core_modules.parallel_simulation_engine import (SimulationStatus,
                                                         SimulationType,
                                                         parallel_simulation)
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you're running from the Echoes project root")
    sys.exit(1)


def demo_basic_simulation():
    """Demonstrate basic simulation creation and execution"""
    print("\n" + "=" * 70)
    print("🧠 BASIC PARALLEL SIMULATION DEMO")
    print("=" * 70)

    print("\n📥 Creating simulation instances:")

    # Create different types of simulations
    simulations = [
        {
            "type": SimulationType.SCENARIO_EXPLORATION,
            "input_data": {
                "scenario": "Implementing a new AI system for customer support",
                "context": {"industry": "technology", "size": "medium"},
            },
            "description": "Scenario exploration",
        },
        {
            "type": SimulationType.OUTCOME_PREDICTION,
            "input_data": {
                "action": "Launch a new mobile app",
                "context": {"timeline": "6 months", "budget": "100k"},
            },
            "description": "Outcome prediction",
        },
        {
            "type": SimulationType.ALTERNATIVE_PATHS,
            "input_data": {
                "problem": "High employee turnover rate",
                "current_approach": "Standard recruitment process",
            },
            "description": "Alternative paths analysis",
        },
    ]

    simulation_ids = []

    for sim in simulations:
        sim_id = parallel_simulation.create_simulation(
            simulation_type=sim["type"],
            input_data=sim["input_data"],
            parameters={"priority": 0.7, "timeout": 20},
        )
        simulation_ids.append(sim_id)
        print(f"  ✅ Created {sim['description']}: {sim_id}")

    print("\n⏳ Waiting for simulations to complete...")

    # Wait for all simulations to complete
    results = []
    for sim_id in simulation_ids:
        result = parallel_simulation.wait_for_simulation(sim_id, timeout=30.0)
        if result:
            results.append(result)
            print(
                f"  ✅ Completed {result.simulation_type.value}: {result.confidence:.1%} confidence"
            )
        else:
            print(f"  ✗ Failed to complete simulation: {sim_id}")

    print("\n📊 Simulation Results:")
    for i, result in enumerate(results, 1):
        print(f"\n  {i}. {result.simulation_type.value.replace('_', ' ').title()}:")
        print(f"     Confidence: {result.confidence:.1%}")
        print(f"     Execution time: {result.execution_time:.2f}s")
        print(f"     Reasoning: {result.reasoning}")

        if result.insights:
            print(f"     Insights: {', '.join(result.insights[:2])}")

        if result.possibilities:
            print(f"     Top possibilities: {len(result.possibilities)}")
            for j, poss in enumerate(result.possibilities[:2], 1):
                if isinstance(poss, dict):
                    desc = poss.get("description", str(poss))
                else:
                    desc = str(poss)
                print(f"       {j}. {desc[:60]}...")


def demo_concurrent_simulation():
    """Demonstrate running multiple simulations concurrently"""
    print("\n" + "=" * 70)
    print("⚡ CONCURRENT SIMULATION DEMO")
    print("=" * 70)

    print("\n🚀 Running multiple simulations in parallel...")

    # Prepare multiple simulation configs
    simulation_configs = [
        {
            "type": SimulationType.SCENARIO_EXPLORATION,
            "input_data": {"scenario": "Adopting remote work policy", "context": {}},
            "parameters": {"priority": 0.8, "timeout": 15},
        },
        {
            "type": SimulationType.OUTCOME_PREDICTION,
            "input_data": {"action": "Implement agile development", "context": {}},
            "parameters": {"priority": 0.7, "timeout": 20},
        },
        {
            "type": SimulationType.ALTERNATIVE_PATHS,
            "input_data": {
                "problem": "Decreasing sales revenue",
                "current_approach": "",
            },
            "parameters": {"priority": 0.6, "timeout": 25},
        },
        {
            "type": SimulationType.CONTEXT_EXPANSION,
            "input_data": {"topic": "digital transformation", "context": {}},
            "parameters": {"priority": 0.5, "timeout": 10},
        },
        {
            "type": SimulationType.DECISION_SUPPORT,
            "input_data": {
                "decision": "Choose cloud provider",
                "options": ["AWS", "Azure", "Google Cloud"],
                "criteria": {"cost": 0.3, "performance": 0.4, "support": 0.3},
            },
            "parameters": {"priority": 0.9, "timeout": 30},
        },
    ]

    start_time = time.time()

    # Run all simulations in parallel
    results = parallel_simulation.run_parallel_simulations(simulation_configs)

    execution_time = time.time() - start_time

    print(
        f"\n⏱️ Executed {len(simulation_configs)} simulations in {execution_time:.2f}s"
    )
    print(
        f"   Average time per simulation: {execution_time/len(simulation_configs):.2f}s"
    )

    print("\n📊 Concurrent Results:")
    for i, result in enumerate(results, 1):
        print(f"\n  {i}. {result.simulation_type.value.replace('_', ' ').title()}:")
        print(f"     Confidence: {result.confidence:.1%}")
        print(f"     Relevance: {result.relevance_score:.1%}")
        print(f"     Execution time: {result.execution_time:.2f}s")
        print(f"     Reasoning: {result.reasoning[:80]}...")


def demo_possibility_space():
    """Demonstrate possibility space exploration"""
    print("\n" + "=" * 70)
    print("🌌 POSSIBILITY SPACE EXPLORATION DEMO")
    print("=" * 70)

    print("\n🔍 Exploring comprehensive possibility space...")

    topic = "Artificial Intelligence in Healthcare"

    print(f"  Topic: {topic}")
    print("  Running possibility space simulation...")

    # Create possibility space simulation
    sim_id = parallel_simulation.create_simulation(
        simulation_type=SimulationType.POSSIBILITY_SPACE,
        input_data={
            "topic": topic,
            "constraints": {"budget": "medium", "timeline": "2-5 years"},
        },
        parameters={"priority": 0.8, "timeout": 30},
    )

    # Wait for completion
    result = parallel_simulation.wait_for_simulation(sim_id, timeout=35.0)

    if result and result.outcome:
        outcome = result.outcome

        print("\n📊 Possibility Space Analysis:")
        print(f"  Total dimensions: {outcome.get('total_dimensions', 0)}")
        print(f"  Total combinations: {outcome.get('total_combinations', 0):,}")
        print(
            f"  Exploration recommendation: {outcome.get('exploration_recommendation', '')}"
        )

        space = outcome.get("possibility_space", [])
        if space:
            print("\n  🌐 Dimension Analysis:")
            for dim in space:
                print(f"\n    • {dim.get('name', 'unknown').title()}:")
                print(f"      Complexity: {dim.get('complexity', 'unknown')}")
                print(f"      Impact: {dim.get('impact', 'unknown')}")

                possibilities = dim.get("possibilities", [])
                print(f"      Possibilities ({len(possibilities)}):")
                for poss in possibilities[:3]:
                    print(f"        - {poss}")

        if result.insights:
            print("\n  💡 Key Insights:")
            for insight in result.insights:
                print(f"    • {insight}")

    else:
        print("  ✗ Failed to explore possibility space")


def demo_cross_reference_enhancement():
    """Demonstrate cross-reference enhancement through simulation"""
    print("\n" + "=" * 70)
    print("🔗 CROSS-REFERENCE ENHANCEMENT DEMO")
    print("=" * 70)

    print("\n🔍 Enhancing cross-references with simulation insights...")

    # Create cross-reference enhancement simulation
    sim_id = parallel_simulation.create_simulation(
        simulation_type=SimulationType.CROSS_REFERENCE_ENHANCEMENT,
        input_data={
            "query": "machine learning algorithms",
            "existing_references": [
                {"type": "basic", "description": "ML algorithms for data analysis"},
                {
                    "type": "technical",
                    "description": "Implementation of neural networks",
                },
            ],
        },
        parameters={"priority": 0.7, "timeout": 20},
    )

    result = parallel_simulation.wait_for_simulation(sim_id, timeout=25.0)

    if result and result.outcome:
        outcome = result.outcome

        print("\n📊 Enhanced Cross-References:")
        print(f"  Original references: {outcome.get('original_count', 0)}")
        print(f"  Enhanced references: {outcome.get('enhanced_count', 0)}")
        print(f"  Improvement: +{outcome.get('improvement', 0)} references")

        enhanced_refs = outcome.get("enhanced_references", [])
        if enhanced_refs:
            print("\n  🔗 Enhanced References:")
            for i, ref in enumerate(enhanced_refs[:3], 1):
                print(f"\n    {i}. Type: {ref.get('type', 'unknown')}")
                print(f"       Description: {ref.get('description', '')[:80]}...")
                print(f"       Strength: {ref.get('strength', 0):.1%}")
                print(f"       Enhanced: {ref.get('enhanced', False)}")

                if ref.get("simulation_insights"):
                    insights = ref["simulation_insights"]
                    print(f"       Simulation insights: {', '.join(insights[:2])}")

        if result.insights:
            print("\n  💡 Enhancement Insights:")
            for insight in result.insights:
                print(f"    • {insight}")

    else:
        print("  ✗ Failed to enhance cross-references")


def demo_decision_support():
    """Demonstrate decision support through simulation"""
    print("\n" + "=" * 70)
    print("🎯 DECISION SUPPORT DEMO")
    print("=" * 70)

    print("\n🤔 Providing decision support through simulation...")

    decision = "Select programming language for new project"
    options = ["Python", "JavaScript", "Java", "Go"]
    criteria = {
        "performance": 0.3,
        "ecosystem": 0.3,
        "learning_curve": 0.2,
        "job_market": 0.2,
    }

    print(f"  Decision: {decision}")
    print(f"  Options: {', '.join(options)}")
    print(f"  Criteria: {', '.join(criteria.keys())}")

    # Create decision support simulation
    sim_id = parallel_simulation.create_simulation(
        simulation_type=SimulationType.DECISION_SUPPORT,
        input_data={"decision": decision, "options": options, "criteria": criteria},
        parameters={"priority": 0.9, "timeout": 25},
    )

    result = parallel_simulation.wait_for_simulation(sim_id, timeout=30.0)

    if result and result.outcome:
        outcome = result.outcome

        print("\n📊 Decision Support Analysis:")
        print(f"  Decision framework: {outcome.get('decision_framework', '')}")
        print(
            f"  Confidence in recommendation: {outcome.get('confidence_in_recommendation', 0):.1%}"
        )

        analyses = outcome.get("option_analyses", [])
        if analyses:
            print("\n  📈 Option Analysis:")
            for i, analysis in enumerate(analyses, 1):
                print(f"\n    {i}. {analysis.get('option', 'Unknown')}:")
                print(
                    f"       Success probability: {analysis.get('success_probability', 0):.1%}"
                )
                print(f"       Timeline: {analysis.get('timeline', 'unknown')}")
                print(f"       Effort: {analysis.get('effort', 'unknown')}")

                if analysis.get("pros"):
                    print(f"       Pros: {', '.join(analysis['pros'][:2])}")

                if analysis.get("cons"):
                    print(f"       Cons: {', '.join(analysis['cons'][:2])}")

        recommended = outcome.get("recommended_option", {})
        if recommended:
            print("\n  🎯 Recommended Option:")
            print(f"    Choice: {recommended.get('option', 'unknown')}")
            print(
                f"    Success probability: {recommended.get('success_probability', 0):.1%}"
            )
            print(f"    Timeline: {recommended.get('timeline', 'unknown')}")

        if result.insights:
            print("\n  💡 Decision Insights:")
            for insight in result.insights:
                print(f"    • {insight}")

    else:
        print("  ✗ Failed to provide decision support")


def demo_performance_statistics():
    """Demonstrate performance monitoring and statistics"""
    print("\n" + "=" * 70)
    print("📊 PERFORMANCE STATISTICS DEMO")
    print("=" * 70)

    print("\n📈 Simulation Engine Performance:")

    # Get comprehensive statistics
    stats = parallel_simulation.get_simulation_statistics()

    print("\n  🧮 Overall Statistics:")
    print(f"    Total simulations: {stats['total_simulations']}")
    print(f"    Active simulations: {stats['active_simulations']}")
    print(f"    Queue size: {stats['queue_size']}")

    print("\n  📋 Status Breakdown:")
    for status, count in stats["status_breakdown"].items():
        print(f"    {status.replace('_', ' ').title()}: {count}")

    print("\n  🏷️ Type Breakdown:")
    for sim_type, count in stats["type_breakdown"].items():
        print(f"    {sim_type.replace('_', ' ').title()}: {count}")

    print("\n  ⚡ Performance Metrics:")
    perf = stats["performance"]
    print(f"    Success rate: {perf['success_rate']:.1%}")
    print(f"    Average execution time: {perf['average_execution_time']:.2f}s")
    print(f"    Average confidence: {perf['average_confidence']:.1%}")
    print(f"    Average relevance: {perf['average_relevance']:.1%}")
    print(f"    Completed simulations: {perf['completed']}")
    print(f"    Failed simulations: {perf['failed']}")

    print("\n  ⚙️ Configuration:")
    print(f"    Max workers: {stats['max_workers']}")
    print(f"    Max concurrent: {stats['max_concurrent']}")

    # Show efficiency
    if stats["total_simulations"] > 0:
        efficiency = perf["success_rate"] * perf["average_confidence"]
        print(f"    Overall efficiency: {efficiency:.1%}")


def demo_real_time_simulation():
    """Demonstrate real-time simulation monitoring"""
    print("\n" + "=" * 70)
    print("⏱️ REAL-TIME SIMULATION MONITORING DEMO")
    print("=" * 70)

    print("\n🚀 Starting simulations and monitoring in real-time...")

    # Create multiple simulations with different durations
    sim_configs = [
        {
            "type": SimulationType.SCENARIO_EXPLORATION,
            "input_data": {"scenario": "Quick market analysis", "context": {}},
            "parameters": {"priority": 0.5, "timeout": 5},
        },
        {
            "type": SimulationType.OUTCOME_PREDICTION,
            "input_data": {"action": "Product launch strategy", "context": {}},
            "parameters": {"priority": 0.7, "timeout": 10},
        },
        {
            "type": SimulationType.ALTERNATIVE_PATHS,
            "input_data": {
                "problem": "Complex optimization challenge",
                "current_approach": "",
            },
            "parameters": {"priority": 0.9, "timeout": 15},
        },
    ]

    # Start simulations
    simulation_ids = []
    for config in sim_configs:
        sim_id = parallel_simulation.create_simulation(
            simulation_type=config["type"],
            input_data=config["input_data"],
            parameters=config["parameters"],
        )
        simulation_ids.append(sim_id)
        print(f"  📤 Started simulation: {sim_id}")

    # Monitor progress
    print("\n⏳ Monitoring simulation progress...")

    completed_count = 0
    start_time = time.time()

    while completed_count < len(simulation_ids) and (time.time() - start_time) < 20:
        # Check status of each simulation
        for sim_id in simulation_ids:
            status = parallel_simulation.get_simulation_status(sim_id)
            if status and status.status == SimulationStatus.COMPLETED:
                if sim_id not in [s for s in simulation_ids[:completed_count]]:
                    completed_count += 1
                    result = parallel_simulation.get_simulation_result(sim_id)
                    if result:
                        print(
                            f"  ✅ Completed: {result.simulation_type.value} "
                            f"(confidence: {result.confidence:.1%}, "
                            f"time: {result.execution_time:.2f}s)"
                        )

        time.sleep(1)

    # Get final results
    print("\n📊 Final Results:")
    for sim_id in simulation_ids:
        result = parallel_simulation.get_simulation_result(sim_id)
        if result:
            print(
                f"  • {result.simulation_type.value}: {result.confidence:.1%} confidence"
            )


def demo_cross_reference_integration():
    """Demonstrate how simulations enhance cross-references"""
    print("\n" + "=" * 70)
    print("🔗 CROSS-REFERENCE INTEGRATION DEMO")
    print("=" * 70)

    print("\n🧠 Demonstrating simulation-enhanced cross-references...")

    # Simulate a conversation where cross-references are enhanced
    topic = "Cloud Computing Architecture"

    print(f"  Topic: {topic}")
    print("  Running context expansion and cross-reference enhancement...")

    # Context expansion simulation
    context_sim_id = parallel_simulation.create_simulation(
        simulation_type=SimulationType.CONTEXT_EXPANSION,
        input_data={"topic": topic, "context": {"conversation": "design discussion"}},
        parameters={"priority": 0.7, "timeout": 15},
    )

    # Cross-reference enhancement simulation
    xref_sim_id = parallel_simulation.create_simulation(
        simulation_type=SimulationType.CROSS_REFERENCE_ENHANCEMENT,
        input_data={
            "query": topic,
            "existing_references": [
                {"type": "technical", "description": "AWS vs Azure comparison"},
                {"type": "conceptual", "description": "Microservices architecture"},
            ],
        },
        parameters={"priority": 0.8, "timeout": 20},
    )

    # Wait for both simulations
    context_result = parallel_simulation.wait_for_simulation(
        context_sim_id, timeout=20.0
    )
    xref_result = parallel_simulation.wait_for_simulation(xref_sim_id, timeout=25.0)

    print("\n📊 Enhanced Cross-Reference Results:")

    if context_result:
        print("\n  🌐 Context Expansion:")
        print(f"    Confidence: {context_result.confidence:.1%}")
        print(f"    Breadth: {context_result.outcome.get('breadth', 0)} dimensions")

        expansions = context_result.outcome.get("expanded_context", [])
        if expansions:
            print("    Enhanced contexts:")
            for exp in expansions[:3]:
                print(
                    f"      • {exp.get('type', 'unknown')}: {exp.get('description', '')[:60]}..."
                )

    if xref_result:
        print("\n  🔗 Cross-Reference Enhancement:")
        print(f"    Confidence: {xref_result.confidence:.1%}")
        print(
            f"    Improvement: +{xref_result.outcome.get('improvement', 0)} references"
        )

        enhanced_refs = xref_result.outcome.get("enhanced_references", [])
        if enhanced_refs:
            print("    Enhanced with simulation insights:")
            for ref in enhanced_refs[:2]:
                print(f"      • {ref.get('description', '')[:60]}...")
                print(f"        Strength: {ref.get('strength', 0):.1%}")

    print("\n💡 Integration Benefits:")
    print("  • Multi-dimensional context understanding")
    print("  • Simulation-driven relationship discovery")
    print("  • Enhanced relevance scoring")
    print("  • Deeper cross-reference insights")


def main():
    """Run all parallel simulation demos"""
    print("\n✨ Welcome to the Parallel Simulation Engine Demo!")
    print(
        "This showcases concurrent simulation instances for possibility exploration and cross-reference enhancement."
    )

    # Run all demos
    demo_basic_simulation()
    demo_concurrent_simulation()
    demo_possibility_space()
    demo_cross_reference_enhancement()
    demo_decision_support()
    demo_performance_statistics()
    demo_real_time_simulation()
    demo_cross_reference_integration()

    # Cleanup
    parallel_simulation.clear_completed_simulations()

    print("\n" + "=" * 70)
    print("🎉 Parallel Simulation Engine Demo Complete!")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✅ 7 simulation types for different analysis needs")
    print("  ✅ Concurrent execution with thread pool management")
    print("  ✅ Real-time monitoring and status tracking")
    print("  ✅ Comprehensive performance statistics")
    print("  ✅ Possibility space mapping with combinatorial analysis")
    print("  ✅ Cross-reference enhancement through simulation")
    print("  ✅ Decision support with multi-criteria analysis")
    print("  ✅ Context expansion with multi-dimensional insights")

    print("\nSimulation Types:")
    print("  • Scenario Exploration: Explore different scenarios")
    print("  • Outcome Prediction: Predict possible outcomes")
    print("  • Alternative Paths: Simulate different approaches")
    print("  • Context Expansion: Expand context with related info")
    print("  • Cross-Reference Enhancement: Enhance cross-references")
    print("  • Possibility Space: Map out possibility combinations")
    print("  • Decision Support: Support decision making")

    print("\nPerformance Features:")
    print("  • Thread-safe concurrent execution")
    print("  • Configurable worker pools and timeouts")
    print("  • Background queue processing")
    print("  • Real-time status monitoring")
    print("  • Comprehensive performance metrics")
    print("  • Automatic cleanup and resource management")

    print("\nTry the interactive mode with:")
    print("  python assistant_v2_core.py")
    print("  Then try commands like:")
    print("    simulate <query>           - Run parallel simulations")
    print("    sims                       - Show simulation statistics")
    print("    sim <id>                   - Get specific result")
    print("    possibilities <topic>     - Explore possibility space")
    print("    clearsims                  - Clear completed simulations")


if __name__ == "__main__":
    main()
