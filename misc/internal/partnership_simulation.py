import sys
import os

# Exclude the core directory to avoid conflicts with standard library
project_root = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.join(project_root, 'core')
if core_dir in sys.path:
    sys.path.remove(core_dir)

import random
import statistics
import matplotlib.pyplot as plt
import numpy as np

# Enhanced partnership funnel simulator
PATHS = {
    'research': {'outreach': 50, 'resp_rate': 0.12, 'accept_rate': 0.25, 'timeline_weeks': 10, 'safety_score': 0.9},
    'integration': {'outreach': 40, 'resp_rate': 0.15, 'accept_rate': 0.2, 'timeline_weeks': 6, 'safety_score': 0.7},
    'academic': {'outreach': 30, 'resp_rate': 0.18, 'accept_rate': 0.18, 'timeline_weeks': 30, 'safety_score': 0.8},
    'community': {'outreach': 100, 'resp_rate': 0.3, 'accept_rate': 0.35, 'timeline_weeks': 4, 'safety_score': 0.6},
    'commercial': {'outreach': 25, 'resp_rate': 0.10, 'accept_rate': 0.3, 'timeline_weeks': 9, 'safety_score': 0.5},
}

SIMS = 5000  # Increased for better statistics

def run_enhanced_sim(path_name, path_config):
    successes = 0
    response_counts = []
    accept_counts = []

    for _ in range(SIMS):
        responses = sum(1 for _ in range(path_config['outreach'])
                       if random.random() < path_config['resp_rate'])
        accepts = sum(1 for _ in range(responses)
                     if random.random() < path_config['accept_rate'])

        response_counts.append(responses)
        accept_counts.append(accepts)

        if accepts >= 1:
            successes += 1

    prob = successes / SIMS
    avg_responses = statistics.mean(response_counts)
    avg_accepts = statistics.mean(accept_counts)

    return {
        'success_probability': prob,
        'avg_responses': avg_responses,
        'avg_accepts': avg_accepts,
        'response_std': statistics.stdev(response_counts),
        'accept_std': statistics.stdev(accept_counts)
    }

# Run simulations
results = {}
for path_name, config in PATHS.items():
    results[path_name] = run_enhanced_sim(path_name, config)

# Print results
print("Enhanced Partnership Simulation Results (5,000 simulations each)")
print("=" * 60)
for path, result in results.items():
    print(f"{path.capitalize():12s} | P(success): {result['success_probability']:.2%} | "
          f"Avg Responses: {result['avg_responses']:.1f} | Avg Accepts: {result['avg_accepts']:.1f}")

# Visualization
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

# Success probabilities
paths = list(results.keys())
probs = [results[p]['success_probability'] for p in paths]
bars1 = ax1.bar(paths, probs, color='#228B22', alpha=0.7)
ax1.set_title('Success Probabilities by Path')
ax1.set_ylabel('Probability')
ax1.tick_params(axis='x', rotation=45)

# Add value labels
for bar, prob in zip(bars1, probs):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
             f'{prob:.1%}', ha='center', va='bottom', fontsize=9)

# Average responses
responses = [results[p]['avg_responses'] for p in paths]
bars2 = ax2.bar(paths, responses, color='#FFD700', alpha=0.7)
ax2.set_title('Average Responses per Simulation')
ax2.set_ylabel('Average Responses')
ax2.tick_params(axis='x', rotation=45)

for bar, resp in zip(bars2, responses):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
             f'{resp:.1f}', ha='center', va='bottom', fontsize=9)

# Timeline vs Success scatter
timelines = [PATHS[p]['timeline_weeks'] for p in paths]
ax3.scatter(timelines, probs, s=100, c='#FF6347', alpha=0.7)
for i, path in enumerate(paths):
    ax3.annotate(path.capitalize(), (timelines[i], probs[i]),
                xytext=(5, 5), textcoords='offset points', fontsize=9)
ax3.set_xlabel('Timeline (weeks)')
ax3.set_ylabel('Success Probability')
ax3.set_title('Timeline vs Success Probability')
ax3.grid(True, alpha=0.3)

# Safety vs Success scatter
safeties = [PATHS[p]['safety_score'] for p in paths]
ax4.scatter(safeties, probs, s=100, c='#90EE90', alpha=0.7)
for i, path in enumerate(paths):
    ax4.annotate(path.capitalize(), (safeties[i], probs[i]),
                xytext=(5, 5), textcoords='offset points', fontsize=9)
ax4.set_xlabel('Safety Score')
ax4.set_ylabel('Success Probability')
ax4.set_title('Safety vs Success Probability')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('partnership_analysis.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved as 'partnership_analysis.png'")
plt.show()
