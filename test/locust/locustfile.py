#!/usr/bin/env python3

import logging

from locust import HttpUser, SequentialTaskSet, between, events, run_single_user, task
from locust.env import Environment


@events.quitting.add_listener
def on_quit(environment: Environment):
    if environment.stats.total.fail_ratio > 0.01:
        logging.error("Test failed due to failure ratio > 1%")
        environment.process_exit_code = 1
    elif environment.stats.total.avg_response_time > 200:
        logging.error("Test failed due to average response time ratio > 500 ms")
        environment.process_exit_code = 1
    else:
        environment.process_exit_code = 0


class Bot(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        # Just to warmup connection pool.
        self.client.post("/", catch_response=True)

    @task
    class Tasks(SequentialTaskSet):
        captcha_id = ""

        @task
        def generate_captcha(self):
            res = self.client.post("/api/captcha/generate/")
            self.captcha_id = res.headers.get("Captcha-Id")

        @task
        def validate_captcha(self):
            with self.client.post(
                "/api/captcha/validate/",
                json={"id": self.captcha_id, "text": "example"},
                catch_response=True,
            ) as response:
                if response.status_code == 400:
                    response.success()


if __name__ == "__main__":
    run_single_user(Bot)
