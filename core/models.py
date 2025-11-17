"""
Database models for the Darwin Gödel Machine Voice Agent.

This module defines the SQLAlchemy models for storing agent versions,
conversations, and evaluation results.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import json
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
    JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class AgentVersion(Base):
    """
    Represents a single version of the voice agent.

    Each agent version includes its prompt, configuration, performance scores,
    and lineage information (parent-child relationships for evolution tracking).
    """
    __tablename__ = 'agent_versions'

    # Primary identifiers
    id = Column(Integer, primary_key=True, autoincrement=True)
    version_id = Column(String(50), unique=True, nullable=False, index=True)

    # Core agent data
    prompt = Column(Text, nullable=False)  # The agent's system prompt
    config = Column(JSON, nullable=True)   # Additional configuration as JSON

    # Evolution tracking
    parent_id = Column(String(50), ForeignKey('agent_versions.version_id'), nullable=True)
    generation = Column(Integer, default=0)  # Which generation in evolution

    # Performance metrics
    goal_completion_score = Column(Float, default=0.0)
    conversational_quality_score = Column(Float, default=0.0)
    compliance_score = Column(Float, default=0.0)
    composite_score = Column(Float, default=0.0)  # Overall score

    # Evaluation metadata
    total_conversations = Column(Integer, default=0)
    successful_conversations = Column(Integer, default=0)
    failed_conversations = Column(Integer, default=0)

    # Evolution metadata
    mutation_strategy = Column(String(50), nullable=True)  # How this variant was created
    change_rationale = Column(Text, nullable=True)  # Why these changes were made
    is_active = Column(Boolean, default=True)  # Is this agent currently being used?
    is_best = Column(Boolean, default=False)   # Is this the best performer?

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    evaluated_at = Column(DateTime, nullable=True)

    # Relationships
    parent = relationship('AgentVersion', remote_side=[version_id], backref='children')

    def __repr__(self):
        return f"<AgentVersion(id={self.version_id}, gen={self.generation}, score={self.composite_score:.2f})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent version to dictionary."""
        return {
            'id': self.id,
            'version_id': self.version_id,
            'prompt': self.prompt,
            'config': self.config,
            'parent_id': self.parent_id,
            'generation': self.generation,
            'scores': {
                'goal_completion': self.goal_completion_score,
                'conversational_quality': self.conversational_quality_score,
                'compliance': self.compliance_score,
                'composite': self.composite_score
            },
            'conversations': {
                'total': self.total_conversations,
                'successful': self.successful_conversations,
                'failed': self.failed_conversations
            },
            'metadata': {
                'mutation_strategy': self.mutation_strategy,
                'change_rationale': self.change_rationale,
                'is_active': self.is_active,
                'is_best': self.is_best,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'evaluated_at': self.evaluated_at.isoformat() if self.evaluated_at else None
            }
        }


class Conversation(Base):
    """
    Represents a single conversation between the agent and a persona.

    Stores the full transcript, evaluation scores, and metadata for analysis.
    """
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(50), unique=True, nullable=False, index=True)

    # Links to agent version
    agent_version_id = Column(String(50), ForeignKey('agent_versions.version_id'), nullable=False)

    # Conversation details
    persona_name = Column(String(50), nullable=False)
    transcript = Column(JSON, nullable=False)  # List of turns

    # Outcome
    goal_achieved = Column(Boolean, default=False)
    termination_reason = Column(String(100), nullable=True)

    # Evaluation scores
    goal_completion_score = Column(Float, default=0.0)
    conversational_quality_score = Column(Float, default=0.0)
    compliance_score = Column(Float, default=0.0)
    composite_score = Column(Float, default=0.0)

    # Metadata
    duration_seconds = Column(Float, nullable=True)
    turn_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    agent = relationship('AgentVersion', backref='conversations')

    def __repr__(self):
        return f"<Conversation(id={self.conversation_id}, persona={self.persona_name}, score={self.composite_score:.2f})>"


class Evolution(Base):
    """
    Tracks evolution generations and their outcomes.

    Each evolution entry represents one generation in the evolutionary process,
    including which agents were tested and which won.
    """
    __tablename__ = 'evolutions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    generation = Column(Integer, nullable=False, index=True)

    # Parent and children
    parent_version_id = Column(String(50), ForeignKey('agent_versions.version_id'), nullable=True)
    winner_version_id = Column(String(50), ForeignKey('agent_versions.version_id'), nullable=True)

    # Candidates tested in this generation
    candidates = Column(JSON, nullable=True)  # List of version_ids

    # Performance
    best_score = Column(Float, default=0.0)
    improvement = Column(Float, default=0.0)  # Improvement over parent

    # Evolution strategy
    selection_strategy = Column(String(50), nullable=True)
    mutation_strategies = Column(JSON, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Evolution(gen={self.generation}, best_score={self.best_score:.2f})>"


def create_database(db_url: str = "sqlite:///data/agents.db") -> sessionmaker:
    """
    Create the database and all tables.

    Args:
        db_url: Database connection string

    Returns:
        SQLAlchemy Session class
    """
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session


def get_session(db_url: str = "sqlite:///data/agents.db"):
    """
    Get a database session.

    Args:
        db_url: Database connection string

    Returns:
        Database session
    """
    Session = create_database(db_url)
    return Session()
