# Retrying requests

Python standard library only. Run `python3 -m unittest discover -s tests -v`.
`fetch_with_retry(operation, retries=None)` retries TemporaryError only.
The default is an initial call followed by at most three retries.
Successful results return immediately. Non-transient errors propagate immediately.
