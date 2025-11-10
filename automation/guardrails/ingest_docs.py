import re


def parse_security_protocols(doc_path):
    """Parses the DEPLOYMENT_AND_OPERATIONS.md file to extract security protocols."""
    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()

    protocols = {}

    # Extract the entire "Security Measures" section
    security_section_match = re.search(
        r"## 2. Security Measures(.*?)---", content, re.DOTALL
    )
    if not security_section_match:
        return protocols

    security_content = security_section_match.group(1)

    # Find all protocol sections and their rules
    protocol_sections = re.findall(
        r"- \*\*(.*?)\*\*\n(.*?)(?=\n- \*\*|\Z)", security_content, re.DOTALL
    )

    for title, section_content in protocol_sections:
        title_key = title.lower().replace(" ", "_").replace("_and_", "_")
        rules = [rule.strip() for rule in re.findall(r"- (.*?)\n", section_content)]
        protocols[title_key] = rules

    return protocols


if __name__ == "__main__":
    doc_path = "e:\\Projects\\Development\\docs\\glimpse\\DEPLOYMENT_AND_OPERATIONS.md"
    security_protocols = parse_security_protocols(doc_path)
    import json

    print(json.dumps(security_protocols, indent=2))
