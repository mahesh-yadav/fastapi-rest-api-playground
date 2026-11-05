import time

from locust import HttpUser, between, task


class GuestUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def view_rooms(self):
        self.client.get("/rooms")

    @task(weight=2)
    def view_room(self):
        for room_id in range(1, 5):
            self.client.get(f"/rooms/{room_id}", name="/room")
            time.sleep(1)
