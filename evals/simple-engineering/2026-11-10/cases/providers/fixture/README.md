# Workflow planner

Python standard library only. Run `python3 -m unittest discover -s tests -v`.
`python3 planner.py TASK [--config config.json]` prints a plan as JSON.
Config can contain `stages`, a list included unchanged in the plan.
`make_plan(task, config=None)` returns the same plan for Python callers.
Planning has no execution side effects.
