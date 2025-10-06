from automation.core.logger import AutomationLogger


def run_tasks(config, context, selected_task: str | None = None):
    """
    Run tasks defined in config. If selected_task is provided, run only that task
    (matched by exact name, case-insensitive).
    """
    log = AutomationLogger()
    tasks = config.get("tasks", [])

    if selected_task:
        sel = selected_task.strip().lower()
        tasks = [t for t in tasks if t.get("name", "").strip().lower() == sel]
        if not tasks:
            log.warning(f"No task matched name: {selected_task}")
            return

    for task in tasks:
        module_name = task["module"]
        params = task.get("params", {})
        # Merge provided params into context for this task
        context.extra_data.update(params)
        try:
            module = __import__(module_name, fromlist=[""])
            func_name = task["name"].lower().replace(" ", "_")
            func = getattr(module, func_name)
            log.info(f"Running task: {task['name']}")
            if context.dry_run:
                log.info(f"Dry-run: would run {task['name']} with params={params}")
                continue
            func(context)
            log.info(f"Completed task: {task['name']}")
        except Exception as e:
            log.error(f"Error running task {task['name']}: {e}")
