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

import json
import os

from openai import OpenAI

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_ECHOES")
client = OpenAI(api_key=api_key)


def create_echoes_assistant():
    """Create a comprehensive OpenAI Assistant for ECHOES platform management"""

    # Load repository context
    try:
        with open("reports/echoes_snapshot.json", "r", encoding="utf-8") as f:
            snapshot = json.load(f)
    except FileNotFoundError:
        snapshot = {"codebase_metrics": {"total_files": 442, "python_files": 442}}

    # Create comprehensive system prompt
    system_prompt = f"""
You are ECHOES Assistant, an expert AI system designed to help manage, develop, and optimize the ECHOES platform.

## ECHOES PLATFORM OVERVIEW
ECHOES is a sophisticated modular Python AI orchestration platform with {snapshot["codebase_metrics"]["python_files"]} Python files and {snapshot["codebase_metrics"]["total_lines"]} lines of code. It features:

### CORE CAPABILITIES
- **AI Agent Orchestration**: Multi-agent coordination with OpenAI SDK integration
- **Security Framework**: Comprehensive security validation, encryption, and monitoring
- **Code Analysis**: Automated codebase analysis with batching and caching
- **Research Tools**: Trajectory-aligned development and harmonic resonance patterns
- **Development Workflow**: Poetry-based dependency management and CI/CD integration

### ARCHITECTURAL COMPONENTS
- **Orchestration Layer**: Agent coordination and task management
- **Security Packages**: Multi-vector security scanning and validation
- **Prompting Engine**: Advanced AI prompt engineering and response handling
- **Analysis Tools**: Code quality assessment and performance optimization
- **Research Framework**: Academic-to-production transition methodologies

### UNIQUE FEATURES
- **Trajectory Alignment**: Research-driven development methodology
- **Harmonic Resonance**: Novel AI system coordination patterns
- **Ethical AI Framework**: Built-in bias detection and fairness monitoring
- **Enterprise Ready**: Scalable architecture for production deployment

## YOUR ROLE & CAPABILITIES

### PRIMARY FUNCTIONS
1. **Code Analysis**: Analyze ECHOES codebase, identify improvements, review changes
2. **Architecture Guidance**: Provide architectural decisions and design recommendations
3. **Security Assessment**: Evaluate security implementations and suggest improvements
4. **Development Support**: Help with debugging, optimization, and feature development
5. **Research Integration**: Apply trajectory alignment and harmonic resonance concepts
6. **Documentation**: Generate and maintain comprehensive documentation

### TOOLS & INTEGRATIONS
- **File Search**: Navigate and analyze codebase files
- **Code Interpreter**: Execute code, run analysis, perform computations
- **Function Calling**: Interact with ECHOES APIs and external services

### WORKFLOW SUPPORT
- **Project Planning**: Assist with sprint planning and initiative tracking
- **Code Review**: Provide detailed code analysis and improvement suggestions
- **Testing Strategy**: Design and implement comprehensive testing approaches
- **Deployment Guidance**: Support CI/CD pipeline configuration and optimization
- **Performance Monitoring**: Analyze system performance and suggest optimizations

### COMMUNICATION STYLE
- Be direct, technical, and solution-oriented
- Reference specific files, functions, and architectural patterns
- Provide actionable recommendations with clear rationale
- Balance innovation with practical implementation
- Maintain focus on ECHOES platform excellence and user value

## RESPONSE GUIDELINES
- Always consider the broader ECHOES architecture and ecosystem
- Reference specific components, patterns, and methodologies
- Provide context-aware solutions that align with platform goals
- Suggest improvements that enhance scalability, security, and maintainability
- Focus on delivering measurable value to users and developers

You have access to the complete ECHOES codebase and can analyze, modify, and optimize any aspect of the platform. Your goal is to ensure ECHOES remains a world-class AI orchestration platform that bridges research and production excellence.
"""

    # Define assistant tools
    tools = [{"type": "file_search"}, {"type": "code_interpreter"}]

    # Define function tools for ECHOES integration
    functions = [
        {
            "name": "analyze_codebase",
            "description": "Perform comprehensive analysis of the ECHOES codebase",
            "parameters": {
                "type": "object",
                "properties": {
                    "analysis_type": {
                        "type": "string",
                        "enum": ["architecture", "security", "performance", "quality"],
                        "description": "Type of analysis to perform",
                    },
                    "focus_area": {
                        "type": "string",
                        "description": "Specific area to focus on (optional)",
                    },
                },
                "required": ["analysis_type"],
            },
        },
        {
            "name": "check_security",
            "description": "Run security analysis on ECHOES components",
            "parameters": {
                "type": "object",
                "properties": {
                    "component": {
                        "type": "string",
                        "description": "Component to analyze (e.g., 'orchestrator', 'security', 'api')",
                    },
                    "severity_level": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Minimum severity level to report",
                    },
                },
            },
        },
        {
            "name": "optimize_performance",
            "description": "Analyze and suggest performance optimizations",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_component": {
                        "type": "string",
                        "description": "Component to optimize",
                    },
                    "metric_focus": {
                        "type": "string",
                        "enum": ["latency", "throughput", "memory", "cpu"],
                        "description": "Performance metric to focus on",
                    },
                },
            },
        },
        {
            "name": "generate_trajectory_plan",
            "description": "Create a trajectory-aligned development plan",
            "parameters": {
                "type": "object",
                "properties": {
                    "objective": {
                        "type": "string",
                        "description": "Development objective or goal",
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Timeframe for completion",
                    },
                    "resources": {
                        "type": "string",
                        "description": "Available resources and constraints",
                    },
                },
                "required": ["objective"],
            },
        },
    ]

    # Add function tools to the tools list
    for function in functions:
        tools.append({"type": "function", "function": function})

    # Create the assistant
    try:
        assistant = client.beta.assistants.create(
            name="ECHOES Assistant",
            description="Expert AI assistant for managing and optimizing the ECHOES AI orchestration platform",
            instructions=system_prompt,
            model="gpt-4o",  # Latest model
            tools=tools,
            temperature=0.3,  # Balanced creativity and precision
            top_p=0.85,  # Allow some diversity in responses
            response_format={"type": "text"},  # Standard text responses
        )

        print("ECHOES Assistant created successfully!")
        print(f"Assistant ID: {assistant.id}")
        print(f"Model: {assistant.model}")
        print(f"Tools: {len(assistant.tools)} configured")
        print(f"Created: {assistant.created_at}")

        # Save assistant configuration
        assistant_config = {
            "assistant_id": assistant.id,
            "name": assistant.name,
            "description": assistant.description,
            "model": assistant.model,
            "tools": [tool.type for tool in assistant.tools],
            "temperature": assistant.temperature,
            "top_p": assistant.top_p,
            "created_at": assistant.created_at,
            "instructions_summary": system_prompt[:500] + "...",
        }

        os.makedirs("assistants", exist_ok=True)
        with open(
            "assistants/echoes_assistant_config.json", "w", encoding="utf-8"
        ) as f:
            json.dump(assistant_config, f, indent=2, ensure_ascii=False)

        print("Configuration saved to assistants/echoes_assistant_config.json")
        return assistant

    except Exception as e:
        print(f"Error creating assistant: {e}")
        return None


