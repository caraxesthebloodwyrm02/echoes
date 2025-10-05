# Educational Ecosystem Data Directory

This directory contains all data files for the Educational Ecosystem application.

## Directory Structure

### `data/`
Root data directory containing ecosystem data and logs.

### `data/ecosystem/`
**Core ecosystem data** - Main application data
- `stakeholders.json` - User/stakeholder database with roles, contact info, and participation tracking
- `zones.json` - Zone configurations including capacity, features, and furniture
- `workshops.json` - Co-creation workshop data and outcomes
- `transparency_log.json` - System activity log for accountability

### `data/ecosystem/memory.json`
**Knowledge Graph Memory** - Persistent contextual memory
- Entity-relationship knowledge graph for AI memory
- Stores user preferences, interactions, and contextual information
- MCP-compatible format for integration with AI assistants

### `data/creative_corner/`
**Creative Corner module data**
- `users.json` - Creative corner user management with access levels and certifications
- `equipment.json` - Equipment inventory and status tracking
- `access_log.json` - Access history and usage tracking

### `data/logs/`
**Session logs** - User interaction logs
- `session_YYYYMMDD.json` - Daily session logs with check-in data

### `data/test/`
**Test data** - Files used for testing purposes
- Test session logs and sample data

## Data Flow

1. **User Registration** → `stakeholders.json`
2. **Check-in Sessions** → `logs/session_*.json` + `transparency_log.json`
3. **Zone Configuration** → `zones.json`
4. **Workshop Management** → `workshops.json`
5. **Creative Corner Usage** → `creative_corner/*.json`
6. **Memory & Context** → `ecosystem/memory.json` (Knowledge Graph)
7. **Analytics Processing** → `ecosystem/analytics/*.json`

## Maintenance Notes

- Session logs are rotated daily
- Test data should be cleaned periodically
- Stakeholder data includes privacy considerations
- Zone configurations support expansion planning

## File Formats

All files use JSON format for easy parsing and human readability. Timestamps follow ISO 8601 format.
