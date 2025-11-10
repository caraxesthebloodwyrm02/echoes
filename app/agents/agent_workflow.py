"""
Agent Workflow System for EchoesAssistantV2

Multi-agent orchestration with chaining, triage, and conditional execution.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

UTC = timezone.utc
from enum import Enum
from typing import Any


class AgentRole(Enum):
    """Agent roles for different tasks."""

    TRIAGE = "triage"
    QUERY_REWRITE = "query_rewrite"
    RESEARCH = "research"
    ANALYSIS = "analysis"
    SUMMARY = "summary"
    APPROVAL = "approval"
    REJECTION = "rejection"


@dataclass
class AgentStep:
    """Single step in an agent workflow."""

    agent_name: str
    role: AgentRole
    instructions: str
    input_data: dict[str, Any]
    output: dict[str, Any] | None = None
    duration_ms: float = 0
    timestamp: str = ""
    success: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "role": self.role.value}


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""

    workflow_id: str
    steps: list[AgentStep]
    final_output: Any
    total_duration_ms: float
    success: bool
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "steps": [s.to_dict() for s in self.steps],
            "final_output": self.final_output,
            "total_duration_ms": self.total_duration_ms,
            "success": self.success,
            "error": self.error,
        }


class AgentWorkflow:
    """Multi-agent workflow orchestrator."""

    def __init__(self, assistant):
        """Initialize with reference to assistant."""
        self.assistant = assistant
        self.conversation_history: list[dict[str, Any]] = []
        self.workflow_counter = 0

    def _create_step(
        self,
        agent_name: str,
        role: AgentRole,
        instructions: str,
        input_data: dict[str, Any],
    ) -> AgentStep:
        """Create a workflow step."""
        return AgentStep(
            agent_name=agent_name,
            role=role,
            instructions=instructions,
            input_data=input_data,
            timestamp=datetime.now(UTC).isoformat(),
        )

    def _execute_step(self, step: AgentStep) -> AgentStep:
        """Execute a single workflow step."""
        import time

        start_time = time.time()

        try:
            # Add instructions to conversation
            self.conversation_history.append(
                {"role": "system", "content": step.instructions}
            )

            # Add input data
            if "query" in step.input_data:
                self.conversation_history.append(
                    {"role": "user", "content": step.input_data["query"]}
                )

            # Execute via assistant
            response = self.assistant.chat(
                message=step.input_data.get("query", ""),
                system_prompt=step.instructions,
                stream=False,
                show_status=False,
            )

            # Store output
            step.output = {"response": response}
            step.success = True

        except Exception as e:
            step.output = {"error": str(e)}
            step.success = False

        step.duration_ms = (time.time() - start_time) * 1000
        return step

    def run_triage_workflow(
        self, user_input: str, context: dict[str, Any] | None = None
    ) -> WorkflowResult:
        """
        Run a triage workflow to classify and route requests.

        Pattern: Triage -> Classify -> Route -> Execute
        """
        import time

        self.workflow_counter += 1
        workflow_id = f"workflow_{self.workflow_counter}"
        start_time = time.time()
        steps = []

        try:
            # Step 1: Triage/Classify
            triage_step = self._create_step(
                agent_name="triage_agent",
                role=AgentRole.TRIAGE,
                instructions="""Classify the user's request into one of these categories:
                - 'qa': Simple question answering
                - 'research': Requires web search or data gathering
                - 'analysis': Requires code analysis or document comparison
                - 'planning': Requires creating work plans or strategies
                - 'structured_query': Requires database or structured data queries

                Respond with just the category name.""",
                input_data={"query": user_input, "context": context or {}},
            )
            triage_step = self._execute_step(triage_step)
            steps.append(triage_step)

            if not triage_step.success:
                raise Exception("Triage failed")

            classification = triage_step.output["response"].strip().lower()

            # Step 2: Route based on classification
            if classification == "qa":
                result_step = self._execute_qa_workflow(user_input)
            elif classification == "research":
                result_step = self._execute_research_workflow(user_input)
            elif classification == "analysis":
                result_step = self._execute_analysis_workflow(user_input)
            elif classification == "planning":
                result_step = self._execute_planning_workflow(user_input)
            elif classification == "structured_query":
                result_step = self._execute_structured_query_workflow(user_input)
            else:
                result_step = self._execute_default_workflow(user_input)

            steps.append(result_step)
            final_output = result_step.output

            total_duration = (time.time() - start_time) * 1000
            return WorkflowResult(
                workflow_id=workflow_id,
                steps=steps,
                final_output=final_output,
                total_duration_ms=total_duration,
                success=True,
            )

        except Exception as e:
            total_duration = (time.time() - start_time) * 1000
            return WorkflowResult(
                workflow_id=workflow_id,
                steps=steps,
                final_output=None,
                total_duration_ms=total_duration,
                success=False,
                error=str(e),
            )

    def _execute_qa_workflow(self, query: str) -> AgentStep:
        """Execute Q&A workflow."""
        step = self._create_step(
            agent_name="qa_agent",
            role=AgentRole.ANALYSIS,
            instructions="Answer the question concisely using available knowledge. Use bullet points.",
            input_data={"query": query},
        )
        return self._execute_step(step)

    def _execute_research_workflow(self, query: str) -> AgentStep:
        """Execute research workflow with knowledge gathering."""
        # Gather knowledge first
        knowledge_results = self.assistant.search_knowledge(query=query, limit=5)

        step = self._create_step(
            agent_name="research_agent",
            role=AgentRole.RESEARCH,
            instructions=f"""Research the topic using available knowledge and filesystem.

            Existing knowledge: {json.dumps(knowledge_results[:3])}

            Provide a comprehensive answer with sources.""",
            input_data={"query": query, "knowledge": knowledge_results},
        )
        return self._execute_step(step)

    def _execute_analysis_workflow(self, query: str) -> AgentStep:
        """Execute analysis workflow."""
        step = self._create_step(
            agent_name="analysis_agent",
            role=AgentRole.ANALYSIS,
            instructions="""Analyze the request and provide detailed insights.
            Use filesystem tools if needed to examine code or documents.
            Structure your analysis with:
            1. Summary
            2. Key findings
            3. Recommendations""",
            input_data={"query": query},
        )
        return self._execute_step(step)

    def _execute_planning_workflow(self, query: str) -> AgentStep:
        """Execute planning workflow."""
        step = self._create_step(
            agent_name="planning_agent",
            role=AgentRole.ANALYSIS,
            instructions="""Create a structured work plan with:
            1. Goal identification
            2. Key milestones
            3. Resource requirements
            4. Timeline
            5. Success criteria

            Be specific and actionable.""",
            input_data={"query": query},
        )
        return self._execute_step(step)

    def _execute_structured_query_workflow(self, query: str) -> AgentStep:
        """Execute structured query workflow."""
        step = self._create_step(
            agent_name="structured_query_agent",
            role=AgentRole.ANALYSIS,
            instructions="""Interpret the natural language query and:
            1. Identify what data is being requested
            2. Determine what operations are needed
            3. Execute using available tools (ATLAS, filesystem, etc.)
            4. Format results clearly""",
            input_data={"query": query},
        )
        return self._execute_step(step)

    def _execute_default_workflow(self, query: str) -> AgentStep:
        """Execute default workflow."""
        step = self._create_step(
            agent_name="default_agent",
            role=AgentRole.ANALYSIS,
            instructions="Provide helpful assistance based on the request.",
            input_data={"query": query},
        )
        return self._execute_step(step)

    def run_comparison_workflow(self, file1: str, file2: str) -> WorkflowResult:
        """
        Run document comparison workflow.

        Pattern: Read -> Compare -> Propose -> Approve/Reject
        """
        import time

        self.workflow_counter += 1
        workflow_id = f"comparison_{self.workflow_counter}"
        start_time = time.time()
        steps = []

        try:
            # Step 1: Read both files
            content1 = self.assistant.read_file(file1)
            content2 = self.assistant.read_file(file2)

            if not content1["success"] or not content2["success"]:
                raise Exception("Failed to read files")

            # Step 2: Compare
            compare_step = self._create_step(
                agent_name="comparison_agent",
                role=AgentRole.ANALYSIS,
                instructions=f"""Compare these two documents and identify:
                1. Key differences
                2. Additions/Deletions
                3. Structural changes
                4. Recommendations for reconciliation

                Document 1: {file1}
                Document 2: {file2}""",
                input_data={
                    "file1": file1,
                    "file2": file2,
                    "content1": content1["content"][:1000],
                    "content2": content2["content"][:1000],
                },
            )
            compare_step = self._execute_step(compare_step)
            steps.append(compare_step)

            # Step 3: Propose reconciliation
            propose_step = self._create_step(
                agent_name="proposal_agent",
                role=AgentRole.SUMMARY,
                instructions="Based on the comparison, propose a reconciliation strategy.",
                input_data={"comparison": compare_step.output},
            )
            propose_step = self._execute_step(propose_step)
            steps.append(propose_step)

            total_duration = (time.time() - start_time) * 1000
            return WorkflowResult(
                workflow_id=workflow_id,
                steps=steps,
                final_output=propose_step.output,
                total_duration_ms=total_duration,
                success=True,
            )

        except Exception as e:
            total_duration = (time.time() - start_time) * 1000
            return WorkflowResult(
                workflow_id=workflow_id,
                steps=steps,
                final_output=None,
                total_duration_ms=total_duration,
                success=False,
                error=str(e),
            )

    def run_data_enrichment_workflow(
        self, topic: str, context: dict[str, Any] | None = None
    ) -> WorkflowResult:
        """
        Run data enrichment workflow.

        Pattern: Query -> Search -> Gather -> Synthesize
        """
        import time

        self.workflow_counter += 1
        workflow_id = f"enrichment_{self.workflow_counter}"
        start_time = time.time()
        steps = []

        try:
            # Step 1: Rewrite query
            rewrite_step = self._create_step(
                agent_name="query_rewriter",
                role=AgentRole.QUERY_REWRITE,
                instructions="Rewrite the query to be more specific and searchable.",
                input_data={"query": topic, "context": context or {}},
            )
            rewrite_step = self._execute_step(rewrite_step)
            steps.append(rewrite_step)

            # Step 2: Gather data
            gather_step = self._create_step(
                agent_name="data_gatherer",
                role=AgentRole.RESEARCH,
                instructions="""Gather comprehensive data about the topic:
                1. Search existing knowledge
                2. Search filesystem for relevant files
                3. Use available tools
                4. Compile findings""",
                input_data={"query": rewrite_step.output["response"]},
            )
            gather_step = self._execute_step(gather_step)
            steps.append(gather_step)

            # Step 3: Synthesize
            synth_step = self._create_step(
                agent_name="synthesizer",
                role=AgentRole.SUMMARY,
                instructions="Synthesize all gathered data into a comprehensive answer.",
                input_data={"data": gather_step.output},
            )
            synth_step = self._execute_step(synth_step)
            steps.append(synth_step)

            total_duration = (time.time() - start_time) * 1000
            return WorkflowResult(
                workflow_id=workflow_id,
                steps=steps,
                final_output=synth_step.output,
                total_duration_ms=total_duration,
                success=True,
            )

        except Exception as e:
            total_duration = (time.time() - start_time) * 1000
            return WorkflowResult(
                workflow_id=workflow_id,
                steps=steps,
                final_output=None,
                total_duration_ms=total_duration,
                success=False,
                error=str(e),
            )

    def get_workflow_history(self) -> list[dict[str, Any]]:
        """Get conversation history from workflow."""
        return self.conversation_history

    def reset_history(self):
        """Reset conversation history."""
        self.conversation_history = []
