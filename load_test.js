import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 50,            // concurrent virtual users (Locust: -u)
  duration: '30s',     // run time (Locust: -t)
  thresholds: {
    http_req_failed: ['rate<0.01'],     // under 1% failures
    http_req_duration: ['p(95)<500'],   // p95 under 500ms
  },
};

export default function () {
  const res = http.get('http://localhost:8000/rooms');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(Math.random() * 2 + 1);  // think time of 1–3s (Locust: wait_time)
}
