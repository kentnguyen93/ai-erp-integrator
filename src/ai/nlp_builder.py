"""Natural language integration builder."""

import json
import logging
from typing import Dict, Any, Optional

import anthropic

from src.core.config import settings

logger = logging.getLogger(__name__)


class NLPIntegrationBuilder:
    """Build integrations from natural language descriptions."""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-3-opus-20240229"
    
    async def create_integration(
        self,
        description: str,
        source_system: str,
        target_system: str
    ) -> Dict[str, Any]:
        """Create an integration specification from natural language.
        
        Args:
            description: Natural language description of the integration
            source_system: Source ERP system name
            target_system: Target ERP system name
            
        Returns:
            Integration specification dictionary
        """
        prompt = self._build_integration_prompt(
            description, source_system, target_system
        )
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            integration_spec = self._parse_integration_response(content)
            
            # Add metadata
            integration_spec["source_system"] = source_system
            integration_spec["target_system"] = target_system
            integration_spec["description"] = description
            
            return integration_spec
            
        except Exception as e:
            logger.error(f"Error creating integration: {e}")
            raise
    
    def _build_integration_prompt(
        self,
        description: str,
        source_system: str,
        target_system: str
    ) -> str:
        """Build the prompt for integration creation."""
        
        return f"""You are an expert in ERP system integration and workflow design.
Parse the following integration description and generate a structured specification.

## Integration Description

{description}

## Systems
- Source: {source_system}
- Target: {target_system}

## Task

Generate a JSON specification for this integration that includes:
1. Integration name and description
2. Source and target entities
3. Trigger conditions (event-driven, scheduled, manual)
4. Field mappings
5. Transformations needed
6. Error handling strategy
7. Dependencies and ordering

## Output Format

Return a JSON object with this structure:
```json
{{
  "name": "integration_name",
  "description": "Brief description",
  "trigger": {{
    "type": "event|schedule|manual",
    "config": {{}}
  }},
  "source": {{
    "system": "{source_system}",
    "entity": "entity_name",
    "filters": {{}}
  }},
  "target": {{
    "system": "{target_system}",
    "entity": "entity_name",
    "operation": "create|update|upsert"
  }},
  "mapping": {{
    "source_field": "target_field"
  }},
  "transformations": [
    {{
      "field": "field_name",
      "operation": "convert|lookup|calculate",
      "config": {{}}
    }}
  ],
  "error_handling": {{
    "retry_count": 3,
    "retry_delay": 60,
    "fallback": "queue|notify|skip"
  }}
}}
```

Be specific and include all relevant fields mentioned in the description.
"""
    
    def _parse_integration_response(self, content: str) -> Dict[str, Any]:
        """Parse the integration specification from AI response."""
        try:
            # Extract JSON block
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0]
            else:
                json_str = content
            
            spec = json.loads(json_str.strip())
            return spec
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse integration response: {e}")
            logger.error(f"Response content: {content}")
            raise
    
    async def explain_integration(self, integration_spec: Dict[str, Any]) -> str:
        """Generate human-readable explanation of an integration.
        
        Args:
            integration_spec: Integration specification
            
        Returns:
            Human-readable explanation
        """
        prompt = f"""Explain this ERP integration in clear, business-friendly language:

```json
{json.dumps(integration_spec, indent=2)}
```

Provide:
1. A brief summary of what the integration does
2. When it runs (trigger conditions)
3. What data flows between systems
4. Any important business rules or transformations
5. Error handling approach

Keep it concise but comprehensive.
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Error explaining integration: {e}")
            raise
