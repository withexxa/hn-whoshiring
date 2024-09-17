# Get all the comments ids from each thread + the date of the thread
# https://hacker-news.firebaseio.com/v0/item/{thread_id}.json?print=pretty

# Get the content of each comment + the date of the comment
# https://hacker-news.firebaseio.com/v0/item/{comment_id}.json?print=pretty

from datetime import datetime
import json
import os
import asyncio
import httpx

from utils import hn_api_url
from utils_threads import fetch_whoishiring_threads

os.makedirs("output", exist_ok=True)

assert os.path.exists(
    "output/whoishiring_threads.jsonl"
), "Please run fetch_threads.py first"


async def fetch_comment(client, comment_id):
    response = await client.get(f"{hn_api_url}/item/{comment_id}.json?print=pretty")
    return response.json()


async def fetch_comments(comment_ids):
    async with httpx.AsyncClient(timeout=60) as client:
        tasks = [fetch_comment(client, comment_id) for comment_id in comment_ids]
        return await asyncio.gather(*tasks)


async def main():
    with open("output/whoishiring_threads.jsonl", "r") as f:
        for line in f.readlines():
            thread_data = json.loads(line)

            deleted = thread_data.get("deleted", False)
            dead = thread_data.get("dead", False)
            kids = thread_data.get("kids", [])
            title = thread_data.get("title", "")
            hiring = "hiring" in title.lower()

            # We only want to parse the thread if it is not deleted, not dead, has kids and has "hiring" in the title
            # (We want to avoid Who wants to be hired posts)
            if not deleted and not dead and len(kids) > 0 and hiring:
                timestamp = datetime.fromtimestamp(int(thread_data["time"]))

                # Make a directory with the date in YYYY-MM-DD format
                date_dir = "output/" + timestamp.strftime("%Y-%m-%d") + "/" + thread_data["title"].replace(" ", "_")

                os.makedirs(date_dir, exist_ok=True)

                if not os.path.exists(f"{date_dir}/thread.json"):
                    with open(f"{date_dir}/thread.json", "w") as f:
                        json.dump(thread_data, f, indent=4)

                if not os.path.exists(f"{date_dir}/comments.jsonl"):
                    comments_data = await fetch_comments(thread_data["kids"])

                    with open(f"{date_dir}/comments.jsonl", "w") as f:
                        for comment_data in comments_data:
                            f.write(json.dumps(comment_data) + "\n")

if __name__ == "__main__":
    # creates output/whoishiring_threads.jsonl file, containing list of threads
    fetch_whoishiring_threads()
    # get all the post from 
    asyncio.run(main())
