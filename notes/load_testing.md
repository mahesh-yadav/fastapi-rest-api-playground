# API Load Testing

Start the API before running either tool, without `--reload` for more realistic numbers:

```bash
uv run fastapi run
```

## Locust

Python-based. Locust is in the dev dependencies, so `uv` manages it.

### Run with the web UI

```bash
uv run locust -f <file_name>.py --host http://localhost:8000
```

Open http://localhost:8089, set the number of users and spawn rate, then start the test.

### Run headless (scripts / CI)

```bash
uv run locust -f <file_name>.py --host http://localhost:8000 \
  --headless -u 50 -r 5 -t 1m --csv results
```

- `-u 50`: peak concurrent users
- `-r 5`: users spawned per second
- `-t 1m`: run time
- `--csv results`: writes `results_stats.csv` and related files

### Run from `pyproject.toml` config

Locust reads a `[tool.locust]` table, so the flags above can live in the project instead of the command line:

```toml
[tool.locust]
locustfile = "locust_files/<file_name>.py"
host = "http://localhost:8000"
users = 50
spawn-rate = 5
run-time = "1m"
headless = true
```

Then run it with no flags:

```bash
uv run locust
```

## Grafana k6

JavaScript-based. k6 is a standalone Go binary, so `uv` does not manage it.

### Install

```bash
brew install k6
```
### Run

```bash
k6 run load_test.js
```

The end-of-run summary shows request rate, latency percentiles, failure rate and threshold results.

Optional outputs:

```bash
k6 run --out web-dashboard load_test.js    # live dashboard on :5665
k6 run --out csv=results.csv load_test.js  # export raw metrics
```
