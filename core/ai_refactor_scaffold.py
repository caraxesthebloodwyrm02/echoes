#!/usr/bin/env python3
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

"""
AI-Powered Context-Aware Refactor Scaffold Generator
Uses GPT-4o to analyze and refactor the Echoes codebase
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.openai_integration import get_openai_integration


class AIRefactorScaffold:
    """AI-powered refactor scaffold generator using GPT-4o"""

    def __init__(self):
        self.openai_integration = get_openai_integration()
        self.project_root = PROJECT_ROOT

        if not self.openai_integration.is_configured:
            raise RuntimeError("OpenAI integration not configured. Set OPENAI_API_KEY.")

    def analyze_codebase(self) -> str:
        """Analyze the current Echoes codebase structure and key files"""

        # Key files to analyze
        key_files = [
            "main.py",  # Main REPL interface
            "bootstrap.py",  # Environment setup
            "setup_profiles.py",  # IDE configuration
            "utils/safe_imports.py",  # Import safety system
            "utils/openai_integration.py",  # OpenAI integration
            "src/modules/transformer.py",  # Text transformation
            "src/utils/budget_guard.py",  # Cost management
            "ai_agents/orchestrator.py",  # Agent orchestration
            "packages/core/config/__init__.py",  # Configuration
        ]

        codebase_analysis = []

        for file_path in key_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Truncate very large files for analysis
                    if len(content) > 10000:
                        content = (
                            content[:5000]
                            + "\n\n[... FILE TRUNCATED FOR ANALYSIS ...]\n\n"
                            + content[-2000:]
                        )

                    codebase_analysis.append(
                        f"""
=== FILE: {file_path} ===
Size: {len(content)} characters

CONTENT:
{content}
"""
                    )
                except Exception as e:
                    codebase_analysis.append(
                        f"""
=== FILE: {file_path} ===
ERROR READING FILE: {e}
"""
                    )
            else:
                codebase_analysis.append(
                    f"""
