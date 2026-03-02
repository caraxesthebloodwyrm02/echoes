#!/usr/bin/env python3
"""
Advanced Echoes AI Assistant V3 - Legal & Financial Decision Support

Enhanced assistant with specialized capabilities for:
- Legal analysis and advice
- Financial decision making
- Tool-based function calling
- Pattern-based challenge detection
- Direct RAG integration for domain knowledge
- Professional-grade response formatting

Architecture: Multi-agent with specialized tools and context-aware responses
"""

import asyncio
import json
import os
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from direct_rag_system import DirectRAGSystem
from openai import OpenAI


class DecisionDomain(Enum):
    """Specialized decision domains."""

    LEGAL = "legal"
    FINANCIAL = "financial"
    BUSINESS = "business"
    TECHNICAL = "technical"
    GENERAL = "general"


class ToolCategory(Enum):
    """Tool categorization for decision support."""

    ANALYSIS = "analysis"
    CALCULATION = "calculation"
    EVALUATION = "evaluation"
    RESEARCH = "research"
    VALIDATION = "validation"


@dataclass
class ToolDefinition:
    """Structured tool definition for function calling."""

    name: str
    description: str
    category: ToolCategory
    domain: DecisionDomain
    parameters: dict[str, Any]
    handler: Callable
    requires_context: bool = False
    confidence_threshold: float = 0.8


@dataclass
class DecisionContext:
    """Context for decision-making scenarios."""

    domain: DecisionDomain
    complexity: str  # simple, moderate, complex
    urgency: str  # low, medium, high
    stakeholders: list[str]
    constraints: list[str]
    objectives: list[str]
    available_tools: list[str] = field(default_factory=list)
    retrieved_knowledge: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ProfessionalResponse:
    """Structured professional response format."""

    domain: DecisionDomain
    confidence_score: float
    recommendations: list[str]
    risks_assessed: list[str]
    next_steps: list[str]
    legal_disclaimers: list[str] = field(default_factory=list)
    financial_projections: dict[str, Any] = field(default_factory=dict)
    sources_cited: list[str] = field(default_factory=list)
    formatted_response: str = ""


