class Context:
    def __init__(self, dry_run=False, user_info=None, env=None, extra_data=None):
        self.dry_run = dry_run
        self.user_info = user_info or {}
        self.env = env or {}
        self.extra_data = extra_data or {}

    def require_confirmation(self, message):
        if self.dry_run:
            print(f"[DRY-RUN] Would prompt: {message}")
            return True
        response = input(f"{message} (y/N): ")
        return response.lower() == "y"
