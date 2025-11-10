"""Generate requirements.txt from pyproject.toml"""
import tomllib

with open("pyproject.toml", "rb") as f:
    config = tomllib.load(f)

# Generate requirements.txt from main dependencies
deps = config["project"]["dependencies"]
with open("requirements.txt", "w") as f:
    f.write("# Auto-generated from pyproject.toml\n")
    f.write("# DO NOT EDIT - Use pyproject.toml as source of truth\n\n")
    for dep in deps:
        f.write(f"{dep}\n")

print(f"Generated requirements.txt with {len(deps)} dependencies")

# Generate requirements-dev.txt from optional dependencies
if (
    "optional-dependencies" in config["project"]
    and "dev" in config["project"]["optional-dependencies"]
):
    dev_deps = config["project"]["optional-dependencies"]["dev"]
    with open("requirements-dev.txt", "w") as f:
        f.write(
            "# Auto-generated from pyproject.toml [project.optional-dependencies.dev]\n"
        )
        f.write("# DO NOT EDIT - Use pyproject.toml as source of truth\n\n")
        for dep in dev_deps:
            f.write(f"{dep}\n")
    print(f"Generated requirements-dev.txt with {len(dev_deps)} dev dependencies")