class AdvancedEchoesAssistant:
    """
    Advanced AI assistant with legal and financial decision-making capabilities.

    Features:
    - Domain-specialized knowledge bases
    - Tool-based function calling
    - Pattern recognition for challenges
    - Professional response formatting
    - Context-aware decision support
    """

    def __init__(self, api_key: str | None = None):
        """Initialize the advanced assistant."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")

        self.client = OpenAI(api_key=self.api_key)

        # Initialize specialized RAG systems for each domain
        self.knowledge_bases = self._initialize_knowledge_bases()

        # Initialize tool registry
        self.tools = self._initialize_tools()

        # Pattern recognition for challenges
        self.challenge_patterns = self._initialize_challenge_patterns()

        # Response formatter
        self.response_formatter = ProfessionalResponseFormatter()

        print(
            "🚀 Advanced Echoes Assistant V3 initialized with legal & financial capabilities"
        )

    def _initialize_knowledge_bases(self) -> dict[DecisionDomain, DirectRAGSystem]:
        """Initialize domain-specific knowledge bases."""
        knowledge_bases = {}

        # Legal knowledge base
        legal_kb = DirectRAGSystem(api_key=self.api_key)
        legal_kb.embedding_model = "text-embedding-3-small"
        legal_kb.completion_model = "gpt-4o"  # Higher reasoning for legal

        # Financial knowledge base
        financial_kb = DirectRAGSystem(api_key=self.api_key)
        financial_kb.embedding_model = "text-embedding-3-small"
        financial_kb.completion_model = "gpt-4o"  # Higher reasoning for financial

        # Business knowledge base
        business_kb = DirectRAGSystem(api_key=self.api_key)
        business_kb.embedding_model = "text-embedding-3-small"
        business_kb.completion_model = "gpt-4o-mini"

        knowledge_bases[DecisionDomain.LEGAL] = legal_kb
        knowledge_bases[DecisionDomain.FINANCIAL] = financial_kb
        knowledge_bases[DecisionDomain.BUSINESS] = business_kb

        return knowledge_bases

    def _initialize_tools(self) -> dict[str, ToolDefinition]:
        """Initialize specialized tools for decision support."""
        tools = {}

        # Legal Tools
        tools["analyze_contract_risks"] = ToolDefinition(
            name="analyze_contract_risks",
            description="Analyze legal risks in contracts and agreements",
            category=ToolCategory.ANALYSIS,
            domain=DecisionDomain.LEGAL,
            parameters={
                "type": "object",
                "properties": {
                    "contract_text": {
                        "type": "string",
                        "description": "Contract content to analyze",
                    },
                    "risk_categories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific risk categories to focus on",
                    },
                },
                "required": ["contract_text"],
            },
            handler=self._analyze_contract_risks,
        )

        tools["evaluate_legal_precedence"] = ToolDefinition(
            name="evaluate_legal_precedence",
            description="Evaluate legal precedence and case law relevance",
            category=ToolCategory.EVALUATION,
            domain=DecisionDomain.LEGAL,
            parameters={
                "type": "object",
                "properties": {
                    "legal_issue": {
                        "type": "string",
                        "description": "Legal issue to evaluate",
                    },
                    "jurisdiction": {
                        "type": "string",
                        "description": "Legal jurisdiction",
                    },
                },
                "required": ["legal_issue"],
            },
            handler=self._evaluate_legal_precedence,
        )

        # Financial Tools
        tools["calculate_roi"] = ToolDefinition(
            name="calculate_roi",
            description="Calculate return on investment with projections",
            category=ToolCategory.CALCULATION,
            domain=DecisionDomain.FINANCIAL,
            parameters={
                "type": "object",
                "properties": {
                    "initial_investment": {
                        "type": "number",
                        "description": "Initial investment amount",
                    },
                    "expected_returns": {
                        "type": "number",
                        "description": "Expected return amount",
                    },
                    "time_period_years": {
                        "type": "number",
                        "description": "Investment time period in years",
                    },
                    "risk_adjustment": {
                        "type": "number",
                        "description": "Risk adjustment factor (0-1)",
                    },
                },
                "required": [
                    "initial_investment",
                    "expected_returns",
                    "time_period_years",
                ],
            },
            handler=self._calculate_roi,
        )

        tools["evaluate_fair_price"] = ToolDefinition(
            name="evaluate_fair_price",
            description="Evaluate fair market price for goods/services/work",
            category=ToolCategory.EVALUATION,
            domain=DecisionDomain.FINANCIAL,
            parameters={
                "type": "object",
                "properties": {
                    "item_description": {
                        "type": "string",
                        "description": "Description of item/service/work",
                    },
                    "market_rates": {
                        "type": "object",
                        "description": "Market rate data",
                    },
                    "complexity_factors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Complexity adjustment factors",
                    },
                },
                "required": ["item_description"],
            },
            handler=self._evaluate_fair_price,
        )

        tools["calculate_work_value"] = ToolDefinition(
            name="calculate_work_value",
            description="Calculate fair value for work hours and deliverables",
            category=ToolCategory.CALCULATION,
            domain=DecisionDomain.FINANCIAL,
            parameters={
                "type": "object",
                "properties": {
                    "hours_required": {
                        "type": "number",
                        "description": "Hours of work required",
                    },
                    "skill_level": {
                        "type": "string",
                        "description": "Required skill level",
                    },
                    "market_rate_per_hour": {
                        "type": "number",
                        "description": "Market rate per hour",
                    },
                    "complexity_multiplier": {
                        "type": "number",
                        "description": "Complexity adjustment multiplier",
                    },
                },
                "required": ["hours_required", "skill_level"],
            },
            handler=self._calculate_work_value,
        )

        return tools

    def _initialize_challenge_patterns(self) -> dict[str, dict[str, Any]]:
        """Initialize pattern recognition for user challenges."""
        return {
            "contract_review": {
                "patterns": [
                    r"review.*contract",
                    r"analyze.*agreement",
                    r"legal.*document",
                ],
                "domain": DecisionDomain.LEGAL,
                "tools": ["analyze_contract_risks"],
                "response_template": "contract_analysis",
            },
            "pricing_negotiation": {
                "patterns": [
                    r"fair.*price",
                    r"market.*rate",
                    r"worth.*pay",
                    r"charge.*for",
                ],
                "domain": DecisionDomain.FINANCIAL,
                "tools": ["evaluate_fair_price", "calculate_work_value"],
                "response_template": "pricing_analysis",
            },
            "investment_decision": {
                "patterns": [
                    r"invest.*in",
                    r"roi",
                    r"return.*investment",
                    r"financial.*decision",
                ],
                "domain": DecisionDomain.FINANCIAL,
                "tools": ["calculate_roi", "evaluate_fair_price"],
                "response_template": "investment_analysis",
            },
            "legal_advice": {
                "patterns": [
                    r"legal.*advice",
                    r"law.*says",
                    r"legally.*allowed",
                    r"court.*case",
                ],
                "domain": DecisionDomain.LEGAL,
                "tools": ["evaluate_legal_precedence"],
                "response_template": "legal_analysis",
            },
        }

    def analyze_user_query(self, query: str) -> DecisionContext:
        """Analyze user query to determine context and required tools."""
        context = DecisionContext(
            domain=DecisionDomain.GENERAL,
            complexity="simple",
            urgency="medium",
            stakeholders=["user"],
            constraints=[],
            objectives=[],
        )

        # Detect domain and complexity
        if any(
            word in query.lower()
            for word in ["contract", "legal", "law", "agreement", "court"]
        ):
            context.domain = DecisionDomain.LEGAL
        elif any(
            word in query.lower()
            for word in ["price", "cost", "value", "investment", "roi", "financial"]
        ):
            context.domain = DecisionDomain.FINANCIAL
        elif any(
            word in query.lower()
            for word in ["business", "company", "market", "strategy"]
        ):
            context.domain = DecisionDomain.BUSINESS

        # Detect complexity
        if len(query.split()) > 50 or any(
            word in query.lower() for word in ["complex", "detailed", "comprehensive"]
        ):
            context.complexity = "complex"
        elif len(query.split()) > 20:
            context.complexity = "moderate"

        # Detect urgency
        if any(
            word in query.lower()
            for word in ["urgent", "asap", "deadline", "immediately"]
        ):
            context.urgency = "high"
        elif any(word in query.lower() for word in ["soon", "week", "month"]):
            context.urgency = "medium"

        # Match challenge patterns
        for challenge_type, pattern_config in self.challenge_patterns.items():
            for pattern in pattern_config["patterns"]:
                if re.search(pattern, query, re.IGNORECASE):
                    context.domain = pattern_config["domain"]
                    context.available_tools.extend(pattern_config["tools"])
                    break

        return context

    async def process_query(
        self, query: str, user_context: dict[str, Any] | None = None
    ) -> ProfessionalResponse:
        """Process user query with full decision support pipeline."""
        print(f"🎯 Processing query: {query[:100]}...")

        # Step 1: Analyze query context
        decision_context = self.analyze_user_query(query)

        # Step 2: Retrieve domain knowledge
        knowledge_base = self.knowledge_bases.get(decision_context.domain)
        if knowledge_base:
            retrieved_docs = knowledge_base.search(query, top_k=3)
            decision_context.retrieved_knowledge = retrieved_docs

        # Step 3: Determine required tools
        required_tools = []
        for tool_name in decision_context.available_tools:
            if tool_name in self.tools:
                required_tools.append(self.tools[tool_name])

        # Step 4: Execute tools if needed
        tool_results = {}
        for tool in required_tools:
            try:
                # Extract parameters from query (simplified version)
                params = self._extract_tool_parameters(query, tool)
                if params:
                    result = await tool.handler(**params)
                    tool_results[tool.name] = result
            except Exception as e:
                print(f"Tool execution error for {tool.name}: {e}")
                tool_results[tool.name] = {"error": str(e)}

        # Step 5: Generate comprehensive response
        response = await self._generate_professional_response(
            query, decision_context, tool_results, user_context
        )

        return response

    def _extract_tool_parameters(
        self, query: str, tool: ToolDefinition
    ) -> dict[str, Any] | None:
        """Extract parameters for tool execution from query."""
        # Simplified parameter extraction - in production, use more sophisticated NLP
        params = {}

        if tool.name == "calculate_work_value":
            # Extract hours, skill level, etc. from query
            hours_match = re.search(r"(\d+)\s*hours?", query, re.IGNORECASE)
            if hours_match:
                params["hours_required"] = int(hours_match.group(1))

            skill_match = re.search(
                r"(senior|junior|expert|intermediate)", query, re.IGNORECASE
            )
            if skill_match:
                params["skill_level"] = skill_match.group(1).lower()

        elif tool.name == "evaluate_fair_price":
            # Extract item description
            params["item_description"] = query

        elif tool.name == "calculate_roi":
            # Extract financial numbers
            investment_match = re.search(r"\$?(\d+(?:,\d{3})*(?:\.\d{2})?)", query)
            if investment_match:
                params["initial_investment"] = float(
                    investment_match.group(1).replace(",", "")
                )

        return params if params else None

    async def _generate_professional_response(
        self,
        query: str,
        context: DecisionContext,
        tool_results: dict[str, Any],
        user_context: dict[str, Any] | None,
    ) -> ProfessionalResponse:
        """Generate professional response with all analysis components."""

        # Build comprehensive prompt
        system_prompt = self._build_system_prompt(context, tool_results)
        user_prompt = (
            f"Query: {query}\n\nTool Results: {json.dumps(tool_results, indent=2)}"
        )

        # Generate response using OpenAI
        response = self.client.chat.completions.create(
            model="gpt-4o",  # Use most capable model for professional responses
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=2000,
            temperature=0.3,  # Lower temperature for professional responses
        )

        raw_response = response.choices[0].message.content

        # Parse and structure the response
        structured_response = self.response_formatter.parse_and_structure(
            raw_response, context, tool_results
        )

        return structured_response

    def _build_system_prompt(
        self, context: DecisionContext, tool_results: dict[str, Any]
    ) -> str:
        """Build comprehensive system prompt for professional responses."""
        domain_knowledge = ""
        if context.retrieved_knowledge:
            knowledge_texts = [
                doc.get("content", "") for doc in context.retrieved_knowledge[:2]
            ]
            domain_knowledge = "\n".join(knowledge_texts)

        prompt = f"""You are an advanced AI assistant specializing in {context.domain.value} decision support.

