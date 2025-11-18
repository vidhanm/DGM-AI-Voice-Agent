#!/usr/bin/env python3
"""
Darwin Gödel Machine Voice Agent - Main Entry Point

This is the main entry point for the self-evolving voice agent system.
"""

import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Darwin Gödel Machine Voice Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run text-based simulation with personas
  python main.py --mode simulate --generations 5

  # Run voice conversation
  python main.py --mode voice

  # Run full evolution cycle
  python main.py --mode evolve --generations 10 --threshold 85

  # Evaluate a specific agent version
  python main.py --mode evaluate --agent-id v1.0
        """
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=["simulate", "voice", "evolve", "evaluate"],
        default="simulate",
        help="Operation mode (default: simulate)"
    )

    parser.add_argument(
        "--generations",
        type=int,
        default=10,
        help="Number of evolution generations (default: 10)"
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=85.0,
        help="Success threshold score (default: 85.0)"
    )

    parser.add_argument(
        "--agent-id",
        type=str,
        help="Specific agent version ID to use/evaluate"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Import mode handlers
    if args.mode == "simulate":
        print("🤖 Running text-based simulation mode...")
        try:
            from simulation import ConversationRunner, PersonaEngine
            from core import Config, PromptManager, BaseAgent
            from evolution import AgentArchive
            from log_manager import ConversationLogger

            # Load configuration
            config = Config()

            # Get agent to use
            if args.agent_id:
                agent_id = args.agent_id
                print(f"Using specified agent: {agent_id}")

                # Load agent from archive
                archive = AgentArchive()
                agent_data = archive.get_agent(agent_id)
                if not agent_data:
                    print(f"❌ Agent {agent_id} not found in archive")
                    return 1
                prompt = agent_data['prompt']
            else:
                # Use baseline prompt
                agent_id = "baseline-simulation"
                print("Using baseline prompt")

                prompt_manager = PromptManager()
                prompt = prompt_manager.create_agent_prompt(
                    'base_prompt.yaml',
                    company_name=config.get('company.name', 'Acme Financial'),
                    agent_name=config.get('agent.name', 'Sarah'),
                    tone=config.get('agent.tone', 'empathetic')
                )

            # Get personas to test
            personas = config.get('evolution.test_personas', [
                'angry_anthony', 'evasive_emma', 'curious_carlos',
                'cooperative_chloe', 'desperate_david'
            ])

            print(f"\nTesting against {len(personas)} personas:")
            for persona in personas:
                print(f"  • {persona}")
            print()

            # Run conversations
            results = []
            max_turns = config.get('simulation.max_turns', 20)

            for i, persona_name in enumerate(personas, 1):
                print(f"[{i}/{len(personas)}] Running conversation with {persona_name}...")

                # Create agent instance for this conversation
                agent = BaseAgent(
                    agent_version_id=agent_id,
                    prompt=prompt,
                    config=config
                )

                # Create persona instance
                persona = PersonaEngine(persona_name=persona_name, config=config)

                # Create conversation runner
                runner = ConversationRunner(
                    agent=agent,
                    persona=persona,
                    max_turns=max_turns
                )

                # Run the conversation
                result = runner.run_conversation()

                results.append(result)
                print(f"    Outcome: {result['outcome']}")
                print(f"    Turns: {result['turn_count']}")
                print()

            # Display summary
            print("=" * 60)
            print("SIMULATION COMPLETE")
            print("=" * 60)
            print(f"Total conversations: {len(results)}")
            print(f"Successful: {sum(1 for r in results if r['outcome'] == 'success')}")
            print(f"Failed: {sum(1 for r in results if r['outcome'] == 'failure')}")
            print(f"Incomplete: {sum(1 for r in results if r['outcome'] == 'incomplete')}")
            print()
            print(f"Conversation logs saved to: data/conversations/")
            print("=" * 60)

            return 0

        except ImportError as e:
            print(f"❌ Error: Simulation components not found")
            print(f"   {e}")
            return 1
        except Exception as e:
            print(f"❌ Error during simulation: {e}")
            import traceback
            traceback.print_exc()
            return 1

    elif args.mode == "voice":
        print("🎤 Running voice conversation mode...")
        try:
            from voice.voice_agent import main as run_voice_agent
            from evolution import AgentArchive

            # Get agent to use
            if args.agent_id:
                agent_id = args.agent_id
                print(f"Using specified agent: {agent_id}")
            else:
                # Use best evolved agent if available
                try:
                    archive = AgentArchive()
                    best_agent = archive.get_best_agent()
                    if best_agent:
                        agent_id = best_agent['id']
                        print(f"Using best evolved agent: {agent_id}")
                        print(f"  Score: {best_agent.get('composite_score', 0):.1f}/100")
                    else:
                        agent_id = "voice-baseline-v1"
                        print("No evolved agents found, using baseline")
                except Exception as e:
                    agent_id = "voice-baseline-v1"
                    print(f"Error loading agent: {e}")
                    print("Using baseline agent")

            # Run voice agent
            print("\n" + "=" * 60)
            print("Starting LiveKit voice agent...")
            print("Join the room via: https://cloud.livekit.io")
            print("Press Ctrl+C to stop")
            print("=" * 60 + "\n")

            run_voice_agent(agent_version_id=agent_id)

        except ImportError as e:
            print(f"❌ Error: Voice dependencies not installed")
            print(f"   {e}")
            print("\nInstall with:")
            print("  pip install 'livekit-agents[deepgram,cartesia,silero]'")
            return 1
        except KeyboardInterrupt:
            print("\n\n👋 Voice agent stopped")
            return 0
        except Exception as e:
            print(f"❌ Error running voice agent: {e}")
            import traceback
            traceback.print_exc()
            return 1

    elif args.mode == "evolve":
        print("🧬 Running evolution mode...")
        try:
            from evolution import EvolutionaryLoop, TerminationPolicy, AgentArchive
            from core import Config, PromptManager

            # Load configuration
            config = Config()

            # Create components
            archive = AgentArchive()

            # Create termination policy
            policy = TerminationPolicy(
                success_threshold=args.threshold,
                max_generations=args.generations,
                plateau_generations=config.get('evolution.plateau_generations', 5),
                min_improvement=config.get('evolution.min_improvement', 0.5)
            )

            # Load baseline prompt
            prompt_manager = PromptManager()
            baseline_prompt = prompt_manager.create_agent_prompt(
                'base_prompt.yaml',
                company_name=config.get('company.name', 'Acme Financial'),
                agent_name=config.get('agent.name', 'Sarah'),
                tone=config.get('agent.tone', 'empathetic')
            )

            # Display configuration
            print()
            print("Evolution Configuration:")
            print(f"  Max generations: {args.generations}")
            print(f"  Success threshold: {args.threshold}/100")
            print(f"  Plateau detection: {config.get('evolution.plateau_generations', 5)} generations")
            print(f"  Variants per generation: {config.get('evolution.variants_per_generation', 3)}")
            print(f"  Test personas: {', '.join(config.get('evolution.test_personas', []))}")
            print(f"  LLM Provider: {config.get('llm.provider', 'openai').upper()}")
            print(f"  LLM Model: {config.get('llm.model', 'unknown')}")
            print()

            # Create evolutionary loop
            evolution = EvolutionaryLoop(
                archive=archive,
                termination_policy=policy,
                config=config
            )

            print("=" * 60)
            print("STARTING EVOLUTION")
            print("=" * 60)
            print()

            # Run evolution!
            best_agent_id, summary = evolution.evolve(
                baseline_prompt=baseline_prompt,
                baseline_metadata={
                    'source': 'base_prompt.yaml',
                    'cli_args': vars(args)
                }
            )

            # Print results
            print()
            print("=" * 60)
            print("EVOLUTION COMPLETE!")
            print("=" * 60)
            print(f"Best Agent ID: {best_agent_id}")
            print(f"Generations Run: {summary['generations_run']}")
            print(f"Best Score: {summary['best_score']:.1f}/100")
            print(f"Baseline Score: {summary.get('baseline_score', 0):.1f}/100")
            print(f"Improvement: +{summary['best_score'] - summary.get('baseline_score', 0):.1f} points")
            print(f"Termination Reason: {summary['termination_reason']}")
            print()
            print("Best agent saved to database!")
            print(f"You can use it with: python main.py --mode voice --agent-id {best_agent_id}")
            print("=" * 60)

            return 0

        except ImportError as e:
            print(f"❌ Error: Evolution components not found")
            print(f"   {e}")
            return 1
        except Exception as e:
            print(f"❌ Error during evolution: {e}")
            import traceback
            traceback.print_exc()
            return 1

    elif args.mode == "evaluate":
        print("📊 Running evaluation mode...")
        try:
            from evaluation import Evaluator
            from evolution import AgentArchive
            from core import Config, PromptManager, BaseAgent
            from log_manager import ConversationLogger
            from simulation import ConversationRunner, PersonaEngine

            # Load configuration
            config = Config()

            # Get agent to evaluate
            if args.agent_id:
                agent_id = args.agent_id
                print(f"Evaluating agent: {agent_id}")

                # Load from archive
                archive = AgentArchive()
                agent_data = archive.get_agent(agent_id)
                if not agent_data:
                    print(f"❌ Agent {agent_id} not found in archive")
                    return 1
                prompt = agent_data['prompt']

            else:
                # Use best evolved agent or baseline
                try:
                    archive = AgentArchive()
                    best_agent = archive.get_best_agent()
                    if best_agent:
                        agent_id = best_agent['id']
                        prompt = best_agent['prompt']
                        print(f"Evaluating best agent: {agent_id}")
                        print(f"  Current score: {best_agent.get('composite_score', 0):.1f}/100")
                    else:
                        agent_id = "baseline-evaluation"
                        print("No evolved agents found, evaluating baseline")
                        prompt_manager = PromptManager()
                        prompt = prompt_manager.create_agent_prompt(
                            'base_prompt.yaml',
                            company_name=config.get('company.name', 'Acme Financial'),
                            agent_name=config.get('agent.name', 'Sarah'),
                            tone=config.get('agent.tone', 'empathetic')
                        )
                except Exception as e:
                    print(f"Error loading agent: {e}")
                    return 1

            print()

            # Get personas to test
            personas = config.get('evolution.test_personas', [
                'angry_anthony', 'evasive_emma', 'curious_carlos',
                'cooperative_chloe', 'desperate_david'
            ])

            # Run conversations
            print(f"Running conversations with {len(personas)} personas...")
            conversation_ids = []
            max_turns = config.get('simulation.max_turns', 20)

            for i, persona_name in enumerate(personas, 1):
                print(f"  [{i}/{len(personas)}] {persona_name}...", end=" ")

                # Create agent instance for this conversation
                agent = BaseAgent(
                    agent_version_id=agent_id,
                    prompt=prompt,
                    config=config
                )

                # Create persona instance
                persona = PersonaEngine(persona_name=persona_name, config=config)

                # Create conversation runner
                runner = ConversationRunner(
                    agent=agent,
                    persona=persona,
                    max_turns=max_turns
                )

                # Run the conversation
                result = runner.run_conversation()

                conversation_ids.append(result['conversation_id'])
                print(f"{result['outcome']}")

            print()

            # Evaluate all conversations
            print("Evaluating conversations...")
            evaluator = Evaluator(config=config)
            logger = ConversationLogger()

            all_scores = []
            for conversation_id in conversation_ids:
                conversation = logger.get_conversation(conversation_id)
                scores = evaluator.evaluate_conversation(conversation)
                all_scores.append(scores)

            # Calculate aggregate statistics
            avg_goal = sum(s['goal_completion_score'] for s in all_scores) / len(all_scores)
            avg_quality = sum(s['conversational_quality_score'] for s in all_scores) / len(all_scores)
            avg_compliance = sum(s['compliance_score'] for s in all_scores) / len(all_scores)
            avg_composite = sum(s['composite_score'] for s in all_scores) / len(all_scores)
            pass_count = sum(1 for s in all_scores if s['passed'])

            # Display results
            print()
            print("=" * 60)
            print("EVALUATION RESULTS")
            print("=" * 60)
            print(f"Agent ID: {agent_id}")
            print(f"Conversations: {len(all_scores)}")
            print()
            print("Average Scores:")
            print(f"  Goal Completion:        {avg_goal:.1f}/100")
            print(f"  Conversational Quality: {avg_quality:.1f}/100")
            print(f"  Compliance:             {avg_compliance:.1f}/100")
            print(f"  Composite Score:        {avg_composite:.1f}/100")
            print()
            print(f"Pass Rate: {pass_count}/{len(all_scores)} ({pass_count/len(all_scores)*100:.0f}%)")
            print()

            # Show per-persona breakdown
            print("Per-Persona Breakdown:")
            for i, (persona, scores) in enumerate(zip(personas, all_scores)):
                status = "✅ PASSED" if scores['passed'] else "❌ FAILED"
                print(f"  {persona:20s} {scores['composite_score']:5.1f}/100  {status}")

            print("=" * 60)

            return 0

        except ImportError as e:
            print(f"❌ Error: Evaluation components not found")
            print(f"   {e}")
            return 1
        except Exception as e:
            print(f"❌ Error during evaluation: {e}")
            import traceback
            traceback.print_exc()
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
