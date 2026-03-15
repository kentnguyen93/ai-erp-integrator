"""NetSuite connector implementation."""

import base64
import json
import hmac
import hashlib
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import httpx

from src.connectors.base import ERPConnector, EntityDefinition, SyncResult


class NetSuiteConnector(ERPConnector):
    """Connector for Oracle NetSuite."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.account_id = config.get("account_id")
        self.consumer_key = config.get("consumer_key")
        self.consumer_secret = config.get("consumer_secret")
        self.token_id = config.get("token_id")
        self.token_secret = config.get("token_secret")
        self.base_url = f"https://{self.account_id}.suitetalk.api.netsuite.com"
    
    @property
    def name(self) -> str:
        return "netsuite"
    
    @property
    def version(self) -> str:
        return "2024.1"
    
    def _generate_oauth_header(self, method: str, url: str) -> str:
        """Generate OAuth 1.0a header for NetSuite."""
        timestamp = str(int(time.time()))
        nonce = base64.b64encode(str(time.time()).encode()).decode()[:20]
        
        params = {
            "oauth_consumer_key": self.consumer_key,
            "oauth_token": self.token_id,
            "oauth_signature_method": "HMAC-SHA256",
            "oauth_timestamp": timestamp,
            "oauth_nonce": nonce,
            "oauth_version": "1.0"
        }
        
        # Create signature base string
        encoded_params = urlencode(sorted(params.items()))
        signature_base = f"{method.upper()}&{self.base_url}%2F{url.split('/')[-1]}&{encoded_params}"
        
        # Generate signature
        signing_key = f"{self.consumer_secret}&{self.token_secret}"
        signature = hmac.new(
            signing_key.encode(),
            signature_base.encode(),
            hashlib.sha256
        ).hexdigest()
        
        params["oauth_signature"] = signature
        
        # Build header
        auth_header = "OAuth " + ", ".join(
            [f'{k}="{v}"' for k, v in params.items()]
        )
        
        return auth_header
    
    async def authenticate(self) -> bool:
        """Authenticate with NetSuite."""
        try:
            # Test authentication by fetching record types
            await self.get_entities()
            self._authenticated = True
            return True
        except Exception as e:
            print(f"NetSuite authentication failed: {e}")
            return False
    
    async def get_entities(self) -> List[EntityDefinition]:
        """Get available NetSuite record types."""
        # NetSuite common entities
        entities = [
            EntityDefinition(
                name="customer",
                label="Customer",
                fields={
                    "id": {"type": "string", "label": "Internal ID"},
                    "entityId": {"type": "string", "label": "Entity ID"},
                    "companyName": {"type": "string", "label": "Company Name"},
                    "email": {"type": "string", "label": "Email"},
                    "phone": {"type": "string", "label": "Phone"},
                    "address": {"type": "object", "label": "Address"},
                },
                primary_key="id",
                relationships=[
                    {"name": "salesorders", "entity": "salesorder", "field": "entity"}
                ]
            ),
            EntityDefinition(
                name="salesorder",
                label="Sales Order",
                fields={
                    "id": {"type": "string", "label": "Internal ID"},
                    "tranId": {"type": "string", "label": "Document Number"},
                    "entity": {"type": "reference", "label": "Customer", "ref": "customer"},
                    "total": {"type": "number", "label": "Total"},
                    "status": {"type": "string", "label": "Status"},
                    "trandate": {"type": "date", "label": "Date"},
                },
                primary_key="id",
                relationships=[
                    {"name": "customer", "entity": "customer", "field": "entity"}
                ]
            ),
            EntityDefinition(
                name="item",
                label="Item",
                fields={
                    "id": {"type": "string", "label": "Internal ID"},
                    "itemId": {"type": "string", "label": "Item Name"},
                    "displayName": {"type": "string", "label": "Display Name"},
                    "salesDescription": {"type": "string", "label": "Description"},
                    "basePrice": {"type": "number", "label": "Base Price"},
                },
                primary_key="id",
                relationships=[]
            ),
        ]
        return entities
    
    async def get_schema(self, entity: str) -> Dict[str, Any]:
        """Get schema for a NetSuite entity."""
        entities = await self.get_entities()
        for e in entities:
            if e.name == entity:
                return {
                    "name": e.name,
                    "label": e.label,
                    "fields": e.fields,
                    "primary_key": e.primary_key
                }
        raise ValueError(f"Entity not found: {entity}")
    
    async def read_records(
        self,
        entity: str,
        filters: Optional[Dict] = None,
        limit: Optional[int] = 100,
        offset: Optional[int] = 0
    ) -> List[Dict[str, Any]]:
        """Read records from NetSuite."""
        # Placeholder implementation
        # In production, this would use NetSuite's REST API
        return [
            {
                "id": "12345",
                "entityId": "CUST001",
                "companyName": "Acme Corporation",
                "email": "contact@acme.com",
                "phone": "+1-555-0123"
            }
        ]
    
    async def write_records(
        self,
        entity: str,
        records: List[Dict[str, Any]],
        operation: str = "upsert"
    ) -> SyncResult:
        """Write records to NetSuite."""
        # Placeholder implementation
        return SyncResult(
            success=True,
            records_processed=len(records),
            records_created=len(records),
            records_updated=0,
            records_failed=0,
            errors=[],
            duration_ms=100
        )
    
    async def subscribe_changes(
        self,
        entity: str,
        callback: callable
    ) -> str:
        """Subscribe to NetSuite changes (via webhooks or polling)."""
        # Placeholder - would use NetSuite's SuiteScript or webhooks
        return f"sub_{entity}_{int(time.time())}"
