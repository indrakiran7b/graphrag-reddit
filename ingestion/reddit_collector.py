import json
import time
from datetime import datetime

import requests

from config import (
    APIFY_TOKEN,
    RAW_JSON,
    MAX_POSTS,
    SUBREDDITS,
)

from ingestion.time_windows import get_time_windows


BASE_URL = "https://api.apify.com/v2"


# ---------------------------------------------------------
# Assign Time Window
# ---------------------------------------------------------

def assign_time_window(created_at):

    if not created_at:
        return "Unknown"

    try:

        created = datetime.fromisoformat(
            created_at.replace("Z", "+00:00")
        )

    except Exception:

        return "Unknown"

    windows = get_time_windows()

    for name, window in windows.items():

        if window["start"] <= created <= window["end"]:

            return name

    return "Older"


# ---------------------------------------------------------
# Reddit Scraper
# ---------------------------------------------------------

def scrape_reddit(query):

    print("=" * 70)
    print("STARTING REDDIT SCRAPER")
    print("=" * 70)

    run_input = {

        "commentContextMode": False,

        "deduplicatePosts": True,

        "includeComments": False,

        "maxCommentsPerPost": 2,

        "maxPostsPerSource": min(MAX_POSTS, 10),

        "searchQuery": query,

        "urls": SUBREDDITS

    }

    # -----------------------------------------------------
    # Start Apify Actor
    # -----------------------------------------------------

    response = requests.post(

        f"{BASE_URL}/acts/automation-lab~reddit-scraper/runs",

        params={

            "token": APIFY_TOKEN

        },

        json=run_input

    )

    if response.status_code not in (200, 201):
        print("Status Code:", response.status_code)
        print(response.text)
        response.raise_for_status()

    run = response.json()["data"]

    run_id = run["id"]

    print("Run ID :", run_id)

    # -----------------------------------------------------
    # Wait Until Finished
    # -----------------------------------------------------

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

            raise RuntimeError(f"Apify run {status}")

        time.sleep(5)

    # -----------------------------------------------------
    # Download Dataset
    # -----------------------------------------------------

    dataset = requests.get(

        f"{BASE_URL}/datasets/{dataset_id}/items",

        params={

            "token": APIFY_TOKEN

        }

    )

    dataset.raise_for_status()

    posts = dataset.json()

    print()

    print(f"Downloaded {len(posts)} posts")

    # -----------------------------------------------------
    # Enrich Metadata
    # -----------------------------------------------------

    enriched_posts = []

    for post in posts:

        post["time_window"] = assign_time_window(

            post.get("createdAt")

        )

        enriched_posts.append(post)

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    with open(

        RAW_JSON,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            enriched_posts,

            f,

            indent=4,

            ensure_ascii=False

        )

    print()

    print("Saved to")

    print(RAW_JSON)

    # -----------------------------------------------------
    # Statistics
    # -----------------------------------------------------

    print()

    print("=" * 70)
    print("TIME WINDOW SUMMARY")
    print("=" * 70)

    counts = {}

    for post in enriched_posts:

        window = post["time_window"]

        counts[window] = counts.get(window, 0) + 1

    for window, count in sorted(counts.items()):

        print(f"{window:<15}: {count}")

    return enriched_posts


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    posts = scrape_reddit(

        "LLM inference"

    )

    print()

    print("=" * 70)
    print("FIRST POST")
    print("=" * 70)

    print(json.dumps(

        posts[0],

        indent=2,

        ensure_ascii=False

    ))