"""
Agent Archive - Version control system for voice agents.

This module provides the AgentArchive class for storing, retrieving,
and managing different versions of the voice agent throughout evolution.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from .models import AgentVersion, Conversation, Evolution, get_session


class AgentArchive:
    """
    Manages the archive of agent versions and their evolution history.

    This class acts as a version control system for AI agents, tracking:
    - Different prompt versions
    - Performance metrics
    - Parent-child relationships (evolution lineage)
    - Best performers
    """

    def __init__(self, db_url: str = "sqlite:///data/agents.db"):
        """
        Initialize the agent archive.

        Args:
            db_url: Database connection string
        """
        self.db_url = db_url
        self.session = get_session(db_url)

    def save_agent(
        self,
        prompt: str,
        config: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None,
        generation: int = 0,
        mutation_strategy: Optional[str] = None,
        change_rationale: Optional[str] = None
    ) -> str:
        """
        Save a new agent version to the archive.

        Args:
            prompt: The agent's system prompt
            config: Additional configuration (optional)
            parent_id: Version ID of the parent agent (None for baseline)
            generation: Generation number in evolution
            mutation_strategy: How this variant was created (e.g., "tone_adjustment")
            change_rationale: Explanation of why changes were made

        Returns:
            version_id: Unique identifier for this agent version

        Example:
            >>> archive = AgentArchive()
            >>> version_id = archive.save_agent(
            ...     prompt="You are a helpful debt collection agent...",
            ...     parent_id=None,  # This is the baseline
            ...     generation=0
            ... )
            >>> print(version_id)
            'v0-abc123'
        """
        # Generate unique version ID
        version_id = self._generate_version_id(generation)

        # Create agent version object
        agent = AgentVersion(
            version_id=version_id,
            prompt=prompt,
            config=config or {},
            parent_id=parent_id,
            generation=generation,
            mutation_strategy=mutation_strategy,
            change_rationale=change_rationale,
            is_active=True,
            created_at=datetime.utcnow()
        )

        # Save to database
        self.session.add(agent)
        self.session.commit()

        print(f"✅ Saved agent version: {version_id} (generation {generation})")
        return version_id

    def get_agent(self, version_id: str) -> Optional[AgentVersion]:
        """
        Retrieve a specific agent version by ID.

        Args:
            version_id: Unique identifier of the agent

        Returns:
            AgentVersion object or None if not found

        Example:
            >>> archive = AgentArchive()
            >>> agent = archive.get_agent('v0-abc123')
            >>> print(agent.prompt)
        """
        agent = self.session.query(AgentVersion).filter_by(version_id=version_id).first()

        if not agent:
            print(f"⚠️  Agent version '{version_id}' not found")
            return None

        return agent

    def update_scores(
        self,
        version_id: str,
        goal_completion: float,
        conversational_quality: float,
        compliance: float,
        total_conversations: int = 0,
        successful_conversations: int = 0,
        failed_conversations: int = 0
    ) -> bool:
        """
        Update performance scores for an agent version.

        Args:
            version_id: Agent version to update
            goal_completion: Score 0-100
            conversational_quality: Score 0-100
            compliance: Score 0-100
            total_conversations: Total number of conversations
            successful_conversations: Number of successful conversations
            failed_conversations: Number of failed conversations

        Returns:
            True if updated successfully, False otherwise

        Example:
            >>> archive.update_scores('v0-abc123', 85.0, 78.0, 95.0)
        """
        agent = self.get_agent(version_id)
        if not agent:
            return False

        # Calculate composite score (weighted average)
        # Default weights: 40% goal, 30% quality, 30% compliance
        composite = (
            goal_completion * 0.4 +
            conversational_quality * 0.3 +
            compliance * 0.3
        )

        # Update scores
        agent.goal_completion_score = goal_completion
        agent.conversational_quality_score = conversational_quality
        agent.compliance_score = compliance
        agent.composite_score = composite
        agent.total_conversations = total_conversations
        agent.successful_conversations = successful_conversations
        agent.failed_conversations = failed_conversations
        agent.evaluated_at = datetime.utcnow()

        self.session.commit()

        print(f"✅ Updated scores for {version_id}: composite={composite:.2f}")
        return True

    def get_best_agent(
        self,
        metric: str = "composite_score",
        generation: Optional[int] = None
    ) -> Optional[AgentVersion]:
        """
        Retrieve the best performing agent.

        Args:
            metric: Which metric to use for "best"
                   (composite_score, goal_completion_score, etc.)
            generation: Optionally filter by generation

        Returns:
            Best performing AgentVersion

        Example:
            >>> archive = AgentArchive()
            >>> best = archive.get_best_agent()
            >>> print(f"Best agent: {best.version_id} with score {best.composite_score}")
        """
        query = self.session.query(AgentVersion)

        if generation is not None:
            query = query.filter_by(generation=generation)

        # Order by the specified metric
        metric_column = getattr(AgentVersion, metric, AgentVersion.composite_score)
        agent = query.order_by(desc(metric_column)).first()

        return agent

    def get_lineage(self, version_id: str) -> List[AgentVersion]:
        """
        Get the evolution lineage (ancestry) of an agent.

        Traces back through parent relationships to show how this agent evolved.

        Args:
            version_id: Agent version to trace

        Returns:
            List of AgentVersions from oldest ancestor to current

        Example:
            >>> archive = AgentArchive()
            >>> lineage = archive.get_lineage('v5-xyz789')
            >>> for agent in lineage:
            ...     print(f"Gen {agent.generation}: {agent.version_id} (score: {agent.composite_score})")
        """
        lineage = []
        current = self.get_agent(version_id)

        while current:
            lineage.insert(0, current)  # Add to front (oldest first)
            if current.parent_id:
                current = self.get_agent(current.parent_id)
            else:
                break

        return lineage

    def list_agents(
        self,
        generation: Optional[int] = None,
        limit: int = 10
    ) -> List[AgentVersion]:
        """
        List agent versions, optionally filtered by generation.

        Args:
            generation: Filter by generation (None for all)
            limit: Maximum number to return

        Returns:
            List of AgentVersions, ordered by composite score

        Example:
            >>> archive = AgentArchive()
            >>> agents = archive.list_agents(generation=5, limit=5)
            >>> for agent in agents:
            ...     print(f"{agent.version_id}: {agent.composite_score:.2f}")
        """
        query = self.session.query(AgentVersion)

        if generation is not None:
            query = query.filter_by(generation=generation)

        agents = query.order_by(desc(AgentVersion.composite_score)).limit(limit).all()
        return agents

    def get_generation_stats(self, generation: int) -> Dict[str, Any]:
        """
        Get statistics for a specific generation.

        Args:
            generation: Generation number

        Returns:
            Dictionary with statistics

        Example:
            >>> stats = archive.get_generation_stats(5)
            >>> print(f"Average score: {stats['avg_score']}")
            >>> print(f"Best agent: {stats['best_agent_id']}")
        """
        agents = self.session.query(AgentVersion).filter_by(generation=generation).all()

        if not agents:
            return {
                'generation': generation,
                'count': 0,
                'avg_score': 0.0,
                'best_score': 0.0,
                'worst_score': 0.0,
                'best_agent_id': None
            }

        scores = [a.composite_score for a in agents]
        best_agent = max(agents, key=lambda a: a.composite_score)

        return {
            'generation': generation,
            'count': len(agents),
            'avg_score': sum(scores) / len(scores),
            'best_score': max(scores),
            'worst_score': min(scores),
            'best_agent_id': best_agent.version_id,
            'agents': [a.version_id for a in agents]
        }

    def mark_as_best(self, version_id: str) -> bool:
        """
        Mark an agent as the current best performer.

        Unmarks all other agents first.

        Args:
            version_id: Agent to mark as best

        Returns:
            True if successful
        """
        # Unmark all agents
        self.session.query(AgentVersion).update({'is_best': False})

        # Mark this one as best
        agent = self.get_agent(version_id)
        if agent:
            agent.is_best = True
            self.session.commit()
            print(f"✅ Marked {version_id} as best agent")
            return True

        return False

    def get_evolution_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the entire evolution process.

        Returns:
            Dictionary with evolution statistics

        Example:
            >>> summary = archive.get_evolution_summary()
            >>> print(f"Total generations: {summary['total_generations']}")
            >>> print(f"Total agents: {summary['total_agents']}")
        """
        agents = self.session.query(AgentVersion).all()

        if not agents:
            return {
                'total_agents': 0,
                'total_generations': 0,
                'best_agent': None,
                'best_score': 0.0
            }

        max_generation = max(a.generation for a in agents)
        best_agent = max(agents, key=lambda a: a.composite_score)

        return {
            'total_agents': len(agents),
            'total_generations': max_generation + 1,
            'best_agent': best_agent.version_id,
            'best_score': best_agent.composite_score,
            'avg_score': sum(a.composite_score for a in agents) / len(agents),
            'total_conversations': sum(a.total_conversations for a in agents)
        }

    def _generate_version_id(self, generation: int) -> str:
        """Generate a unique version ID."""
        short_uuid = str(uuid.uuid4())[:8]
        return f"v{generation}-{short_uuid}"

    def close(self):
        """Close the database session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
