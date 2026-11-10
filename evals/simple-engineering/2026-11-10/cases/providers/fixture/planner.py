import argparse
import json

def make_plan(task, config=None):
    config = config or {}
    return {"task": task, "assistant": "claude", "stages": config.get("stages", ["build", "review"])}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task")
    parser.add_argument("--config")
    args = parser.parse_args()
    config = {}
    if args.config:
        with open(args.config) as stream:
            config = json.load(stream)
    print(json.dumps(make_plan(args.task, config)))

if __name__ == "__main__":
    main()
