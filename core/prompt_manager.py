"""
Prompt Management for Darwin Godel Machine Voice Agent.

This module handles loading, rendering, and managing prompt templates
with variable substitution.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from string import Template


class PromptTemplate:
    """
    Represents a prompt template with metadata and variables.
    """

    def __init__(
        self,
        name: str,
        template: str,
        description: Optional[str] = None,
        variables: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a prompt template.

        Args:
            name: Template name/identifier
            template: Template string (supports ${variable} syntax)
            description: Template description
            variables: List of variable names used in template
            metadata: Additional metadata
        """
        self.name = name
        self.template = template
        self.description = description or ""
        self.variables = variables or []
        self.metadata = metadata or {}

    def render(self, **kwargs) -> str:
        """
        Render the template with provided variables.

        Args:
            **kwargs: Variable values

        Returns:
            Rendered prompt string

        Example:
            >>> template = PromptTemplate(
            ...     name="greeting",
            ...     template="Hello ${name}, welcome to ${company}!"
            ... )
            >>> prompt = template.render(name="Alice", company="Acme Corp")
            >>> print(prompt)  # "Hello Alice, welcome to Acme Corp!"
        """
        try:
            t = Template(self.template)
            return t.safe_substitute(**kwargs)
        except Exception as e:
            print(f"❌ Error rendering template '{self.name}': {e}")
            return self.template

    def validate(self, **kwargs) -> bool:
        """
        Validate that all required variables are provided.

        Args:
            **kwargs: Variable values

        Returns:
            True if all required variables provided
        """
        provided = set(kwargs.keys())
        required = set(self.variables)
        missing = required - provided

        if missing:
            print(f"❌ Missing required variables: {missing}")
            return False

        return True

    def __repr__(self):
        return f"<PromptTemplate(name='{self.name}', vars={self.variables})>"


class PromptManager:
    """
    Manages prompt templates for voice agents.

    Handles loading templates from YAML files, rendering with variables,
    and versioning prompts for evolution.
    """

    def __init__(self, templates_dir: str = "config"):
        """
        Initialize prompt manager.

        Args:
            templates_dir: Directory containing prompt template files
        """
        self.templates_dir = Path(templates_dir)
        self.templates: Dict[str, PromptTemplate] = {}

    def load_template(self, template_path: str) -> Optional[PromptTemplate]:
        """
        Load a prompt template from a YAML file.

        Args:
            template_path: Path to template file (relative to templates_dir)

        Returns:
            PromptTemplate object or None if load fails

        Example:
            >>> manager = PromptManager()
            >>> template = manager.load_template('base_prompt.yaml')
            >>> prompt = template.render(agent_name="DebtBot")
        """
        file_path = self.templates_dir / template_path

        if not file_path.exists():
            print(f"❌ Template file not found: {file_path}")
            return None

        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)

            # Extract template data
            name = data.get('name', template_path)
            template_text = data.get('template', data.get('prompt', ''))
            description = data.get('description', '')
            variables = data.get('variables', [])
            metadata = data.get('metadata', {})

            # Create template object
            template = PromptTemplate(
                name=name,
                template=template_text,
                description=description,
                variables=variables,
                metadata=metadata
            )

            # Cache it
            self.templates[name] = template

            print(f"✅ Loaded template: {name}")
            return template

        except Exception as e:
            print(f"❌ Error loading template from {file_path}: {e}")
            return None

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """
        Get a cached template by name.

        Args:
            name: Template name

        Returns:
            PromptTemplate object or None if not found
        """
        return self.templates.get(name)

    def render_template(self, name: str, **kwargs) -> Optional[str]:
        """
        Render a template by name with provided variables.

        Args:
            name: Template name
            **kwargs: Variable values

        Returns:
            Rendered prompt string or None if template not found

        Example:
            >>> manager = PromptManager()
            >>> manager.load_template('base_prompt.yaml')
            >>> prompt = manager.render_template('base_prompt',
            ...     tone='empathetic', company='Acme Loans')
        """
        template = self.get_template(name)
        if not template:
            print(f"❌ Template '{name}' not found")
            return None

        return template.render(**kwargs)

    def create_agent_prompt(
        self,
        template_name: str,
        **variables
    ) -> Optional[str]:
        """
        Create an agent prompt from a template.

        This is a convenience method that loads (if needed) and renders
        a template in one call.

        Args:
            template_name: Name of the template (or path to load)
            **variables: Variable values

        Returns:
            Rendered prompt string

        Example:
            >>> manager = PromptManager()
            >>> prompt = manager.create_agent_prompt(
            ...     'base_prompt.yaml',
            ...     company_name='Acme Loans',
            ...     tone='professional'
            ... )
        """
        # Try to get from cache first
        template = self.get_template(template_name)

        # If not cached, try loading it
        if not template:
            template = self.load_template(template_name)

        # If still not found, fail
        if not template:
            return None

        # Render with variables
        return template.render(**variables)

    def list_templates(self) -> List[str]:
        """
        List all loaded templates.

        Returns:
            List of template names
        """
        return list(self.templates.keys())

    def get_template_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a template.

        Args:
            name: Template name

        Returns:
            Dictionary with template info
        """
        template = self.get_template(name)
        if not template:
            return None

        return {
            'name': template.name,
            'description': template.description,
            'variables': template.variables,
            'metadata': template.metadata,
            'template_length': len(template.template)
        }

    def save_template(
        self,
        name: str,
        template_text: str,
        description: str = "",
        variables: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        filename: Optional[str] = None
    ) -> bool:
        """
        Save a template to a YAML file.

        Args:
            name: Template name
            template_text: Template content
            description: Template description
            variables: List of variable names
            metadata: Additional metadata
            filename: Output filename (defaults to {name}.yaml)

        Returns:
            True if saved successfully
        """
        if filename is None:
            filename = f"{name}.yaml"

        file_path = self.templates_dir / filename

        data = {
            'name': name,
            'description': description,
            'template': template_text,
            'variables': variables or [],
            'metadata': metadata or {}
        }

        try:
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

            print(f"✅ Saved template to {file_path}")

            # Also cache it
            template = PromptTemplate(
                name=name,
                template=template_text,
                description=description,
                variables=variables,
                metadata=metadata
            )
            self.templates[name] = template

            return True

        except Exception as e:
            print(f"❌ Error saving template: {e}")
            return False

    def __repr__(self):
        return f"<PromptManager(templates={len(self.templates)})>"
