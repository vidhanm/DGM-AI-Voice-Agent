#!/usr/bin/env python3
"""
FastAPI Web Interface for Darwin-Gödel Machine Voice Agent

This provides a web-based UI for running simulations, evolution,
evaluation, and voice chat.
"""

import asyncio
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import our existing modules
from core import Config, PromptManager, BaseAgent
from evolution import AgentArchive, EvolutionaryLoop
from evaluation import Evaluator
from simulation import ConversationRunner, PersonaEngine
from log_manager import ConversationLogger

# Initialize FastAPI app
app = FastAPI(
    title="Darwin-Gödel Voice Agent",
    description="Self-evolving voice agent for debt collection",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared state
config = Config()
archive = AgentArchive()
logger = ConversationLogger()

# Pydantic models for API requests
class SimulateRequest(BaseModel):
    agent_id: Optional[str] = None
    personas: List[str] = ['angry_anthony', 'evasive_emma', 'curious_carlos', 'cooperative_chloe', 'desperate_david']
    max_turns: int = 20

class EvolveRequest(BaseModel):
    max_generations: int = 10
    success_threshold: float = 85.0
    variants_per_generation: int = 3

class EvaluateRequest(BaseModel):
    agent_id: Optional[str] = None
    personas: List[str] = ['angry_anthony', 'evasive_emma', 'curious_carlos', 'cooperative_chloe', 'desperate_david']

# API Endpoints

@app.get("/")
async def root():
    """Redirect to index.html"""
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/status")
async def get_status():
    """Get system status"""
    try:
        best_agent = archive.get_best_agent()
        all_agents = archive.list_agents(limit=100)

        return {
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "config": {
                "llm_provider": config.get('llm.provider', 'unknown'),
                "llm_model": config.get('llm.model', 'unknown'),
            },
            "agents": {
                "total": len(all_agents),
                "best": best_agent.version_id if best_agent else None,
                "best_score": best_agent.composite_score if best_agent else 0
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/api/agents")
async def list_agents():
    """List all agents"""
    try:
        agents = archive.list_agents(limit=100)
        return {
            "agents": [
                {
                    "id": agent.version_id,
                    "generation": agent.generation,
                    "composite_score": agent.composite_score,
                    "created_at": agent.created_at.isoformat() if agent.created_at else None,
                    "parent_id": agent.parent_id,
                }
                for agent in agents
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent details"""
    try:
        agent = archive.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        return agent.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/simulate")
async def run_simulation(request: SimulateRequest):
    """Run simulation mode"""
    try:
        # Get agent prompt
        if request.agent_id:
            agent_data = archive.get_agent(request.agent_id)
            if not agent_data:
                raise HTTPException(status_code=404, detail=f"Agent {request.agent_id} not found")
            prompt = agent_data.prompt
            agent_id = request.agent_id
        else:
            # Use baseline
            agent_id = "baseline-simulation"
            prompt_manager = PromptManager()
            prompt = prompt_manager.create_agent_prompt(
                'base_prompt.yaml',
                company_name=config.get('company.name', 'Acme Financial'),
                agent_name=config.get('agent.name', 'Sarah'),
                tone=config.get('agent.tone', 'empathetic')
            )

        # Run conversations
        results = []
        for persona_name in request.personas:
            # Create instances
            agent = BaseAgent(agent_id, prompt, config)
            persona = PersonaEngine(persona_name, config=config)
            runner = ConversationRunner(agent, persona, max_turns=request.max_turns)

            # Run conversation
            result = runner.run_conversation()
            results.append(result)

        # Calculate summary
        summary = {
            "total": len(results),
            "success": sum(1 for r in results if r['outcome'] == 'success'),
            "failure": sum(1 for r in results if r['outcome'] == 'failure'),
            "incomplete": sum(1 for r in results if r['outcome'] == 'incomplete'),
        }

        return {
            "agent_id": agent_id,
            "results": results,
            "summary": summary
        }

    except HTTPException:
        raise
    except Exception as e:
        # Print full error traceback to terminal
        print("\n" + "="*60)
        print("ERROR in /api/simulate endpoint:")
        print("="*60)
        traceback.print_exc()
        print("="*60 + "\n")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/evaluate")
async def run_evaluation(request: EvaluateRequest):
    """Run evaluation mode"""
    try:
        # Get agent
        if request.agent_id:
            agent_data = archive.get_agent(request.agent_id)
            if not agent_data:
                raise HTTPException(status_code=404, detail=f"Agent {request.agent_id} not found")
            prompt = agent_data.prompt
            agent_id = request.agent_id
        else:
            # Use best agent or baseline
            best_agent = archive.get_best_agent()
            if best_agent:
                agent_id = best_agent.version_id
                prompt = best_agent.prompt
            else:
                agent_id = "baseline-evaluation"
                prompt_manager = PromptManager()
                prompt = prompt_manager.create_agent_prompt(
                    'base_prompt.yaml',
                    company_name=config.get('company.name', 'Acme Financial'),
                    agent_name=config.get('agent.name', 'Sarah'),
                    tone=config.get('agent.tone', 'empathetic')
                )

        # Run conversations
        conversation_ids = []
        for persona_name in request.personas:
            agent = BaseAgent(agent_id, prompt, config)
            persona = PersonaEngine(persona_name, config=config)
            runner = ConversationRunner(agent, persona, max_turns=20)
            result = runner.run_conversation()
            conversation_ids.append(result['conversation_id'])

        # Evaluate conversations
        evaluator = Evaluator(config=config)
        all_scores = []
        for conversation_id in conversation_ids:
            conversation = logger.get_conversation(conversation_id)
            scores = evaluator.evaluate_conversation(
                transcript=conversation['transcript'],
                persona_name=conversation['persona_name'],
                conversation_id=conversation_id
            )
            all_scores.append(scores)

        # Calculate aggregates
        avg_scores = {
            "goal_completion": sum(s['goal_completion_score'] for s in all_scores) / len(all_scores),
            "conversational_quality": sum(s['conversational_quality_score'] for s in all_scores) / len(all_scores),
            "compliance": sum(s['compliance_score'] for s in all_scores) / len(all_scores),
            "composite": sum(s['composite_score'] for s in all_scores) / len(all_scores),
        }
        pass_count = sum(1 for s in all_scores if s['passed'])

        return {
            "agent_id": agent_id,
            "scores": all_scores,
            "average_scores": avg_scores,
            "pass_count": pass_count,
            "total_conversations": len(all_scores),
            "pass_rate": pass_count / len(all_scores) if all_scores else 0
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations")
async def list_conversations(limit: int = 50):
    """List recent conversations"""
    try:
        # This is a placeholder - implement based on your ConversationLogger
        return {
            "conversations": [],
            "message": "Conversation listing not yet implemented"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get specific conversation"""
    try:
        conversation = logger.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket for evolution updates
@app.websocket("/ws/evolve")
async def websocket_evolve(websocket: WebSocket):
    """WebSocket endpoint for real-time evolution updates"""
    await websocket.accept()

    try:
        # Receive evolution parameters
        data = await websocket.receive_json()
        max_generations = data.get('max_generations', 10)
        success_threshold = data.get('success_threshold', 85.0)

        # Send start message
        await websocket.send_json({
            "type": "start",
            "message": "Starting evolution...",
            "timestamp": datetime.now().isoformat()
        })

        # Update config with user's custom evolution settings
        # EvolutionaryLoop creates TerminationPolicy from config internally
        config.set('evolution.success_threshold', success_threshold)
        config.set('evolution.max_generations', max_generations)

        # Create required components for EvolutionaryLoop
        prompt_manager = PromptManager()
        evaluator = Evaluator(config=config)

        # Create evolutionary loop with correct parameters
        evolution = EvolutionaryLoop(
            config=config,
            agent_archive=archive,
            prompt_manager=prompt_manager,
            evaluator=evaluator
        )

        # Send progress update
        await websocket.send_json({
            "type": "config",
            "data": {
                "max_generations": max_generations,
                "threshold": success_threshold,
                "llm_provider": config.get('llm.provider', 'unknown'),
                "llm_model": config.get('llm.model', 'unknown'),
            }
        })

        # Run evolution (this will block - in production we'd run in background)
        await websocket.send_json({
            "type": "info",
            "message": "Evolution running... (this may take several minutes)"
        })

        # Run evolution - returns a dict with all results
        results = evolution.evolve(max_generations=max_generations)

        # Send completion
        await websocket.send_json({
            "type": "complete",
            "data": {
                "best_agent_id": results['best_agent_id'],
                "generations_run": results['generations'],
                "best_score": results['best_score'],
                "baseline_score": results.get('baseline_score', 0),
                "improvement": results['improvement'],
                "termination_reason": results['termination_reason']
            }
        })

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        await websocket.close()

# Serve static files (must be at the end)
app.mount("/static", StaticFiles(directory="static"), name="static")

def main():
    """Run the web server"""
    print("=" * 60)
    print("Darwin-Gödel Machine Voice Agent - Web Interface")
    print("=" * 60)
    print(f"LLM Provider: {config.get('llm.provider', 'unknown').upper()}")
    print(f"LLM Model: {config.get('llm.model', 'unknown')}")
    print()
    print("Starting web server...")
    print("URL: http://localhost:8000")
    print("=" * 60)
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    main()
