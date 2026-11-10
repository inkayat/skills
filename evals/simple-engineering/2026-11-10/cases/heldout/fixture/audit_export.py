"""Export a local audit log for reviewers."""
import argparse
import csv
import json
from pathlib import Path


FIELDS = ("id", "actor", "action")


def _read_events(source):
    events = json.loads(Path(source).read_text(encoding="utf-8"))
    if not isinstance(events, list):
        raise ValueError("source must contain a JSON array")
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("each event must be an object")
        if type(event.get("id")) is not int:
            raise ValueError("event id must be an integer")
        if not all(isinstance(event.get(key), str) for key in ("actor", "action")):
            raise ValueError("event actor and action must be strings")
        if type(event.get("internal", False)) is not bool:
            raise ValueError("event internal must be a boolean")
    return events


def _csv_cell(value):
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + value
    return value


def export_events(source, destination, *, fields=FIELDS, include_internal=False,
                  show_actors=False, limit=None, overwrite=False):
    """Write CSV and return the number of exported events."""
    fields = tuple(fields)
    if not fields or len(set(fields)) != len(fields) or any(f not in FIELDS for f in fields):
        raise ValueError("fields must be distinct names from id, actor, action")
    if limit is not None and (type(limit) is not int or limit < 0):
        raise ValueError("limit must be a nonnegative integer")
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError("source and destination must differ")
    events = _read_events(source)
    rows = []
    for event in events:
        if event.get("internal", False) and not include_internal:
            continue
        if limit is not None and len(rows) >= limit:
            break
        row = {field: event[field] for field in fields}
        if "actor" in row and not show_actors:
            row["actor"] = "[redacted]"
        rows.append(row)
    with destination.open("w" if overwrite else "x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: _csv_cell(value) for key, value in row.items()} for row in rows)
    return len(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument("--fields", default=",".join(FIELDS))
    parser.add_argument("--include-internal", action="store_true")
    parser.add_argument("--show-actors", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    try:
        count = export_events(args.source, args.destination, fields=args.fields.split(","),
                              include_internal=args.include_internal, show_actors=args.show_actors,
                              limit=args.limit, overwrite=args.overwrite)
    except (ValueError, OSError) as error:
        parser.exit(2, f"error: {error}\n")
    print(f"Exported {count} events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
