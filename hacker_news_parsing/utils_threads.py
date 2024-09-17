# User Whoishiring post a thread every month
# Get all the threads ids from Whoishiring
# https://hacker-news.firebaseio.com/v0/user/whoishiring.json?print=pretty

import json
import os
import asyncio
import httpx

from utils import hn_api_url


async def fetch_thread(client, thread_id):
    response = await client.get(f"{hn_api_url}/item/{thread_id}.json?print=pretty")
    return response.json()


async def fetch_all_threads(thread_ids):
    async with httpx.AsyncClient(timeout=30) as client:
        tasks = [fetch_thread(client, thread_id) for thread_id in thread_ids]
        return await asyncio.gather(*tasks)

def fetch_whoishiring_threads():
    whoishiring = httpx.get(f"{hn_api_url}/user/whoishiring.json?print=pretty")
    whoishiring_data = whoishiring.json()
    threads_ids = whoishiring_data["submitted"]

    thread_data_list = asyncio.run(fetch_all_threads(threads_ids))

    os.makedirs("output", exist_ok=True)

    with open("output/whoishiring_threads.jsonl", "w") as f:
        for thread_data in thread_data_list:
            f.write(json.dumps(thread_data) + "\n")
