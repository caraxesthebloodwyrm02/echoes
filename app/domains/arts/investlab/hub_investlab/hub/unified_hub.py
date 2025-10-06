#!/usr/bin/env python3
"""
UnifiedHub - Seamless Interactive Research Ecosystem
Connects all modules, enables data exchange, and provides guided workflows
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
import logging

# Import all system components
from highway import get_highway
from highway.router import get_highway_router
from highway.monitor import get_highway_monitor
from highway.development_bridge import get_development_bridge
from researchlab import get_research_lab
from research.advanced_research import get_advanced_research
from entertainment.nudges.music_nudges import get_music_nudges

logger = logging.getLogger(__name__)

@dataclass
class UnifiedSession:
    """Represents an active user session in UnifiedHub"""
    session_id: str = field(default_factory=lambda: f"uh_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    user_id: str = "default_user"
    current_workflow: Optional[str] = None
    active_modules: List[str] = field(default_factory=list)
    data_exchange_log: List[Dict[str, Any]] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class InteractiveWorkflow:
    """Represents an interactive guided workflow"""
    name: str
    description: str
    steps: List[Dict[str, Any]]
    current_step: int = 0
    context: Dict[str, Any] = field(default_factory=dict)
    completed: bool = False

class UnifiedHub:
    """
    UnifiedHub - The central nervous system of the research ecosystem
    Provides seamless connectivity, data exchange, and interactive workflows
    """

    def __init__(self):
        # Core system components
        self.highway = get_highway()
        self.router = get_highway_router()
        self.monitor = get_highway_monitor()
        self.dev_bridge = get_development_bridge()
        self.research_lab = get_research_lab()
        self.advanced_research = get_advanced_research()
        self.music_nudges = get_music_nudges()

        # Session management
        self.active_sessions: Dict[str, UnifiedSession] = {}

        # Workflow templates
        self.workflow_templates = self._initialize_workflows()

        # Integration mappings
        self.module_connections = self._initialize_connections()

        # Data exchange protocols
        self.exchange_protocols = self._initialize_protocols()

        logger.info("UnifiedHub initialized - All systems connected")

    def _initialize_workflows(self) -> Dict[str, InteractiveWorkflow]:
        """Initialize interactive workflow templates"""
        return {
            'quickstart': InteractiveWorkflow(
                name='QuickStart Research Journey',
                description='Guided introduction to the research ecosystem',
                steps=[
                    {
                        'title': 'Welcome to ResearchLab',
                        'description': 'Get familiar with the system capabilities',
                        'action': 'welcome',
                        'duration_estimate': 2
                    },
                    {
                        'title': 'Choose Research Domain',
                        'description': 'Select your area of interest',
                        'action': 'domain_selection',
                        'options': ['artificial_intelligence', 'data_science', 'computational_research'],
                        'duration_estimate': 3
                    },
                    {
                        'title': 'AI-Powered Research',
                        'description': 'Experience AI-driven hypothesis generation',
                        'action': 'ai_research_demo',
                        'duration_estimate': 5
                    },
                    {
                        'title': 'Collaborative Environment',
                        'description': 'Explore multi-user research capabilities',
                        'action': 'collaboration_demo',
                        'duration_estimate': 4
                    },
                    {
                        'title': 'Data Analysis Showcase',
                        'description': 'See automated data analysis in action',
                        'action': 'data_analysis_demo',
                        'duration_estimate': 6
                    },
                    {
                        'title': 'Complete Research Workflow',
                        'description': 'Execute a complete research project',
                        'action': 'full_workflow_demo',
                        'duration_estimate': 10
                    }
                ]
            ),

            'research_project': InteractiveWorkflow(
                name='Complete Research Project',
                description='End-to-end research project workflow',
                steps=[
                    {
                        'title': 'Project Initialization',
                        'description': 'Set up your research project',
                        'action': 'project_init',
                        'duration_estimate': 5
                    },
                    {
                        'title': 'Hypothesis Generation',
                        'description': 'AI-powered hypothesis creation',
                        'action': 'hypothesis_generation',
                        'duration_estimate': 8
                    },
                    {
                        'title': 'Experiment Design',
                        'description': 'Design and plan experiments',
                        'action': 'experiment_design',
                        'duration_estimate': 10
                    },
                    {
                        'title': 'Data Collection',
                        'description': 'Gather and prepare research data',
                        'action': 'data_collection',
                        'duration_estimate': 15
                    },
                    {
                        'title': 'Analysis & Insights',
                        'description': 'Analyze data and extract insights',
                        'action': 'data_analysis',
                        'duration_estimate': 12
                    },
                    {
                        'title': 'Results Validation',
                        'description': 'Validate and peer review results',
                        'action': 'results_validation',
                        'duration_estimate': 8
                    },
                    {
                        'title': 'Publication Preparation',
                        'description': 'Prepare research for publication',
                        'action': 'publication_prep',
                        'duration_estimate': 10
                    }
                ]
            ),

            'collaboration_session': InteractiveWorkflow(
                name='Research Collaboration',
                description='Multi-user research collaboration session',
                steps=[
                    {
                        'title': 'Session Setup',
                        'description': 'Configure collaboration session',
                        'action': 'session_setup',
                        'duration_estimate': 3
                    },
                    {
                        'title': 'Invite Collaborators',
                        'description': 'Add team members to the session',
                        'action': 'invite_collaborators',
                        'duration_estimate': 2
                    },
                    {
                        'title': 'Share Research Context',
                        'description': 'Share project background and goals',
                        'action': 'share_context',
                        'duration_estimate': 5
                    },
                    {
                        'title': 'Collaborative Ideation',
                        'description': 'Brainstorm and generate ideas together',
                        'action': 'collaborative_ideation',
                        'duration_estimate': 15
                    },
                    {
                        'title': 'Peer Review',
                        'description': 'Review and provide feedback',
                        'action': 'peer_review',
                        'duration_estimate': 10
                    },
                    {
                        'title': 'Session Summary',
                        'description': 'Summarize collaboration outcomes',
                        'action': 'session_summary',
                        'duration_estimate': 5
                    }
                ]
            )
        }

    def _initialize_connections(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize module connection mappings"""
        return {
            'research': {
                'inputs': ['brainstorming_ideas', 'hypothesis_requests', 'experiment_data'],
                'outputs': ['hypotheses', 'experiment_designs', 'analysis_results'],
                'connections': ['highway', 'research_lab', 'advanced_research']
            },
            'entertainment': {
                'inputs': ['mood_data', 'context_requests', 'music_preferences'],
                'outputs': ['music_recommendations', 'mood_analysis', 'nudges'],
                'connections': ['highway', 'music_nudges', 'all_modules']
            },
            'insights': {
                'inputs': ['raw_data', 'analysis_requests', 'visualization_needs'],
                'outputs': ['insights', 'dashboards', 'recommendations'],
                'connections': ['highway', 'data_platform', 'visualization']
            },
            'finance': {
                'inputs': ['financial_data', 'budget_requests', 'market_analysis'],
                'outputs': ['financial_insights', 'budget_reports', 'investment_advice'],
                'connections': ['highway', 'yahoo_finance', 'commerce_integration']
            },
            'content': {
                'inputs': ['research_outputs', 'creation_requests', 'publication_needs'],
                'outputs': ['generated_content', 'publications', 'media_assets'],
                'connections': ['highway', 'ai_generation', 'media_pipeline']
            },
            'media': {
                'inputs': ['content_to_publish', 'platform_requests', 'audience_data'],
                'outputs': ['published_content', 'engagement_metrics', 'monetization_reports'],
                'connections': ['highway', 'youtube_api', 'instagram_api', 'discord_api']
            },
            'brainstorming': {
                'inputs': ['idea_prompts', 'collaboration_requests', 'discussion_topics'],
                'outputs': ['generated_ideas', 'discussion_summaries', 'action_items'],
                'connections': ['highway', 'ai_collaboration', 'research_lab']
            }
        }

    def _initialize_protocols(self) -> Dict[str, Callable]:
        """Initialize data exchange protocols"""
        return {
            'research_data': self._exchange_research_data,
            'collaboration_update': self._exchange_collaboration_data,
            'analysis_request': self._exchange_analysis_data,
            'publication_content': self._exchange_publication_data,
            'music_nudge': self._exchange_music_data,
            'system_status': self._exchange_system_data
        }

    def create_session(self, user_id: str = "default_user") -> UnifiedSession:
        """Create a new interactive session"""
        session = UnifiedSession(user_id=user_id)

        # Initialize with welcome workflow
        session.current_workflow = 'quickstart'

        # Play welcome music nudge
        nudge_result = self.music_nudges.play_nudge('direction')
        session.data_exchange_log.append({
            'type': 'music_nudge',
            'action': 'welcome',
            'result': nudge_result,
            'timestamp': datetime.now().isoformat()
        })

        self.active_sessions[session.session_id] = session

        logger.info(f"UnifiedHub session created: {session.session_id} for user: {user_id}")

        return session

    def start_workflow(self, session_id: str, workflow_name: str) -> Dict[str, Any]:
        """Start an interactive workflow"""
        if session_id not in self.active_sessions:
            return {'error': 'Session not found'}

        session = self.active_sessions[session_id]

        if workflow_name not in self.workflow_templates:
            return {'error': 'Workflow not found'}

        workflow = self.workflow_templates[workflow_name]
        session.current_workflow = workflow_name

        # Initialize workflow context
        workflow.current_step = 0
        workflow.completed = False

        # Execute first step
        first_step_result = self._execute_workflow_step(session, workflow, 0)

        return {
            'session_id': session_id,
            'workflow': workflow_name,
            'current_step': 0,
            'step_result': first_step_result,
            'total_steps': len(workflow.steps)
        }

    def advance_workflow(self, session_id: str, user_input: Dict[str, Any] = None) -> Dict[str, Any]:
        """Advance to the next step in the current workflow"""
        if session_id not in self.active_sessions:
            return {'error': 'Session not found'}

        session = self.active_sessions[session_id]

        if not session.current_workflow:
            return {'error': 'No active workflow'}

        workflow = self.workflow_templates[session.current_workflow]

        if workflow.completed:
            return {'error': 'Workflow already completed'}

        current_step = workflow.current_step

        # Execute current step with user input
        if user_input:
            workflow.context.update(user_input)

        step_result = self._execute_workflow_step(session, workflow, current_step)

        # Advance to next step
        if current_step < len(workflow.steps) - 1:
            workflow.current_step = current_step + 1
        else:
            workflow.completed = True
            session.achievements.append(f"Completed {workflow.name}")

            # Play celebration music nudge
            nudge_result = self.music_nudges.play_nudge('celebration')
            session.data_exchange_log.append({
                'type': 'achievement',
                'action': 'workflow_completed',
                'workflow': workflow.name,
                'nudge': nudge_result,
                'timestamp': datetime.now().isoformat()
            })

        return {
            'session_id': session_id,
            'workflow': session.current_workflow,
            'current_step': workflow.current_step,
            'step_result': step_result,
            'completed': workflow.completed,
            'progress': f"{workflow.current_step + 1}/{len(workflow.steps)}"
        }

    def _execute_workflow_step(self, session: UnifiedSession, workflow: InteractiveWorkflow, step_index: int) -> Dict[str, Any]:
        """Execute a specific workflow step"""
        step = workflow.steps[step_index]
        action = step['action']

        if action == 'welcome':
            return self._welcome_step(session)
        elif action == 'domain_selection':
            return self._domain_selection_step(session, step)
        elif action == 'ai_research_demo':
            return self._ai_research_demo_step(session)
        elif action == 'collaboration_demo':
            return self._collaboration_demo_step(session)
        elif action == 'data_analysis_demo':
            return self._data_analysis_demo_step(session)
        elif action == 'full_workflow_demo':
            return self._full_workflow_demo_step(session)
        elif action == 'project_init':
            return self._project_init_step(session, workflow)
        elif action == 'hypothesis_generation':
            return self._hypothesis_generation_step(session, workflow)
        elif action == 'experiment_design':
            return self._experiment_design_step(session, workflow)
        elif action == 'data_collection':
            return self._data_collection_step(session, workflow)
        elif action == 'data_analysis':
            return self._data_analysis_step(session, workflow)
        elif action == 'results_validation':
            return self._results_validation_step(session, workflow)
        elif action == 'publication_prep':
            return self._publication_prep_step(session, workflow)
        else:
            return {'error': f'Unknown action: {action}'}

    def _welcome_step(self, session: UnifiedSession) -> Dict[str, Any]:
        """Execute welcome step"""
        return {
            'message': 'Welcome to ResearchLab! 🎉',
            'description': 'You are now connected to a state-of-the-art research ecosystem with AI capabilities, collaborative tools, and intelligent automation.',
            'capabilities': [
                '🤖 AI-powered research assistance',
                '👥 Multi-user collaboration',
                '📊 Automated data analysis',
                '🎵 Contextual music guidance',
                '🔄 Intelligent workflow automation'
            ],
            'next_action': 'Choose your research domain to begin'
        }

    def _domain_selection_step(self, session: UnifiedSession, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute domain selection step"""
        domains = step.get('options', [])
        domain_info = {}

        for domain in domains:
            if domain in self.research_lab.research_domains:
                info = self.research_lab.research_domains[domain]
                domain_info[domain] = {
                    'capabilities': info['capabilities'][:3],  # Show first 3
                    'tools': info['tools'][:2]  # Show first 2
                }

        return {
            'message': 'Choose Your Research Domain',
            'description': 'Select the area that interests you most to customize your experience.',
            'domains': domain_info,
            'selection_required': True
        }

    def _ai_research_demo_step(self, session: UnifiedSession) -> Dict[str, Any]:
        """Execute AI research demo step"""
        # Generate a sample hypothesis
        hypothesis = self.advanced_research.ai_capabilities.generate_hypothesis(
            "artificial intelligence in healthcare"
        )

        # Route through highway for additional processing
        packet = {
            'type': 'ai_demo',
            'hypothesis': hypothesis.title,
            'session_id': session.session_id,
            'user_id': session.user_id
        }

        packet_id = self.highway.send_to_research(packet, "unified_hub")

        return {
            'message': 'AI Research Demo ✨',
            'description': 'Experience AI-powered hypothesis generation and research assistance.',
            'hypothesis': {
                'title': hypothesis.title,
                'description': hypothesis.description,
                'variables': hypothesis.variables,
                'methodology': hypothesis.methodology
            },
            'packet_routed': packet_id,
            'ai_capabilities': [
                'Automated hypothesis generation',
                'Research methodology suggestions',
                'Literature analysis assistance',
                'Experiment design optimization'
            ]
        }

    def _collaboration_demo_step(self, session: UnifiedSession) -> Dict[str, Any]:
        """Execute collaboration demo step"""
        # Start a demo collaboration session
        session_id = self.advanced_research.collaboration.start_collaborative_session(
            f"demo_session_{session.session_id}",
            ["demo_researcher_1", "demo_researcher_2", session.user_id]
        )

        return {
            'message': 'Collaboration Demo 👥',
            'description': 'Experience multi-user research collaboration with real-time updates.',
            'session_started': session_id,
            'collaborators': ["demo_researcher_1", "demo_researcher_2", session.user_id],
            'features': [
                'Real-time idea sharing',
                'Peer review integration',
                'Progress synchronization',
                'Knowledge base access'
            ]
        }

    def _data_analysis_demo_step(self, session: UnifiedSession) -> Dict[str, Any]:
        """Execute data analysis demo step"""
        # Create sample data for analysis
        sample_data = {
            'records': [
                {'feature1': 1.2, 'feature2': 3.4, 'target': 1},
                {'feature1': 2.1, 'feature2': 4.2, 'target': 0},
                {'feature1': 3.3, 'feature2': 2.1, 'target': 1}
            ],
            'features': ['feature1', 'feature2'],
            'metadata': {'source': 'demo', 'quality_score': 0.95}
        }

        analysis = self.advanced_research.data_platform.analyze_dataset(
            sample_data, {'analysis_type': 'exploratory'}
        )

        return {
            'message': 'Data Analysis Demo 📊',
            'description': 'See automated data analysis and statistical insights in action.',
            'analysis_results': {
                'data_quality': analysis.get('data_quality_assessment', {}),
                'insights': analysis.get('insights', [])[:3],  # Show first 3
                'recommendations': analysis.get('recommendations', [])[:2]
            },
            'capabilities': [
                'Automated statistical analysis',
                'Machine learning model evaluation',
                'Data quality assessment',
                'Visualization recommendations'
            ]
        }

    def _full_workflow_demo_step(self, session: UnifiedSession) -> Dict[str, Any]:
        """Execute full workflow demo step"""
        # Create a mini research project
        project = self.research_lab.initiate_research_project(
            title=f"Demo Research: {session.user_id}",
            description="Demonstration of complete research workflow",
            domain="artificial_intelligence",
            collaborators=[session.user_id, "demo_collaborator"]
        )

        # Conduct research
        results = self.research_lab.conduct_research_workflow(
            project['project_id'],
            "Demonstrate AI capabilities in automated research workflows"
        )

        return {
            'message': 'Complete Research Workflow Demo 🚀',
            'description': 'Experience the full research lifecycle from ideation to insights.',
            'project': {
                'id': project['project_id'],
                'title': project['title'],
                'workflow_status': results.get('workflow_progress', 'completed')
            },
            'results_summary': {
                'hypothesis_generated': bool(results.get('research_results', {}).get('hypothesis')),
                'experiment_designed': bool(results.get('research_results', {}).get('experiment')),
                'analysis_performed': bool(results.get('research_results', {}).get('analysis')),
                'insights_extracted': len(results.get('publication_insights', {}).get('key_findings', []))
            },
            'workflow_capabilities': [
                'AI-powered hypothesis generation',
                'Automated experiment design',
                'Real-time data analysis',
                'Collaborative validation',
                'Publication-ready insights'
            ]
        }

    def _project_init_step(self, session: UnifiedSession, workflow: InteractiveWorkflow) -> Dict[str, Any]:
        """Execute project initialization step"""
        # Use context from previous steps
        domain = workflow.context.get('selected_domain', 'artificial_intelligence')
        title = workflow.context.get('project_title', f"Research Project by {session.user_id}")
        description = workflow.context.get('project_description', 'Comprehensive research investigation')

        project = self.research_lab.initiate_research_project(
            title=title,
            description=description,
            domain=domain,
            collaborators=[session.user_id]
        )

        # Store project ID in workflow context
        workflow.context['project_id'] = project['project_id']

        return {
            'message': 'Research Project Initialized 📋',
            'project': {
                'id': project['project_id'],
                'title': title,
                'domain': domain,
                'collaborators': project.get('collaborators', [])
            },
            'next_steps': [
                'Define research objectives',
                'Gather background information',
                'Identify key research questions'
            ]
        }

    def _hypothesis_generation_step(self, session: UnifiedSession, workflow: InteractiveWorkflow) -> Dict[str, Any]:
        """Execute hypothesis generation step"""
        project_id = workflow.context.get('project_id')
        research_query = workflow.context.get('research_query', 'AI applications in modern research')

        if project_id:
            results = self.research_lab.conduct_research_workflow(project_id, research_query)

            # Extract hypothesis from results
            hypothesis = results.get('research_results', {}).get('hypothesis', {})

            return {
                'message': 'AI Hypothesis Generated 🤖',
                'hypothesis': {
                    'title': hypothesis.get('title', 'Generated hypothesis'),
                    'description': hypothesis.get('description', 'AI-generated research hypothesis'),
                    'variables': hypothesis.get('variables', []),
                    'methodology': hypothesis.get('methodology', 'AI-assisted approach')
                },
                'ai_insights': results.get('publication_insights', {}).get('key_findings', [])[:3]
            }
        else:
            return {'error': 'No active project found'}

    def _experiment_design_step(self, session: UnifiedSession, workflow: InteractiveWorkflow) -> Dict[str, Any]:
        """Execute experiment design step"""
        # Implementation for experiment design workflow
        return {
            'message': 'Experiment Design Phase 🧪',
            'description': 'Design and plan your research experiments',
            'design_elements': {
                'variables': ['independent', 'dependent', 'control'],
                'methodology': 'controlled_experiment',
                'sample_size': 'determined_by_power_analysis',
                'timeline': '4-6_weeks'
            }
        }

    def _data_collection_step(self, session: UnifiedSession, workflow: InteractiveWorkflow) -> Dict[str, Any]:
        """Execute data collection step"""
        return {
            'message': 'Data Collection Phase 📥',
            'description': 'Gather and prepare research data',
            'data_sources': ['primary_collection', 'existing_datasets', 'simulations'],
            'quality_checks': ['completeness', 'accuracy', 'consistency']
        }

    def _data_analysis_step(self, session: UnifiedSession, workflow: InteractiveWorkflow) -> Dict[str, Any]:
        """Execute data analysis step"""
        return {
            'message': 'Data Analysis Phase 📊',
            'description': 'Analyze data and extract meaningful insights',
            'analysis_types': ['statistical', 'machine_learning', 'qualitative'],
            'outputs': ['insights', 'visualizations', 'recommendations']
        }

    def _results_validation_step(self, session: UnifiedSession, workflow: InteractiveWorkflow) -> Dict[str, Any]:
        """Execute results validation step"""
        return {
            'message': 'Results Validation Phase ✅',
            'description': 'Validate and peer review research results',
            'validation_methods': ['statistical_significance', 'peer_review', 'reproducibility_checks'],
            'quality_metrics': ['rigor', 'novelty', 'impact', 'feasibility']
        }

    def _publication_prep_step(self, session: UnifiedSession, workflow: InteractiveWorkflow) -> Dict[str, Any]:
        """Execute publication preparation step"""
        return {
            'message': 'Publication Preparation Phase 📝',
            'description': 'Prepare research for publication and dissemination',
            'publication_types': ['journal_article', 'conference_paper', 'technical_report'],
            'preparation_steps': ['manuscript_writing', 'figure_preparation', 'review_process']
        }

    def exchange_data(self, source_module: str, target_module: str,
                     data_type: str, payload: Dict[str, Any]) -> str:
        """Exchange data between modules seamlessly"""
        if data_type in self.exchange_protocols:
            return self.exchange_protocols[data_type](source_module, target_module, payload)
        else:
            # Use highway routing as fallback
            packet = {
                'type': data_type,
                'source': source_module,
                'target': target_module,
                'payload': payload,
                'exchange_timestamp': datetime.now().isoformat()
            }

            packet_id = self.router.route_research_to_dev(payload)  # Generic routing
            return packet_id

    def _exchange_research_data(self, source: str, target: str, payload: Dict[str, Any]) -> str:
        """Exchange research data between modules"""
        packet = {
            'type': 'research_data_exchange',
            'source': source,
            'target': target,
            'data': payload,
            'timestamp': datetime.now().isoformat()
        }

        if target == 'insights':
            return self.highway.send_to_insights(packet, source)
        elif target == 'content':
            return self.highway.send_to_content(packet, source)
        else:
            return self.highway.send_to_research(packet, source)

    def _exchange_collaboration_data(self, source: str, target: str, payload: Dict[str, Any]) -> str:
        """Exchange collaboration data"""
        packet = {
            'type': 'collaboration_exchange',
            'source': source,
            'target': target,
            'collaboration_data': payload,
            'timestamp': datetime.now().isoformat()
        }

        return self.highway.send_to_brainstorming(packet, source)

    def _exchange_analysis_data(self, source: str, target: str, payload: Dict[str, Any]) -> str:
        """Exchange analysis data"""
        packet = {
            'type': 'analysis_exchange',
            'source': source,
            'target': target,
            'analysis_data': payload,
            'timestamp': datetime.now().isoformat()
        }

        return self.highway.send_to_insights(packet, source)

    def _exchange_publication_data(self, source: str, target: str, payload: Dict[str, Any]) -> str:
        """Exchange publication data"""
        packet = {
            'type': 'publication_exchange',
            'source': source,
            'target': target,
            'publication_data': payload,
            'timestamp': datetime.now().isoformat()
        }

        return self.highway.send_to_media(packet, source)

    def _exchange_music_data(self, source: str, target: str, payload: Dict[str, Any]) -> str:
        """Exchange music data"""
        # Music nudges work across all modules
        nudge_type = payload.get('nudge_type', 'motivation')
        result = self.music_nudges.play_nudge(nudge_type)

        return f"music_nudge_{nudge_type}_{datetime.now().strftime('%H%M%S')}"

    def _exchange_system_data(self, source: str, target: str, payload: Dict[str, Any]) -> str:
        """Exchange system status data"""
        status = self.get_unified_status()
        packet = {
            'type': 'system_status_exchange',
            'source': source,
            'target': target,
            'system_status': status,
            'timestamp': datetime.now().isoformat()
        }

        return self.highway.send_to_insights(packet, source)

    def get_unified_status(self) -> Dict[str, Any]:
        """Get comprehensive unified system status"""
        return {
            'unified_hub': {
                'active_sessions': len(self.active_sessions),
                'available_workflows': len(self.workflow_templates),
                'module_connections': len(self.module_connections)
            },
            'highway_system': self.highway.get_highway_status(),
            'research_lab': self.research_lab.get_lab_status(),
            'advanced_research': self.advanced_research.get_research_status(),
            'system_health': 'optimal',
            'timestamp': datetime.now().isoformat()
        }

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get status of a specific session"""
        if session_id not in self.active_sessions:
            return {'error': 'Session not found'}

        session = self.active_sessions[session_id]

        workflow_status = {}
        if session.current_workflow and session.current_workflow in self.workflow_templates:
            workflow = self.workflow_templates[session.current_workflow]
            workflow_status = {
                'name': workflow.name,
                'current_step': workflow.current_step,
                'total_steps': len(workflow.steps),
                'completed': workflow.completed,
                'progress': f"{workflow.current_step + 1}/{len(workflow.steps)}"
            }

        return {
            'session_id': session_id,
            'user_id': session.user_id,
            'active_modules': session.active_modules,
            'current_workflow': workflow_status,
            'achievements': session.achievements,
            'data_exchanges': len(session.data_exchange_log),
            'created_at': session.created_at.isoformat()
        }

# Global UnifiedHub instance
unified_hub = UnifiedHub()

def get_unified_hub() -> UnifiedHub:
    """Get the global UnifiedHub instance"""
    return unified_hub

# Quick access functions
def create_session(user_id: str = "default_user") -> UnifiedSession:
    """Create a new unified session"""
    return unified_hub.create_session(user_id)

def start_workflow(session_id: str, workflow: str) -> Dict[str, Any]:
    """Start an interactive workflow"""
    return unified_hub.start_workflow(session_id, workflow)

def advance_workflow(session_id: str, user_input: Dict[str, Any] = None) -> Dict[str, Any]:
    """Advance workflow to next step"""
    return unified_hub.advance_workflow(session_id, user_input)

def exchange_data(source: str, target: str, data_type: str, payload: Dict[str, Any]) -> str:
    """Exchange data between modules"""
    return unified_hub.exchange_data(source, target, data_type, payload)

def get_unified_status() -> Dict[str, Any]:
    """Get unified system status"""
    return unified_hub.get_unified_status()

def get_session_status(session_id: str) -> Dict[str, Any]:
    """Get session status"""
    return unified_hub.get_session_status(session_id)
