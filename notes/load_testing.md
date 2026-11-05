# API Load Testing

Start the API before running either tool, without `--reload` for more realistic numbers:

```bash
uv run fastapi run
```

## Locust

Python-based. Locust is in the dev dependencies, so `uv` manages it.

### Define the test

`load_test.py`:

```python
from locust import HttpUser, task, between


class User(HttpUser):
    wait_time = between(1, 3)  # optional: pause 1-3s between requests

    @task
    def get_rooms(self):
        self.client.get("/rooms")
```

- Each `HttpUser` subclass is a simulated user type, and Locust spawns many instances of it.
- Each `@task` is an action the user repeats. `@task(3)` makes it run 3x as often.
- `self.client` is a `requests` session that records timings and failures.

### Run with the web UI

```bash
uv run locust -f load_test.py --host http://localhost:8000
```

Open http://localhost:8089, set the number of users and spawn rate, then start the test.

### Run headless (scripts / CI)

```bash
uv run locust -f load_test.py --host http://localhost:8000 \
  --headless -u 50 -r 5 -t 1m --csv results
```

- `-u 50`: peak concurrent users
- `-r 5`: users spawned per second
- `-t 1m`: run time
- `--csv results`: writes `results_stats.csv` and related files

### Auth

If the endpoint needs a bearer token, log in once per simulated user. Adjust the path and fields to match the auth routes.

```python
def on_start(self):
    r = self.client.post("/token", data={"username": "u", "password": "p"})
    self.client.headers["Authorization"] = f"Bearer {r.json()['access_token']}"
```

## Grafana k6

JavaScript-based. k6 is a standalone Go binary, so `uv` does not manage it.

### Install

```bash
brew install k6
```

### Define the test

`load_test.js`:

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 50,            // concurrent virtual users
  duration: '1m',     // run time
  thresholds: {
    http_req_failed: ['rate<0.01'],     // under 1% failures
    http_req_duration: ['p(95)<500'],   // p95 under 500ms
  },
};

export default function () {
  const res = http.get('http://localhost:8000/rooms');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(Math.random() * 2 + 1);  // think time of 1-3s
}
```

- The `default` function is what each virtual user runs in a loop.
- `check` records pass/fail counts but does not stop the test.
- `thresholds` are pass/fail criteria for the whole run. k6 exits non-zero if one is breached, which makes it suitable for CI.

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

### Ramping load

Replace `vus` and `duration` with `stages`:

```javascript
export const options = {
  stages: [
    { duration: '30s', target: 20 },  // ramp up 0 -> 20
    { duration: '1m',  target: 50 },  // keep ramping 20 -> 50 but slowly
    { duration: '10s', target: 0 },   // ramp down 50 -> 0
  ],
};
```

### Auth

Log in once in `setup()` and pass the token to the virtual users. Adjust the path and fields to match the auth routes.

```javascript
export function setup() {
  const r = http.post('http://localhost:8000/token', { username: 'u', password: 'p' });
  return { token: r.json('access_token') };
}

export default function (data) {
  http.get('http://localhost:8000/rooms', {
    headers: { Authorization: `Bearer ${data.token}` },
  });
}
```