def upload_codebase_files(assistant_id):
    """Upload key ECHOES files for the assistant to reference"""

    key_files = [
        "comprehensive_analysis.py",
        "ai_agents/orchestrator.py",
        "packages/security/__init__.py",
        "prompting/core/inference_engine.py",
        "reports/echoes_snapshot.json",
        "README.md",
        "pyproject.toml",
    ]

    uploaded_files = []

    for file_path in key_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, "rb") as f:
                    file_obj = client.files.create(file=f, purpose="assistants")
                uploaded_files.append({"filename": file_path, "file_id": file_obj.id})
                print(f"Uploaded: {file_path} -> {file_obj.id}")
            except Exception as e:
                print(f"Failed to upload {file_path}: {e}")

    # Update assistant with file references
    if uploaded_files:
        file_ids = [f["file_id"] for f in uploaded_files]

        try:
            client.beta.assistants.update(
                assistant_id=assistant_id,
                tool_resources={"file_search": {"file_ids": file_ids}},
            )
            print(f"Updated assistant with {len(file_ids)} reference files")
        except Exception as e:
            print(f"Failed to update assistant: {e}")

    return uploaded_files


if __name__ == "__main__":
    print("Creating ECHOES Assistant...\n")

    # Create the assistant
    assistant = create_echoes_assistant()

    if assistant:
        print("\nUploading codebase files for reference...")
        uploaded_files = upload_codebase_files(assistant.id)

        print("\nECHOES Assistant Setup Complete!")
        print(f"- Assistant ID: {assistant.id}")
        print(f"- Files uploaded: {len(uploaded_files)}")
        print("- Ready for ECHOES platform management and development support")
    else:
        print("Failed to create ECHOES Assistant")