DOMAIN: {context.domain.value.upper()}
COMPLEXITY: {context.complexity.upper()}
URGENCY: {context.urgency.upper()}

RELEVANT KNOWLEDGE:
{domain_knowledge}

TOOL RESULTS AVAILABLE:
{json.dumps(tool_results, indent=2)}

INSTRUCTIONS:
1. Provide professional, well-structured analysis
2. Include specific recommendations with reasoning
3. Assess and clearly state risks and limitations
4. Suggest concrete next steps
5. Include appropriate legal/financial disclaimers
6. Cite sources and reasoning methods
7. Maintain objectivity and professional tone

Format your response as a structured professional analysis."""

        return prompt

    # Tool Handlers
    async def _analyze_contract_risks(
        self, contract_text: str, risk_categories: list[str] = None
    ) -> dict[str, Any]:
        """Analyze contract risks."""
        # Simplified implementation - in production, use specialized legal AI
        risks = {
            "identified_risks": ["Standard contract clauses identified"],
            "severity": "low",
            "recommendations": ["Review with legal counsel"],
            "confidence": 0.7,
        }
        return risks

    async def _evaluate_legal_precedence(
        self, legal_issue: str, jurisdiction: str = "general"
    ) -> dict[str, Any]:
        """Evaluate legal precedence."""
        # Simplified implementation
        evaluation = {
            "relevant_precedents": ["General legal principles apply"],
            "strength_of_case": "moderate",
            "recommendations": [
                "Consult legal expert for jurisdiction-specific advice"
            ],
            "confidence": 0.6,
        }
        return evaluation

    async def _calculate_roi(
        self,
        initial_investment: float,
        expected_returns: float,
        time_period_years: float,
        risk_adjustment: float = 1.0,
    ) -> dict[str, Any]:
        """Calculate ROI with projections."""
        total_return = expected_returns - initial_investment
        roi_percentage = (total_return / initial_investment) * 100
        annualized_roi = roi_percentage / time_period_years
        risk_adjusted_roi = annualized_roi * risk_adjustment

        return {
            "total_investment": initial_investment,
            "total_returns": expected_returns,
            "net_profit": total_return,
            "roi_percentage": round(roi_percentage, 2),
            "annualized_roi": round(annualized_roi, 2),
            "risk_adjusted_roi": round(risk_adjusted_roi, 2),
            "payback_period_years": round(
                initial_investment / (total_return / time_period_years), 2
            ),
            "confidence": 0.9,
        }

    async def _evaluate_fair_price(
        self,
        item_description: str,
        market_rates: dict[str, Any] = None,
        complexity_factors: list[str] = None,
    ) -> dict[str, Any]:
        """Evaluate fair market price."""
        # Simplified market analysis
        base_price = 100.0  # Placeholder
        complexity_multiplier = 1.0 + (len(complexity_factors or []) * 0.1)

        fair_price = base_price * complexity_multiplier

        return {
            "item_description": item_description,
            "estimated_fair_price": round(fair_price, 2),
            "price_range": {
                "low": round(fair_price * 0.8, 2),
                "high": round(fair_price * 1.2, 2),
            },
            "market_factors_considered": complexity_factors or ["standard"],
            "confidence": 0.75,
            "recommendations": ["Consider market research for precise pricing"],
        }

    async def _calculate_work_value(
        self,
        hours_required: float,
        skill_level: str,
        market_rate_per_hour: float = None,
        complexity_multiplier: float = 1.0,
    ) -> dict[str, Any]:
        """Calculate fair value for work."""
        # Default market rates by skill level
        default_rates = {
            "junior": 25.0,
            "intermediate": 50.0,
            "senior": 100.0,
            "expert": 150.0,
        }

        hourly_rate = market_rate_per_hour or default_rates.get(
            skill_level.lower(), 50.0
        )
        adjusted_rate = hourly_rate * complexity_multiplier
        total_value = hours_required * adjusted_rate

        return {
            "hours_required": hours_required,
            "skill_level": skill_level,
            "hourly_rate": round(hourly_rate, 2),
            "complexity_multiplier": complexity_multiplier,
            "adjusted_hourly_rate": round(adjusted_rate, 2),
            "total_estimated_value": round(total_value, 2),
            "value_breakdown": {
                "labor_cost": round(total_value * 0.7, 2),
                "overhead": round(total_value * 0.2, 2),
                "profit_margin": round(total_value * 0.1, 2),
            },
            "confidence": 0.8,
            "market_comparison": f"Competitive with {skill_level} rates in industry",
        }


class ProfessionalResponseFormatter:
    """Format responses in professional structure."""

    def parse_and_structure(
        self, raw_response: str, context: DecisionContext, tool_results: dict[str, Any]
    ) -> ProfessionalResponse:
        """Parse AI response and structure it professionally."""

        response = ProfessionalResponse(
            domain=context.domain,
            confidence_score=0.8,
            recommendations=[],
            risks_assessed=[],
            next_steps=[],
        )

        # Extract sections from response (simplified parsing)
        lines = raw_response.split("\n")

        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect sections
            if line.upper().startswith("RECOMMENDATION"):
                current_section = "recommendations"
            elif line.upper().startswith("RISK"):
                current_section = "risks"
            elif line.upper().startswith("NEXT STEP"):
                current_section = "next_steps"
            elif current_section and line.startswith("-"):
                content = line[1:].strip()
                if current_section == "recommendations":
                    response.recommendations.append(content)
                elif current_section == "risks":
                    response.risks_assessed.append(content)
                elif current_section == "next_steps":
                    response.next_steps.append(content)

        # Add domain-specific disclaimers
        if context.domain == DecisionDomain.LEGAL:
            response.legal_disclaimers = [
                "This is not legal advice. Consult with a qualified attorney.",
                "Laws vary by jurisdiction and change over time.",
            ]
        elif context.domain == DecisionDomain.FINANCIAL:
            response.legal_disclaimers = [
                "This is not financial advice. Past performance does not guarantee future results.",
                "Consider consulting a licensed financial advisor.",
            ]

        response.formatted_response = self._format_final_response(
            response, context, tool_results
        )
        return response

    def _format_final_response(
        self,
        response: ProfessionalResponse,
        context: DecisionContext,
        tool_results: dict[str, Any],
    ) -> str:
        """Format the final professional response."""
        formatted = f"""# {context.domain.value.title()} Analysis Report