=== FILE: {file_path} ===
FILE NOT FOUND
"""
                )

        return "\n".join(codebase_analysis)

    def generate_refactor_scaffold(self) -> Dict[str, Any]:
        """Use GPT-4o to generate the refactor scaffold"""

        # Analyze current codebase
        codebase_content = self.analyze_codebase()

        # Project description
        project_description = """
        ECHOES AI PLATFORM - CURRENT ARCHITECTURE ANALYSIS

        Current State:
        - Interactive REPL system with AI assistant mode
        - Batch processing with budget protection
        - OpenAI integration via custom wrapper
        - Safe import system preventing cascade failures
        - Agent orchestration framework
        - Cost management and budget tracking
        - IDE integration and profile management

        Current Issues to Address:
        - Mixed concerns in main.py (CLI, REPL, assistant logic)
        - Scattered utilities across src/ and utils/
        - Tight coupling between components
        - Configuration scattered across multiple files
        - Test coverage gaps
        - Limited error recovery mechanisms

        Requirements for Refactor:
        - Modular architecture with clear separation of concerns
        - Context-aware configuration management
        - Extensible integration layer for APIs
        - Robust error handling and logging
        - Comprehensive test coverage
        - Clean CLI interface
        - Maintainable codebase structure
        """

        refactor_prompt = f"""
        You are a senior Python architect and AI systems expert. Analyze the provided Echoes codebase and generate a comprehensive context-aware refactor scaffold.

        REQUIREMENTS:
        1. Preserve all existing functionality while improving architecture
        2. Create modular, maintainable structure with clear separation of concerns
        3. Implement proper error handling and logging throughout
        4. Design extensible integration layer for AI APIs (OpenAI, future services)
        5. Include comprehensive test coverage structure
        6. Create clean CLI interface with modern command structure
        7. Implement context-aware configuration management
        8. Add proper documentation and type hints

        OUTPUT FORMAT:
        Return a valid JSON object with this exact structure:
        {{
          "structure": "ASCII tree diagram of the new directory structure",
          "files": [
            {{
              "path": "relative/path/to/file.py",
              "content": "complete file content as string",
              "description": "brief description of file purpose"
            }}
          ],
          "migrations": [
            {{
              "from": "old/path/file.py",
              "to": "new/path/file.py",
              "changes": "description of changes made"
            }}
          ],
          "dependencies": [
            {{
              "package": "package_name",
              "version": ">=1.0.0",
              "purpose": "why this dependency is needed"
            }}
          ]
        }}

        PROJECT DESCRIPTION:
        {project_description}

        CURRENT CODEBASE ANALYSIS:
        {codebase_content}
        """

        print("🤖 Sending codebase to GPT-4o for analysis and refactor generation...")
        print("This may take a moment...")

        response = self.openai_integration.create_completion(
            prompt=refactor_prompt,
            model="gpt-4o",  # Using GPT-4o as requested
            temperature=0.2,  # Lower temperature for more consistent architectural decisions
            max_tokens=12000,  # Large context for comprehensive refactor
        )

        if not response:
            raise RuntimeError("Failed to get refactor scaffold from OpenAI API")

        # Parse JSON response
        try:
            # Clean the response if it has markdown formatting
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]

            scaffold_data = json.loads(clean_response.strip())
            return scaffold_data

        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse AI response as JSON: {e}")
            print("Raw response preview:")
            print(response[:1000] + "..." if len(response) > 1000 else response)
            raise

    def create_scaffold_files(self, scaffold_data: Dict[str, Any]) -> None:
        """Create the scaffold files on disk"""

        print("\n📁 PROPOSED PROJECT STRUCTURE:")
        print("=" * 50)
        print(scaffold_data.get("structure", "No structure provided"))

        print("\n📝 CREATING SCAFFOLD FILES:")
        print("=" * 50)

        files_created = 0
        files_skipped = 0

        for file_info in scaffold_data.get("files", []):
            file_path = file_info["path"]
            content = file_info["content"]
            description = file_info.get("description", "")

            full_path = self.project_root / file_path

            # Create directory if it doesn't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Check if file already exists
            if full_path.exists():
                print(f"⚠️  Skipping existing file: {file_path}")
                files_skipped += 1
                continue

            try:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"✅ Created: {file_path}")
                if description:
                    print(f"   └─ {description}")
                files_created += 1

            except Exception as e:
                print(f"❌ Failed to create {file_path}: {e}")

        print("\n📊 SCAFFOLD CREATION SUMMARY:")
        print(f"   Files created: {files_created}")
        print(f"   Files skipped: {files_skipped}")

        # Show migrations if available
        migrations = scaffold_data.get("migrations", [])
        if migrations:
            print(f"   Migration guides: {len(migrations)}")

        # Show dependencies if available
        dependencies = scaffold_data.get("dependencies", [])
        if dependencies:
            print(f"   New dependencies: {len(dependencies)}")

    def show_migration_guide(self, scaffold_data: Dict[str, Any]) -> None:
        """Show migration guide for existing code"""

        migrations = scaffold_data.get("migrations", [])
        if not migrations:
            return

        print("\n🔄 MIGRATION GUIDE:")
        print("=" * 50)

        for migration in migrations:
            print(f"📁 {migration['from']} → {migration['to']}")
            print(f"   {migration.get('changes', 'See file for details')}")
            print()

    def show_dependencies(self, scaffold_data: Dict[str, Any]) -> None:
        """Show new dependencies to install"""

        dependencies = scaffold_data.get("dependencies", [])
        if not dependencies:
            return

        print("\n📦 NEW DEPENDENCIES TO INSTALL:")
        print("=" * 50)

        for dep in dependencies:
            package = dep["package"]
            version = dep.get("version", "latest")
            purpose = dep.get("purpose", "")

            print(f'pip install "{package}{version}"')
            if purpose:
                print(f"   └─ {purpose}")
            print()


def main():
    """Main execution"""
    print("🚀 AI-POWERED CONTEXT-AWARE REFACTOR SCAFFOLD GENERATOR")
    print("=" * 70)
    print("Using GPT-4o to analyze and refactor the Echoes codebase")
    print("=" * 70)

    try:
        # Initialize refactor system
        refactor = AIRefactorScaffold()

        # Generate scaffold using GPT-4o
        scaffold_data = refactor.generate_refactor_scaffold()

        # Create files
        refactor.create_scaffold_files(scaffold_data)

        # Show migration guide
        refactor.show_migration_guide(scaffold_data)

        # Show dependencies
        refactor.show_dependencies(scaffold_data)

        print("\n🎉 REFACTOR SCAFFOLD COMPLETE!")
        print("=" * 70)
        print("✅ AI-generated modular architecture created")
        print("✅ Context-aware design preserved")
        print("✅ Production-ready structure implemented")
        print()
        print("Next steps:")
        print("1. Review generated files")
        print("2. Install new dependencies: pip install -r requirements-new.txt")
        print("3. Run tests: pytest")
        print("4. Migrate existing code following the migration guide")

    except Exception as e:
        print(f"❌ Refactor generation failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
