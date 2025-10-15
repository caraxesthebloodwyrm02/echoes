# Solar - Renewable Energy utilities

This folder contains research artifacts and lightweight tools for working with
the Solar Energy Research and Innovation Plan. Key files:

- `solar_energy_research_plan.md` - human-readable research plan and roadmap.
- `solar_module.py` - small Python helpers to parse the plan, compute inspiration vectors, and export summaries as JSON.
- `solar_microgrid_tool.py` - prototype microgrid simulation and optimizer.
- `solar_ai_improvements.py` - experimental AI-driven integration helpers.
- `solar_salesman_tools.py` - tools for solar sales workflow (mapping, timing, pitching, convincing).
- `solar_datastore.py` - integration with JSON-based datastore for knowledge graph simulation.
- `test_solar_module.py` - unit tests for modules.
- `solar_summary.json` - example exported JSON summary.

## Usage Examples

### Parse and Print Summary
```bash
py SCIENCE/renewable_energy/solar_module.py print
```

### Export JSON Summary
```bash
py SCIENCE/renewable_energy/solar_module.py export --output_file summary.json
# Customize: --add_field "custom_field:value"
```

### Integrate with Datastore
```bash
py SCIENCE/renewable_energy/solar_datastore.py --json_file summary.json
```

### Run Unit Tests
```bash
py -m pytest SCIENCE/renewable_energy/test_solar_module.py
```

### Salesman Tools
See `solar_salesman_tools.py` for homework/realtime sales tools.

The utilities are intentionally minimal to be safe for CI and unit tests.
