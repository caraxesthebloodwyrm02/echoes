# ATLAS - Advanced Inventory and Media Management System

## Overview

ATLAS is a comprehensive, modular inventory and media management system that evolved from the Echoes codebase organizer. It provides a complete solution for inventory tracking, media discovery, and AI-powered workflows with both programmatic and command-line interfaces.

## Architecture

ATLAS consists of multiple integrated subsystems:

### 1. Core Inventory Management
- **Models**: Data structures for inventory items with timezone-aware timestamps
- **Storage**: JSON-backed persistence with atomic writes
- **Service Layer**: Business logic for CRUD operations and reporting
- **CLI**: Command-line interface for inventory management
- **API**: Programmatic interface for integrations

### 2. Media Discovery System
- **Find Engine**: Advanced search for movies and TV series in JSON databases
- **Media Models**: Structured data models for film and television content
- **Multi-format Support**: Handles various media metadata formats

### 3. Echoes AI Integration
- **Full AI System**: Complete Echoes assistant implementation
- **Workflow Engine**: Business process automation
- **Multi-agent Architecture**: Advanced AI agent orchestration
- **Knowledge Graph**: Semantic relationships and context management

---

## Core Inventory System

### Data Model

```python
@dataclass
class InventoryItem:
    sku: str                    # Unique stock keeping unit
    name: str                   # Item name
    category: str              # Item category
    quantity: int              # Current stock level
    location: str              # Storage location
    min_stock: int = 0         # Minimum stock threshold
    max_stock: int = 0         # Maximum stock threshold
    created_at: str = ""       # UTC ISO timestamp
    updated_at: str = ""       # UTC ISO timestamp
    attributes: Optional[Dict[str, Any]] = None  # Custom attributes
```

### Storage Layer

**Features:**
- JSON file-based storage at `data/atlas_inventory.json`
- Atomic writes using temporary files
- Automatic directory creation
- Error-resilient loading

**Implementation:**
```python
class InventoryStorage:
    def load(self) -> Dict[str, Any]: ...
    def save(self, data: Dict[str, Any]) -> None: ...
```

### Service Layer

**Core Operations:**
- `add_item()`: Add new inventory items with validation
- `list_items()`: Query items by category/location
- `get_item()`: Retrieve specific items by SKU
- `adjust_quantity()`: Modify stock levels
- `move_item()`: Change item locations
- `report()`: Generate inventory reports

**Business Logic:**
- SKU uniqueness validation
- Quantity never drops below zero
- Automatic timestamp updates
- Category and location filtering

### Command Line Interface

**Available Commands:**

```bash
# Item Management
python -m ATLAS add --sku SKU-001 --name "Item Name" --category Electronics --qty 50 --loc A1 --min 5 --max 100
python -m ATLAS list [--category CATEGORY] [--location LOCATION]
python -m ATLAS adjust --sku SKU-001 --delta -5
python -m ATLAS move --sku SKU-001 --to B2

# Reporting
python -m ATLAS report --type summary    # Overview statistics
python -m ATLAS report --type low        # Low stock alerts
python -m ATLAS report --type over       # Overstock warnings
```

### Programmatic API

**Direct API Interface:**

```python
from ATLAS import ATLASDirectAPI

api = ATLASDirectAPI()

# Item operations
api.add_item(sku="SKU-001", name="Widget", category="Parts", quantity=100, location="A1")
api.adjust_quantity("SKU-001", delta=-10)
api.move_item("SKU-001", new_location="B1")

# Queries
items = api.list_items(category="Parts")
item = api.get_item("SKU-001")

# Reports
summary = api.report_summary()
low_stock = api.report_low_stock()
overstock = api.report_overstock()
```

---

## Media Discovery System

### Media Models

**Base Media Item:**
```python
@dataclass
class MediaItem:
    title: str
    rank: int          # Position in source file
    file: str          # Source JSON file path
    year: str = 'N/A'
    director: str = 'Unknown'
    type: str = 'Movie'
```

**Specialized Types:**
- `Movie`: Film-specific metadata
- `TVSeries`: Television series with seasons/episodes/network info

### Search Engine

**Features:**
- Recursive JSON file scanning
- Case-insensitive title matching
- Multi-format metadata support
- Error-resilient parsing

**Usage:**
```python
from ATLAS.find import find_media, print_media_info

# Search for media
result = find_media("Game of Thrones", "/path/to/media/database")
if result:
    print_media_info(result)
    # Output: Title, Rank, File, Director, Year, Seasons, Episodes, Network, Status
```

---

## Echoes AI Integration

### Architecture Overview

The `ATLAS/echoes/` directory contains a complete Echoes AI assistant implementation with:

