import time
import requests

from config import (
    APIFY_TOKEN,
    SUBREDDITS,
)

BASE_URL = "https://api.apify.com/v2"


# ---------------------------------------------------------
# Live Reddit Scraper
# ---------------------------------------------------------

def scrape_live_topic(
    topic,
    limit=10,
):

    if not topic.strip():

        return []

    print()
    print("=" * 70)
    print("LIVE REDDIT SCRAPER")
    print("=" * 70)
    print("Topic :", topic)
    print()

    run_input = {

        "commentContextMode": False,

        "deduplicatePosts": True,

        "includeComments": False,

        "maxCommentsPerPost": 1,

        "maxPostsPerSource": limit,

        "searchQuery": topic,

        "urls": [
            "https://www.reddit.com/r/LocalLLaMA/"
        ]

    }

    response = requests.post(

        f"{BASE_URL}/acts/automation-lab~reddit-scraper/runs",

        params={

            "token": APIFY_TOKEN

        },

        json=run_input

    )

    response.raise_for_status()

    run = response.json()["data"]

    run_id = run["id"]

    print("Run ID :", run_id)

    timeout = 120
    start = time.time()

    while True:

        status_response = requests.get(

            f"{BASE_URL}/actor-runs/{run_id}",

            params={

                "token": APIFY_TOKEN

            }

        )

        status_response.raise_for_status()

        run_data = status_response.json()["data"]

        status = run_data["status"]

        print("Status :", status)

        if status == "SUCCEEDED":

            dataset_id = run_data["defaultDatasetId"]

            break

        if status in (

            "FAILED",

            "TIMED-OUT",

            "ABORTED"

        ):

            return []

        if time.time() - start > timeout:

            print("Request timed out.")

            return []

        time.sleep(3)

    dataset = requests.get(

        f"{BASE_URL}/datasets/{dataset_id}/items",

        params={

            "token": APIFY_TOKEN

        }

    )

    dataset.raise_for_status()

    items = dataset.json()
    import json

    print(json.dumps(items[0], indent=2, ensure_ascii=False))

    posts = []

    for item in items:

        if item.get("type", "").lower() != "post":

            continue

        title = item.get("title", "").lower()

        if item.get("author") == "AutoModerator":

            continue

        if "self-promotion" in title:

            continue

        if "who's hiring" in title:

            continue

        posts.append(item)

    posts.sort(

        key=lambda x: x.get("score", 0),

        reverse=True

    )

    return posts[:limit]


# ---------------------------------------------------------
# Pretty Print
# ---------------------------------------------------------

def print_posts(posts):

    print()

    print("=" * 70)
    print("SCRAPED POSTS")
    print("=" * 70)

    if not posts:

        print("No posts found.")
        return

    for i, post in enumerate(posts, start=1):

        print()

        print(f"{i}. {post.get('title','')}")

        print(f"Author      : {post.get('author','')}")

        print(f"Subreddit   : {post.get('subreddit','')}")

        print(f"Score       : {post.get('score',0)}")

        print(f"Comments    : {post.get('numComments',0)}")

        print(f"URL         : {post.get('url','')}")

        print("-" * 70)


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    topic = input("Enter topic: ").strip()

    limit = input("Number of posts (default 10): ").strip()

    limit = int(limit) if limit else 10

    posts = scrape_live_topic(

        topic,

        limit

    )

    print_posts(posts)
