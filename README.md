# 🔗 AI-Powered ERP Integration Orchestrator

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent integration platform that connects ERP systems (SAP, NetSuite, Odoo, Business Central) using AI-powered data mapping, event-driven workflows, and natural language integration builders.

## 🌟 Why This Project?

Enterprise ERP integration is one of the most expensive and error-prone aspects of IT operations. This project demonstrates how AI can dramatically simplify and automate these complex integrations.

## 🚀 Key Features

### 🤖 AI-Powered Schema Mapping
- **Intelligent Field Mapping**: AI automatically maps fields between different ERP systems
- **Few-Shot Learning**: Learns from examples to improve mapping accuracy over time
- **Conflict Detection**: Identifies and flags potential data conflicts before sync

### 🔄 Event-Driven Architecture
- **Change Data Capture**: Real-time sync when data changes
- **Saga Pattern**: Distributed transactions with rollback capability
- **Event Sourcing**: Complete audit trail of all changes

### 📝 Natural Language Integration Builder
- **Describe, Don't Code**: Business users describe integration flows in plain English
- **AI Code Generation**: Platform generates the orchestration code
- **Visual Workflow Editor**: Drag-and-drop interface for technical refinement

### 🔐 Enterprise Security
- **PII Detection**: Automatic detection and redaction of sensitive data
- **Audit Logging**: Complete lineage tracking for compliance
- **Role-Based Access**: Granular permissions for integration management

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Natural    │  │  Workflow   │  │    Integration          │  │
│  │  Language   │  │  Management │  │    Management           │  │
│  │  Builder    │  │  API        │  │    API                  │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
└─────────┼────────────────┼─────────────────────┼────────────────┘
          │                │                     │
          └────────────────┴─────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                  Workflow Orchestration (Temporal)               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Schema    │  │   Data      │  │    Conflict             │  │
│  │   Mapping   │  │   Transform │  │    Resolution           │  │
│  │   Engine    │  │   Engine    │  │    Engine               │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼────────┐  ┌──────▼────────┐  ┌──────▼────────┐
│    ERP         │  │    Message    │  │     AI        │
│  Connectors    │  │     Queue     │  │   Services    │
├────────────────┤  ├────────────────┤  ├────────────────┤
│ • SAP          │  │ • Apache      │  │ • OpenAI      │
│ • NetSuite     │  │   Kafka       │  │ • Anthropic   │
│ • Odoo         │  │ • RabbitMQ    │  │ • Embedding   │
│ • Business     │  │ • Redis       │  │   Models      │
│   Central      │  │   Streams     │  │               │
└────────────────┘  └────────────────┘  └────────────────┘
```

## 📦 Supported ERP Systems

| ERP System | Read | Write | Real-time Sync |
|------------|------|-------|----------------|
| SAP S/4HANA | ✅ | ✅ | ✅ |
| Oracle NetSuite | ✅ | ✅ | ✅ |
| Odoo | ✅ | ✅ | ✅ |
| Microsoft Business Central | ✅ | ✅ | ✅ |
| Salesforce | ✅ | ✅ | ⚠️ Polling |
| HubSpot | ✅ | ✅ | ⚠️ Polling |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- OpenAI API key

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/ai-erp-integrator.git
cd ai-erp-integrator

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Start infrastructure
docker-compose up -d kafka postgres temporal

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start the application
python -m src.main
```

## 📖 Usage Examples

### 1. Natural Language Integration

```python
from src.api.nlp_builder import create_integration_from_description

# Describe your integration in plain English
integration = await create_integration_from_description(
    description="""
    Sync customer orders from Shopify to NetSuite.
    When an order is created in Shopify, create a sales order in NetSuite.
    Map Shopify order ID to NetSuite external ID.
    If the customer doesn't exist in NetSuite, create them first.
    """,
    source_system="shopify",
    target_system="netsuite"
)

print(f"Integration created: {integration.id}")
```

### 2. AI-Powered Schema Mapping

```python
from src.ai.schema_mapper import SchemaMapper

mapper = SchemaMapper()

# Source and target schemas
source_schema = {
    "customer_id": "string",
    "full_name": "string",
    "email_address": "string",
    "phone": "string"
}

target_schema = {
    "cust_id": "string",
    "name": "string",
    "email": "string",
    "phone_number": "string"
}

# AI generates the mapping
mapping = await mapper.generate_mapping(
    source_schema=source_schema,
    target_schema=target_schema,
    source_name="Shopify",
    target_name="NetSuite"
)

print(mapping)
# {
#     "customer_id": "cust_id",
#     "full_name": "name",
#     "email_address": "email",
#     "phone": "phone_number"
# }
```

### 3. Event-Driven Sync

```python
from src.workflows.sync_workflow import SyncWorkflow
from temporalio.client import Client

# Start a sync workflow
temporal_client = await Client.connect("localhost:7233")

result = await temporal_client.execute_workflow(
    SyncWorkflow.run,
    {
        "source": {"system": "shopify", "entity": "orders"},
        "target": {"system": "netsuite", "entity": "salesorders"},
        "trigger": "webhook",
        "mapping_id": "map_123"
    },
    id="sync-order-456",
    task_queue="erp-sync"
)
```

## 🔌 Connector Development

Create custom ERP connectors:

```python
from src.connectors.base import ERPConnector

class CustomERPConnector(ERPConnector):
    """Custom ERP connector implementation."""
    
    async def authenticate(self):
        # Implement authentication
        pass
    
    async def get_entities(self):
        # List available entities
        pass
    
    async def read_records(self, entity, filters=None):
        # Read records from ERP
        pass
    
    async def write_records(self, entity, records):
        # Write records to ERP
        pass
    
    async def subscribe_changes(self, entity, callback):
        # Subscribe to real-time changes
        pass
```

## 🧪 Testing

```bash
# Unit tests
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# Run with coverage
pytest --cov=src --cov-report=html
```

## 📊 Performance

| Metric | Value |
|--------|-------|
| Sync throughput | 1,000+ records/minute |
| AI mapping latency | < 2 seconds |
| Workflow execution | 99.9% reliability |
| Event latency | < 100ms |

## 🔐 Security Features

- ✅ OAuth 2.0 / OIDC authentication
- ✅ API key management with rotation
- ✅ PII detection and redaction
- ✅ End-to-end encryption for sensitive data
- ✅ Complete audit logging
- ✅ Rate limiting and throttling

## 🛣️ Roadmap

- [ ] Additional ERP connectors (Workday, SAP ByDesign)
- [ ] GraphQL API gateway
- [ ] Webhook management portal
- [ ] Custom transformation functions
- [ ] ML-based anomaly detection
- [ ] Data quality scoring

## 👤 Author

**Pham Thach Son (Kent) Nguyen**
- Solutions Architect | AI & Systems Integration
- LinkedIn: [linkedin.com/in/kentnguyen93](https://linkedin.com/in/kentnguyen93)

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details.

---

⭐ Star this repo if you find it helpful!
