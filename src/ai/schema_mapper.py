"""AI-powered schema mapping."""

import json
import logging
from typing import Dict, List, Any, Optional

import anthropic

from src.core.config import settings

logger = logging.getLogger(__name__)


class SchemaMapper:
    """AI-powered schema mapping between ERP systems."""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-3-opus-20240229"
    
    async def generate_mapping(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        source_name: str = "Source",
        target_name: str = "Target",
        examples: Optional[List[Dict]] = None
    ) -> Dict[str, str]:
        """Generate field mapping between two schemas.
        
        Args:
            source_schema: Source system schema {field_name: field_type}
            target_schema: Target system schema {field_name: field_type}
            source_name: Name of source system
            target_name: Name of target system
            examples: Optional example mappings for few-shot learning
            
        Returns:
            Mapping dictionary {source_field: target_field}
        """
        
        prompt = self._build_mapping_prompt(
            source_schema, target_schema,
            source_name, target_name, examples
        )
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse the response
            content = response.content[0].text
            mapping = self._parse_mapping_response(content)
            
            return mapping
            
        except Exception as e:
            logger.error(f"Error generating mapping: {e}")
            raise
    
    def _build_mapping_prompt(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        source_name: str,
        target_name: str,
        examples: Optional[List[Dict]]
    ) -> str:
        """Build the prompt for schema mapping."""
        
        prompt = f"""You are an expert in Enterprise Resource Planning (ERP) systems and data integration.
Your task is to create a field mapping between two ERP systems.

## Source System: {source_name}

Schema:
```json
{json.dumps(source_schema, indent=2)}
```

## Target System: {target_name}

Schema:
```json
{json.dumps(target_schema, indent=2)}
```

## Task

Create a mapping from source fields to target fields. Consider:
1. Field names and semantics
2. Data types compatibility
3. Business context (customers, orders, products, etc.)
4. Common ERP conventions

Only map fields that have clear semantic equivalents. If a field has no equivalent, do not include it in the mapping.

## Output Format

Return ONLY a JSON object with the mapping in this format:
```json
{{
  "source_field_1": "target_field_1",
  "source_field_2": "target_field_2"
}}
```
"""
        
        if examples:
            prompt += "\n## Examples\n\n"
            for i, example in enumerate(examples, 1):
                prompt += f"Example {i}:\n"
                prompt += f"Source: {json.dumps(example['source'], indent=2)}\n"
                prompt += f"Target: {json.dumps(example['target'], indent=2)}\n"
                prompt += f"Mapping: {json.dumps(example['mapping'], indent=2)}\n\n"
        
        return prompt
    
    def _parse_mapping_response(self, content: str) -> Dict[str, str]:
        """Parse the mapping from AI response."""
        # Extract JSON from the response
        try:
            # Look for JSON block
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0]
            else:
                json_str = content
            
            mapping = json.loads(json_str.strip())
            
            # Validate it's a dict of strings
            if not isinstance(mapping, dict):
                raise ValueError("Response is not a valid mapping dictionary")
            
            return mapping
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse mapping response: {e}")
            logger.error(f"Response content: {content}")
            raise
    
    async def detect_conflicts(
        self,
        mapping: Dict[str, str],
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detect potential data conflicts in the mapping.
        
        Args:
            mapping: Field mapping dictionary
            source_schema: Source schema
            target_schema: Target schema
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        for source_field, target_field in mapping.items():
            source_type = source_schema.get(source_field, {}).get("type", "unknown")
            target_type = target_schema.get(target_field, {}).get("type", "unknown")
            
            # Check type compatibility
            type_conflicts = self._check_type_compatibility(source_type, target_type)
            if type_conflicts:
                conflicts.append({
                    "type": "type_mismatch",
                    "source_field": source_field,
                    "target_field": target_field,
                    "source_type": source_type,
                    "target_type": target_type,
                    "message": type_conflicts
                })
        
        return conflicts
    
    def _check_type_compatibility(self, source_type: str, target_type: str) -> str:
        """Check if two types are compatible.
        
        Returns:
            Conflict message if incompatible, empty string if compatible
        """
        # Simple type compatibility checks
        compatible_types = {
            "string": ["string", "text"],
            "number": ["number", "decimal", "integer"],
            "integer": ["integer", "number"],
            "boolean": ["boolean"],
            "date": ["date", "datetime"],
            "datetime": ["datetime", "date"],
        }
        
        source_compat = compatible_types.get(source_type, [source_type])
        
        if target_type not in source_compat:
            return f"Type mismatch: {source_type} -> {target_type} may require conversion"
        
        return ""
    
    async def generate_transformation(
        self,
        source_field: str,
        target_field: str,
        source_type: str,
        target_type: str,
        transformation_hint: Optional[str] = None
    ) -> str:
        """Generate transformation code for a field mapping.
        
        Args:
            source_field: Source field name
            target_field: Target field name
            source_type: Source field type
            target_type: Target field type
            transformation_hint: Optional hint for transformation
            
        Returns:
            Python code for the transformation
        """
        prompt = f"""Generate Python code to transform data from one field to another.

Source Field: {source_field}
Source Type: {source_type}
Target Field: {target_field}
Target Type: {target_type}
"""
        
        if transformation_hint:
            prompt += f"\nTransformation Hint: {transformation_hint}\n"
        
        prompt += """
Generate a Python function that performs this transformation.
The function should be named `transform` and take one argument `value`.

Output only the Python code, no explanation.
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            code = response.content[0].text.strip()
            
            # Clean up code block markers
            if code.startswith("```python"):
                code = code[9:]
            if code.startswith("```"):
                code = code[3:]
            if code.endswith("```"):
                code = code[:-3]
            
            return code.strip()
            
        except Exception as e:
            logger.error(f"Error generating transformation: {e}")
            raise
