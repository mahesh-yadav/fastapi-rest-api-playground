import time

from locust import HttpUser, between, task


class GuestUser(HttpUser):
    wait_time = between(
        1, 3
    )  # user waits between 1 and 3 seconds after each task is executed

    @task
    def view_rooms(self):
        self.client.get("/rooms")

    @task(weight=2)
    def view_room(self):
        for room_id in range(1, 5):
            self.client.get(f"/rooms/{room_id}", name="/room")
            time.sleep(1)