**Core Components:**
- `agents.py`: Multi-agent orchestration system
- `workflows.py`: Business process automation
- `cluster.py`: Distributed processing
- `middleware.py`: Request/response processing
- `routes/`: API endpoint definitions

**Key Features:**
- **Knowledge Graph**: Semantic relationship management
- **Parallel Simulations**: Possibility exploration
- **Context Management**: Conversation state tracking
- **Legal Safeguards**: Compliance and accounting
- **Multimodal Processing**: Cross-format content analysis

### Integration Points

**With Inventory System:**
- Automated stock level monitoring
- Predictive reordering workflows
- Category classification assistance
- Report generation and analysis

**With Media System:**
- Content discovery and recommendations
- Metadata enrichment
- Cross-reference analysis

---

## Installation & Setup

### Requirements
- Python 3.11+
- Standard library only (no external dependencies for core features)
- Optional: aiohttp for external API integration

### Installation
```bash
# Clone or navigate to project root
cd e:\Projects\Echoes

# ATLAS is part of the project structure
# No separate installation required
```

### Configuration
- Data directory: `data/` (auto-created)
- Inventory file: `data/atlas_inventory.json`
- Media search paths: Configurable in find.py

---

## Usage Examples

### Basic Inventory Management

```python
from ATLAS import InventoryService

# Initialize service
svc = InventoryService()

# Add items
svc.add_item("MOUSE-001", "Wireless Mouse", "Peripherals", 50, "A1", min_stock=5)
svc.add_item("CABLE-001", "USB-C Cable", "Accessories", 100, "B2", min_stock=10)

# Query inventory
peripherals = svc.list_items(category="Peripherals")
mouse = svc.get_item("MOUSE-001")

# Stock operations
svc.adjust_quantity("MOUSE-001", delta=-5)  # Sold 5 units
svc.move_item("CABLE-001", "C3")           # Relocate item

# Generate reports
summary = svc.report("summary")
low_stock = svc.report("low")
```

### Media Discovery

```python
from ATLAS.find import find_media

# Search for content
movie = find_media("Inception", "/path/to/media/db")
tv_show = find_media("Breaking Bad", "/path/to/media/db")

if movie:
    print(f"Found: {movie.title} ({movie.year}) by {movie.director}")

if tv_show and hasattr(tv_show, 'seasons'):
    print(f"Series: {tv_show.title}, {tv_show.seasons} seasons on {tv_show.network}")
```

### Advanced Workflows

```python
# Using Echoes integration for intelligent inventory management
from ATLAS.echoes.workflows import InventoryWorkflow

workflow = InventoryWorkflow()

# Automated reordering based on AI analysis
recommendations = workflow.analyze_reorder_needs()
workflow.generate_purchase_orders(recommendations)

# Predictive analytics
forecast = workflow.predict_demand_patterns()
alerts = workflow.monitor_stock_levels()
```

---

## API Reference

### InventoryService Class

#### Methods

**Item Management:**
- `add_item(sku, name, category, quantity, location, min_stock=0, max_stock=0, attributes=None)` → `InventoryItem`
- `get_item(sku)` → `InventoryItem | None`
- `list_items(category=None, location=None)` → `List[InventoryItem]`

**Stock Operations:**
- `adjust_quantity(sku, delta)` → `InventoryItem`
- `move_item(sku, new_location)` → `InventoryItem`

**Reporting:**
- `report(type="summary")` → `Dict[str, Any]`
  - `"summary"`: Total items, quantities, stock levels by category
  - `"low"`: Items below minimum stock threshold
  - `"over"`: Items above maximum stock threshold

### ATLASDirectAPI Class

#### Methods

**CRUD Operations:**
- `add_item(...)` → `Dict[str, Any]`
- `get_item(sku)` → `Dict[str, Any]`
- `list_items(category=None, location=None)` → `Dict[str, Any]`

**Batch Operations:**
- `bulk_add_items(items)` → `Dict[str, Any]`
- `bulk_adjust_quantities(adjustments)` → `Dict[str, Any]`

**Advanced Reporting:**
- `report_by_category()` → `Dict[str, Any]`
- `report_by_location()` → `Dict[str, Any]`
- `get_statistics()` → `Dict[str, Any]`

### Media Search API

**Functions:**
- `find_media(title, search_dir)` → `MediaItem | None`
- `print_media_info(media_item)` → `None`

---

## Data Formats

### Inventory JSON Structure
```json
{
  "SKU-001": {
    "sku": "SKU-001",
    "name": "Wireless Mouse",
    "category": "Peripherals",
    "quantity": 45,
    "location": "A1",
    "min_stock": 5,
    "max_stock": 100,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:22:15Z",
    "attributes": {
      "supplier": "TechCorp",
      "warranty": "2 years"
    }
  }
}
```

