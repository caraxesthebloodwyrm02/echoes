# app/harmony/cli.py
import argparse
import json
import yaml
from pathlib import Path
from app.harmony.diff_service import diff


def load_file(path: Path):
    text = path.read_text()
    try:
        return json.loads(text)
    except Exception:
        try:
            return yaml.safe_load(text)
        except Exception:
            raise RuntimeError(f"Unsupported file format: {path}")


def main():
    p = argparse.ArgumentParser(prog="harmony-diff")
    p.add_argument("--harmony", required=True, type=Path)
    p.add_argument("--melody", required=True, type=Path)
    p.add_argument("--format", choices=["json", "yaml"], default="json")
    p.add_argument("--epsilon", type=float, default=0.0)
    args = p.parse_args()
    harmony = load_file(args.harmony)
    melody = load_file(args.melody)
    cfg = {"epsilon": args.epsilon}
    out = diff(harmony, melody, cfg)
    if args.format == "json":
        print(json.dumps(out, sort_keys=True, indent=2))
    else:
        print(yaml.safe_dump(out, sort_keys=True))


if __name__ == "__main__":
    main()
