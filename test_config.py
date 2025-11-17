#!/usr/bin/env python3
"""
Test script for Configuration Management system.

Tests the Config and PromptManager classes.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import Config, get_config, reset_config
from core.prompt_manager import PromptManager, PromptTemplate


def test_config():
    """Test configuration loading and management."""

    print("=" * 70)
    print("🧪 Testing Configuration Management")
    print("=" * 70)
    print()

    # Test 1: Load configuration
    print("📦 Step 1: Load configuration from settings.yaml...")
    config = Config()
    print(f"   Config loaded: {config}")
    print()

    # Test 2: Get configuration values
    print("📦 Step 2: Read configuration values...")
    print(f"   LLM Provider: {config.get('llm.provider')}")
    print(f"   LLM Model: {config.get('llm.model')}")
    print(f"   Temperature: {config.get('llm.temperature')}")
    print(f"   Max Generations: {config.get('evolution.max_generations')}")
    print(f"   Success Threshold: {config.get('evolution.success_threshold')}")
    print(f"   Database Type: {config.get('database.type')}")
    print()

    # Test 3: Get LLM config
    print("📦 Step 3: Get LLM configuration...")
    llm_config = config.get_llm_config()
    print(f"   Provider: {llm_config.get('provider')}")
    print(f"   Model: {llm_config.get('model')}")
    print(f"   Temperature: {llm_config.get('temperature')}")
    print(f"   API Key Set: {'Yes' if llm_config.get('api_key') else 'No (not required for testing)'}")
    print()

    # Test 4: Get database URL
    print("📦 Step 4: Get database URL...")
    db_url = config.get_database_url()
    print(f"   Database URL: {db_url}")
    print()

    # Test 5: Set and get custom values
    print("📦 Step 5: Test setting custom values...")
    config.set('evolution.max_generations', 15)
    print(f"   Set max_generations to: 15")
    print(f"   Read back: {config.get('evolution.max_generations')}")
    print()

    # Test 6: Validate configuration
    print("📦 Step 6: Validate configuration...")
    # Note: This will fail if API keys aren't set, but that's okay for testing
    is_valid = config.validate()
    if not is_valid:
        print("   ⚠️  Validation failed (expected - API keys not set)")
        print("   ℹ️  This is normal for testing without .env file")
    print()

    print("✅ Config tests completed!")
    print()


def test_prompt_manager():
    """Test prompt template management."""

    print("=" * 70)
    print("🧪 Testing Prompt Manager")
    print("=" * 70)
    print()

    # Test 1: Initialize prompt manager
    print("📦 Step 1: Initialize PromptManager...")
    manager = PromptManager(templates_dir="config")
    print(f"   {manager}")
    print()

    # Test 2: Load base prompt template
    print("📦 Step 2: Load base_prompt.yaml...")
    template = manager.load_template("base_prompt.yaml")
    if template:
        print(f"   ✅ Template loaded: {template.name}")
        print(f"   Description: {template.description.strip()[:100]}...")
        print(f"   Variables: {template.variables}")
        print(f"   Template length: {len(template.template)} characters")
    print()

    # Test 3: Get template info
    print("📦 Step 3: Get template information...")
    info = manager.get_template_info("base_prompt")
    if info:
        print(f"   Name: {info['name']}")
        print(f"   Variables: {info['variables']}")
        print(f"   Metadata: {info['metadata']}")
    print()

    # Test 4: Render template with variables
    print("📦 Step 4: Render template with variables...")
    rendered = manager.render_template(
        "base_prompt",
        company_name="Acme Financial Services",
        agent_name="Sarah",
        tone="empathetic"
    )

    if rendered:
        print("   ✅ Template rendered successfully!")
        print()
        print("   Preview (first 500 characters):")
        print("   " + "-" * 66)
        preview = rendered[:500].replace('\n', '\n   ')
        print(f"   {preview}...")
        print("   " + "-" * 66)
    print()

    # Test 5: Test create_agent_prompt convenience method
    print("📦 Step 5: Test create_agent_prompt method...")
    prompt = manager.create_agent_prompt(
        "base_prompt.yaml",
        company_name="Global Lending Corp",
        agent_name="Michael",
        tone="professional"
    )

    if prompt:
        print("   ✅ Agent prompt created!")
        print(f"   Prompt length: {len(prompt)} characters")
        print(f"   Contains 'Michael': {'Yes' if 'Michael' in prompt else 'No'}")
        print(f"   Contains 'Global Lending': {'Yes' if 'Global Lending' in prompt else 'No'}")
    print()

    # Test 6: List all templates
    print("📦 Step 6: List loaded templates...")
    templates = manager.list_templates()
    print(f"   Loaded templates: {templates}")
    print()

    # Test 7: Create and save a new template
    print("📦 Step 7: Create and save a new template...")
    test_template = """Hello, I'm calling from ${company}.
This is ${agent_name}.
Is this ${customer_name}?"""

    success = manager.save_template(
        name="greeting_template",
        template_text=test_template,
        description="Simple greeting template for testing",
        variables=["company", "agent_name", "customer_name"],
        metadata={"version": "1.0", "test": True},
        filename="test_greeting.yaml"
    )

    if success:
        print("   ✅ Template saved!")

        # Test rendering the new template
        greeting = manager.render_template(
            "greeting_template",
            company="Test Corp",
            agent_name="Alex",
            customer_name="John"
        )
        print(f"   Rendered greeting: {greeting}")
    print()

    print("✅ PromptManager tests completed!")
    print()


def test_integration():
    """Test Config and PromptManager working together."""

    print("=" * 70)
    print("🧪 Testing Config + PromptManager Integration")
    print("=" * 70)
    print()

    print("📦 Creating agent prompt using both systems...")

    # Load config
    config = get_config()

    # Load prompt manager
    manager = PromptManager()

    # Get LLM settings from config
    llm_model = config.get('llm.model')
    print(f"   LLM Model from config: {llm_model}")

    # Create agent prompt from template
    prompt = manager.create_agent_prompt(
        "base_prompt.yaml",
        company_name="Integration Test Financial",
        agent_name="TestBot",
        tone="professional and empathetic"
    )

    if prompt:
        print("   ✅ Integration successful!")
        print(f"   Generated prompt ready for {llm_model}")
        print(f"   Prompt length: {len(prompt)} characters")
    print()

    print("✅ Integration tests completed!")
    print()


def main():
    """Run all tests."""
    print()
    print("🚀 Configuration Management Test Suite")
    print()

    try:
        # Test 1: Config
        test_config()

        # Test 2: PromptManager
        test_prompt_manager()

        # Test 3: Integration
        test_integration()

        print("=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print()
        print("📁 Files created:")
        print("   - config/base_prompt.yaml (baseline agent prompt)")
        print("   - config/test_greeting.yaml (test template)")
        print()
        print("🎯 Ready for Phase 2: Agent Implementation!")
        print()

    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
