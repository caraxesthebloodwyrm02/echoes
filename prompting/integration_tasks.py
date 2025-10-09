"""
Integration tasks for the automation framework
These tasks can be used with the existing automation system
"""

import asyncio

from automation.core.context import Context
from automation.core.logger import AutomationLogger

from .system import prompting_system


def analyze_codebase_structure(context: Context):
    """
    Automation task: Analyze codebase structure using prompting system
    """
    logger = AutomationLogger()

    if context.dry_run:
        logger.info("[DRY-RUN] Would analyze codebase structure using IDE mode")
        return

    prompt = "Analyze the current codebase structure, identify patterns, and suggest organizational improvements"

    # Run synchronously for automation framework compatibility
    result = asyncio.run(
        prompting_system.process_prompt(
            prompt=prompt, mode="ide", enable_data_loop=True
        )
    )

    logger.success("Codebase analysis completed")
    print(f"\n{result['response']}\n")


def generate_documentation(context: Context):
    """
    Automation task: Generate documentation using prompting system
    """
    logger = AutomationLogger()

    target_file = context.extra_data.get("target_file", "README.md")

    if context.dry_run:
        logger.info(f"[DRY-RUN] Would generate documentation for {target_file}")
        return

    prompt = f"Generate comprehensive documentation for the current project, focusing on {target_file}"

    result = asyncio.run(
        prompting_system.process_prompt(
            prompt=prompt, mode="ide", enable_data_loop=False
        )
    )

    logger.success(f"Documentation generated for {target_file}")
    print(f"\n{result['response']}\n")


def business_analysis(context: Context):
    """
    Automation task: Perform business analysis using prompting system
    """
    logger = AutomationLogger()

    focus_area = context.extra_data.get("focus_area", "general")

    if context.dry_run:
        logger.info(
            f"[DRY-RUN] Would perform business analysis focusing on {focus_area}"
        )
        return

    prompt = f"Analyze the business value and ROI potential of this project, focusing on {focus_area}"

    result = asyncio.run(
        prompting_system.process_prompt(
            prompt=prompt, mode="business", enable_data_loop=True
        )
    )

    logger.success("Business analysis completed")
    print(f"\n{result['response']}\n")


def creative_brainstorm(context: Context):
    """
    Automation task: Creative brainstorming using Star Stuff mode
    """
    logger = AutomationLogger()

    topic = context.extra_data.get("topic", "innovation opportunities")

    if context.dry_run:
        logger.info(f"[DRY-RUN] Would brainstorm creative ideas about {topic}")
        return

    prompt = f"Explore creative possibilities and innovative approaches for {topic} in this project"

    result = asyncio.run(
        prompting_system.process_prompt(
            prompt=prompt, mode="star_stuff", enable_data_loop=False
        )
    )

    logger.success("Creative brainstorming completed")
    print(f"\n{result['response']}\n")


def quick_summary(context: Context):
    """
    Automation task: Generate quick summary using Concise mode
    """
    logger = AutomationLogger()

    topic = context.extra_data.get("topic", "project status")

    if context.dry_run:
        logger.info(f"[DRY-RUN] Would generate concise summary of {topic}")
        return

    prompt = f"Provide a concise summary of {topic} for this project"

    result = asyncio.run(
        prompting_system.process_prompt(
            prompt=prompt, mode="concise", enable_data_loop=False
        )
    )

    logger.success("Quick summary generated")
    print(f"\n{result['response']}\n")


def interactive_help(context: Context):
    """
    Automation task: Provide interactive help using Conversational mode
    """
    logger = AutomationLogger()

    question = context.extra_data.get("question", "How does this project work?")

    if context.dry_run:
        logger.info(f"[DRY-RUN] Would provide interactive help for: {question}")
        return

    result = asyncio.run(
        prompting_system.process_prompt(
            prompt=question, mode="conversational", enable_data_loop=False
        )
    )

    logger.success("Interactive help provided")
    print(f"\n{result['response']}\n")


# Task registry for automation framework
PROMPTING_TASKS = {
    "analyze_codebase_structure": analyze_codebase_structure,
    "generate_documentation": generate_documentation,
    "business_analysis": business_analysis,
    "creative_brainstorm": creative_brainstorm,
    "quick_summary": quick_summary,
    "interactive_help": interactive_help,
}