### Media JSON Structure
```json
[
  {
    "title": "Inception",
    "year": "2010",
    "director": "Christopher Nolan",
    "type": "Movie"
  },
  {
    "title": "Game of Thrones",
    "year": "2011-2019",
    "network": "HBO",
    "seasons": "8",
    "episodes": "73",
    "status": "Ended",
    "type": "TV"
  }
]
```

---

## Error Handling

### Inventory Operations
- **ValueError**: SKU already exists, item not found
- **Validation**: Quantity cannot be negative
- **File I/O**: Graceful fallback on storage errors

### Media Search
- **JSONDecodeError**: Malformed JSON files
- **PermissionError**: Access denied to files/directories
- **FileNotFoundError**: Search directory doesn't exist

### Echoes Integration
- **NetworkError**: External API communication failures
- **TimeoutError**: Long-running operations
- **ValidationError**: Invalid workflow configurations

---

## Testing

### Unit Tests
```bash
# Test inventory operations
python -c "
from ATLAS.service import InventoryService
svc = InventoryService()
item = svc.add_item('TEST-001', 'Test Item', 'Test', 10, 'A1')
print('✓ Add operation successful')
assert item.quantity == 10
print('✓ Quantity validation passed')
"
```

### Integration Tests
```bash
# Test full CLI workflow
python -m ATLAS add --sku TEST-001 --name "Test Item" --category Test --qty 10 --loc A1
python -m ATLAS list --category Test
python -m ATLAS adjust --sku TEST-001 --delta -5
python -m ATLAS report --type summary
```

### Media Search Tests
```bash
# Test media discovery
python ATLAS/find.py  # Runs example search for "Game of Thrones"
```

---

## Performance Characteristics

### Inventory Operations
- **Add Item**: O(1) - Direct dictionary insertion
- **Query Operations**: O(n) - Linear scan of items
- **Storage I/O**: Atomic writes prevent corruption
- **Memory Usage**: Minimal - JSON-based storage

### Media Search
- **Search Time**: O(m × f) where m = files, f = items per file
- **Memory**: Low - Stream processing of JSON files
- **Scalability**: Efficient for large media databases

### Echoes Integration
- **Parallel Processing**: Configurable worker pools
- **Memory Management**: Chunked processing for large datasets
- **API Limits**: Built-in rate limiting and retry logic

---

## Security Considerations

### Data Protection
- **Atomic Writes**: Prevent data corruption during updates
- **Access Control**: File system permissions apply
- **Input Validation**: SKU uniqueness and data type checking

### API Security
- **Input Sanitization**: All external inputs validated
- **Error Handling**: No sensitive information in error messages
- **Rate Limiting**: Configurable request throttling

---

## Future Enhancements

### Planned Features
1. **Database Integration**: PostgreSQL/MySQL support
2. **REST API**: FastAPI-based web service
3. **Barcode Integration**: QR code support for inventory
4. **Dashboard UI**: Web-based inventory management
5. **Mobile App**: React Native inventory client
6. **IoT Integration**: Sensor-based stock monitoring
7. **Analytics**: Advanced reporting and forecasting
8. **Multi-tenancy**: Organization-based access control

### Integration Opportunities
- **E-commerce**: Automated inventory sync
- **ERP Systems**: Bidirectional data flow
- **IoT Sensors**: Real-time stock monitoring
- **AI/ML**: Demand prediction and optimization
- **Blockchain**: Immutable audit trails

---

## Troubleshooting

### Common Issues

**"SKU already exists"**
- Each SKU must be unique
- Check existing items: `python -m ATLAS list`

**"Item not found"**
- Verify SKU spelling
- Use `list` command to see available items

**Permission errors**
- Ensure write access to `data/` directory
- Check file system permissions

**JSON corruption**
- System uses atomic writes to prevent corruption
- Manual recovery: Backup and recreate data file

### Debug Mode
```bash
# Enable verbose logging
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
# Run operations...
"
```

---

## Contributing

### Code Style
- **PEP 8** compliance
- **Type hints** for all function parameters
- **Docstrings** for all public methods
- **Descriptive variable names**

### Testing Requirements
- **Unit tests** for all new functions
- **Integration tests** for CLI and API
- **Edge case coverage** for error conditions
- **Performance benchmarks** for critical paths

### Documentation
- **README updates** for new features
- **Code comments** for complex logic
- **API examples** for integration points
- **Migration guides** for breaking changes

---

## License

Copyright (c) 2024 Echoes AI

This project is part of the Echoes AI ecosystem and follows the project's licensing terms.

---

## Support

For support and questions:
- **Documentation**: This README and inline code documentation
- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for general questions
- **Code Examples**: Refer to the usage examples above

---

*Last updated: November 2025*
*Version: 1.0.0*
*Maintainer: Echoes AI Team*
