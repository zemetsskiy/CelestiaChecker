import asyncio
import time

import httpx
import json
import requests
from app.logs import logging


class Capsolver:
    def __init__(self, api_key, site_url, site_key, page_action='', min_score=0.9):
        self.api_key = api_key
        self.site_url = site_url
        self.site_key = site_key
        self.page_action = page_action
        self.min_score = min_score

    def create_task(self):
        global resp
        payload = {
            "clientKey": self.api_key,
            "task": {
                "type": "ReCaptchaV3TaskProxyLess",
                "websiteURL": self.site_url,
                "websiteKey": self.site_key,
                "pageAction": "submit",
                "minScore": self.min_score,
            }
        }
        while True:
            try:
                resp = requests.post('https://api.capsolver.com/createTask', json=payload)
                task_id = resp.json()['taskId']
                return task_id
            except Exception as error:
                print(f'ERROR while getting task ID: {error}')

    def get_captcha_solution(self, task_id):
        payload = {
            "clientKey": self.api_key,
            "taskId": task_id
        }
        while True:
            time.sleep(2)
            try:
                resp = requests.post('https://api.capsolver.com/getTaskResult', json=payload)
                status = resp.json()['status']
                if (status == 'ready'):
                    token = resp.json()['solution']['gRecaptchaResponse']
                    return token
            except Exception as error:
                logging.error(f'ERROR getting captcha solution: {error}')


class Checker:
    URL = "https://genesis-api.celestia.org/api/v1/airdrop/eligibility"

    def __init__(self, capsolver):
        self.captcha_solver = capsolver

    async def check(self, wallet):
        while True:
            try:
                task_id = self.captcha_solver.create_task()
                token = self.captcha_solver.get_captcha_solution(task_id)

                async with httpx.AsyncClient(timeout=15) as client:
                    response = await client.get(f"{Checker.URL}/{wallet}?recaptcha_token={token}")
                    slug = response.json()['slug']
                    logging.info(f"{wallet}: {response.status_code} {slug}")
                    
                    if slug == 'recaptcha-verification':
                        continue

                    return "✅" if (slug == 'eligible') else "❌"

            except httpx.ConnectTimeout:
                logging.error("Connection timed out")
                return "Connection timed out"
            except httpx.RequestError as error:
                logging.error(f"An error occurred: {error}")


# if __name__ == "__main__":
#     captcha_solver = Capsolver(API_KEY, SITE_URL, SITE_KEY, page_action='submit')
#     checker = Checker(captcha_solver)
#
#     asyncio.run(checker.check(wallet="0x51ca93591E160d75855B31F7c90f98AEA1F5Cc84"))