from locust import HttpUser, task, between

class LearnHubUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def placeholder(self):
        self.client.get("/")