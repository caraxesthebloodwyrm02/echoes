# Local tooling runner (PowerShell)
param(
    [ValidateSet('test','perf','security','types','load','metrics','all')]
    [string]$Task = 'all'
)

switch ($Task) {
  'test'    { pytest tests/unit -v --cov=app --cov=Q4; break }
  'perf'    { python tests/performance/benchmark_suite.py > baseline_metrics.csv; break }
  'security'{ safety check; pip-audit; bandit -r app automation Q4 -ll; break }
  'types'   { mypy app automation Q4 --strict; ruff check .; black --check .; break }
  'load'    { locust -f tests/load/locustfile.py --headless -u 50 -r 10 -t 3m --host http://127.0.0.1:8000; break }
  'metrics' { curl http://127.0.0.1:8000/api/metrics; curl http://127.0.0.1:8000/api/health; break }
  'all'     { pytest tests/unit -v --cov=app --cov=Q4; python tests/performance/benchmark_suite.py > baseline_metrics.csv; safety check; pip-audit; bandit -r app automation Q4 -ll; mypy app automation Q4 --strict; ruff check .; black --check .; break }
}
