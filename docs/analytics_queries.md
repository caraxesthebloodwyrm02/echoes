# docs/analytics_queries.md

## Analytics Queries for Swing Profiles and User Profiles

This document provides example queries to analyze logs from `automation/reports/` for performance, user feedback, and compliance.

### 1. Generation Metrics by User
Query generation logs for a specific user to track perplexity and engagement.
```python
import yaml
from pathlib import Path

user = "john_doe"
logs = Path("automation/reports/").glob(f"generation_{user}_*.yaml")
for log in logs:
    data = yaml.safe_load(log.read_text())
    print(f"Goal: {data['goal']}, Tokens: {data['generated_tokens']}, Perplexity: {data['ratings']['perplexity']}")
```

### 2. Swing Profile Effectiveness
Compare metrics across swing profiles.
```python
import yaml
from collections import defaultdict

profiles = defaultdict(list)
for log in Path("automation/reports/").glob("generation_*.yaml"):
    data = yaml.safe_load(log.read_text())
    profiles[data['swing_profile']].append(data['ratings']['engagement'])

for profile, engagements in profiles.items():
    avg = sum(engagements) / len(engagements)
    print(f"Profile {profile}: Avg Engagement {avg:.2f}")
```

### 3. Compliance Check by Persona
Check refusal patterns and safety scores for a persona.
```python
import yaml

persona = "creator"
logs = Path("automation/reports/").glob(f"generation_*_{persona}*.yaml")  # Adjust pattern
violations = 0
for log in logs:
    data = yaml.safe_load(log.read_text())
    if data.get('refusals'):  # Placeholder for actual refusal logs
        violations += 1
print(f"Persona {persona}: {violations} violations")
```

### 4. Publishing Success Rate
Track publish events by platform.
```python
import yaml

platform = "youtube"
logs = Path("automation/reports/").glob(f"publish_*_{platform}.yaml")
successes = 0
for log in logs:
    data = yaml.safe_load(log.read_text())
    if data.get('success'):  # Placeholder for success flag
        successes += 1
rate = successes / len(logs) if logs else 0
print(f"Platform {platform}: Success Rate {rate:.2f}")
```

### 5. Overall Tour-Guide Usage
Aggregate stats across all users.
```python
import yaml
from collections import Counter

users = Counter()
goals = Counter()
for log in Path("automation/reports/").glob("generation_*.yaml"):
    data = yaml.safe_load(log.read_text())
    users[data['user']] += 1
    goals[data['goal']] += 1

print("Top Users:", users.most_common(5))
print("Top Goals:", goals.most_common(5))
```

Use these queries to iterate on profiles and ensure production safety.