## Executive Summary
Confidence Score: {response.confidence_score * 100:.1f}%

## Key Recommendations
{chr(10).join(f"• {rec}" for rec in response.recommendations)}

## Risk Assessment
{chr(10).join(f"• {risk}" for risk in response.risks_assessed)}

## Next Steps
{chr(10).join(f"• {step}" for step in response.next_steps)}

## Important Disclaimers
{chr(10).join(f"• {disc}" for disc in response.legal_disclaimers)}

---
*Analysis generated using advanced AI decision support tools*
*Domain: {context.domain.value} | Complexity: {context.complexity} | Urgency: {context.urgency}*"""

        return formatted


# Factory function
def create_advanced_assistant(api_key: str | None = None) -> AdvancedEchoesAssistant:
    """Create an advanced Echoes assistant instance."""
    return AdvancedEchoesAssistant(api_key=api_key)


# Demo and testing
async def demo_advanced_assistant():
    """Demonstrate the advanced assistant capabilities."""
    print("🚀 Advanced Echoes Assistant V3 Demo")
    print("=" * 50)

    # Initialize assistant
    assistant = create_advanced_assistant()

    # Add some domain knowledge
    legal_kb = assistant.knowledge_bases[DecisionDomain.LEGAL]
    legal_kb.add_documents(
        [
            "Contract law requires clear terms and mutual agreement between parties.",
            "Due diligence is essential before signing any legal agreement.",
            "Intellectual property rights must be clearly defined in contracts.",
        ]
    )

    financial_kb = assistant.knowledge_bases[DecisionDomain.FINANCIAL]
    financial_kb.add_documents(
        [
            "Return on investment (ROI) measures the efficiency of an investment.",
            "Fair market value considers comparable transactions in the marketplace.",
            "Risk-adjusted returns account for the volatility of investments.",
        ]
    )

    # Test queries
    test_queries = [
        "What's a fair price to charge for 20 hours of senior Python development work?",
        "Should I invest $50,000 in this startup with expected $200,000 return in 3 years?",
        "What are the main risks in this software development contract?",
    ]

    for query in test_queries:
        print(f"\\n❓ Query: {query}")
        response = await assistant.process_query(query)
        print(f"📋 Response Preview: {response.formatted_response[:300]}...")

    print("\\n✅ Advanced Assistant Demo Complete!")


if __name__ == "__main__":
    asyncio.run(demo_advanced_assistant())
