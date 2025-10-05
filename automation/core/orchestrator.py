from automation.core.logger import AutomationLogger


def run_tasks(config, context):
    log = AutomationLogger()
    tasks = config.get("tasks", [])
    for task in tasks:
        module_name = task["module"]
        params = task.get("params", {})
        context.extra_data.update(params)
        try:
            module = __import__(module_name, fromlist=[""])
            func_name = task["name"].lower().replace(" ", "_")
            func = getattr(module, func_name)
            log.info(f"Running task: {task['name']}")
            if not context.dry_run:
                func(context)
            else:
                log.info(f"Dry-run: would run {task['name']}")
        except Exception as e:
            log.error(f"Error running task {task['name']}: {e}")
