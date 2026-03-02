import json

with open("remediation/pip-audit-pre-scan.json") as f:
    data = json.load(f)

vulns = [d for d in data["dependencies"] if d.get("vulns", [])]
print(f"Found {len(vulns)} packages with vulnerabilities:")
for v in vulns:
    print(f"- {v['name']} {v['version']}: {len(v['vulns'])} vuln(s)")
    for vuln in v["vulns"]:
        print(f"  - {vuln['id']}: {vuln.get('description', 'N/A')[:100]}...")
