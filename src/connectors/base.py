"""Base connector for ERP systems."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class SyncMode(Enum):
    """Synchronization modes."""
    FULL = "full"           # Full data sync
    INCREMENTAL = "incremental"  # Only changed records
    REALTIME = "realtime"   # Event-driven


@dataclass
class EntityDefinition:
    """Definition of an ERP entity."""
    name: str
    label: str
    fields: Dict[str, Dict[str, Any]]
    primary_key: str
    relationships: List[Dict[str, str]]


@dataclass
class SyncResult:
    """Result of a sync operation."""
    success: bool
    records_processed: int
    records_created: int
    records_updated: int
    records_failed: int
    errors: List[str]
    duration_ms: int


class ERPConnector(ABC):
    """Abstract base class for ERP connectors."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._authenticated = False
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Connector name."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Connector version."""
        pass
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the ERP system.
        
        Returns:
            True if authentication successful
        """
        pass
    
    @abstractmethod
    async def get_entities(self) -> List[EntityDefinition]:
        """Get list of available entities.
        
        Returns:
            List of entity definitions
        """
        pass
    
    @abstractmethod
    async def get_schema(self, entity: str) -> Dict[str, Any]:
        """Get schema for an entity.
        
        Args:
            entity: Entity name
            
        Returns:
            Schema definition with field types
        """
        pass
    
    @abstractmethod
    async def read_records(
        self,
        entity: str,
        filters: Optional[Dict] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Read records from the ERP.
        
        Args:
            entity: Entity name
            filters: Optional filter criteria
            limit: Maximum records to return
            offset: Pagination offset
            
        Returns:
            List of records
        """
        pass
    
    @abstractmethod
    async def write_records(
        self,
        entity: str,
        records: List[Dict[str, Any]],
        operation: str = "upsert"
    ) -> SyncResult:
        """Write records to the ERP.
        
        Args:
            entity: Entity name
            records: Records to write
            operation: One of "create", "update", "upsert"
            
        Returns:
            Sync result with statistics
        """
        pass
    
    @abstractmethod
    async def subscribe_changes(
        self,
        entity: str,
        callback: Callable[[Dict[str, Any]], None]
    ) -> str:
        """Subscribe to real-time changes.
        
        Args:
            entity: Entity to watch
            callback: Function to call on changes
            
        Returns:
            Subscription ID
        """
        pass
    
    async def unsubscribe_changes(self, subscription_id: str) -> bool:
        """Unsubscribe from changes.
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            True if successful
        """
        pass
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to ERP.
        
        Returns:
            Connection test results
        """
        try:
            await self.authenticate()
            entities = await self.get_entities()
            return {
                "success": True,
                "message": f"Connected successfully. Found {len(entities)} entities.",
                "entities": [e.name for e in entities[:5]]
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
