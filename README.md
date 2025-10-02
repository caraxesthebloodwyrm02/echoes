# Python Automation Framework (Context-Aware, Safety-Hardened)

## Overview
- Modular, config-driven automation for security, cleanup, maintenance, and monitoring
- Context-aware: every task receives system/user/environment info
- Safety-hardened: dry-run, pre-checks, robust error handling

## Structure
```
automation/
  core/
    context.py
    logger.py
    config.py
    orchestrator.py
  tasks/
    sanitize_codebase.py
    ... (add more tasks)
  scripts/
    run_automation.py
  config/
    automation_config.yaml
  logs/
```

## Usage
### Run a Task
```sh
python automation/scripts/run_automation.py --task-type cleanup --frequency monthly
```
- Use `--dry-run` for safety preview

### Add a Task
- Implement `run(context)` in `automation/tasks/<taskname>.py`
- Register in `automation/config/automation_config.yaml`

## Safety Features
- Dry-run mode for all destructive actions
- Context object for environment/user awareness
- Exception handling and logging
- Configurable via YAML

## Extending
- Add new modules to `tasks/`
- Add new frequencies/types in config
- Use context for custom safety logic

---

**This framework is ready for production automation with proven patterns and hardened safety.**
