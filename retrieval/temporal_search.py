from datetime import datetime, timezone

from retrieval.vector_search import semantic_search
from retrieval.metadata_filter import filter_posts


# ---------------------------------------------------------
# Parse ISO Date
# ---------------------------------------------------------

def parse_date(date_string):

    try:

        return datetime.fromisoformat(

            date_string.replace("Z", "+00:00")

        )

    except Exception:

        return None


# ---------------------------------------------------------
# Temporal Search
# ---------------------------------------------------------

def temporal_search(

    query,

    window="7d",

    top_k=5,

    subreddit=None,

    author=None,

    min_score=None,

    min_comments=None,

):

    # -----------------------------------------
    # Retrieve semantic candidates
    # -----------------------------------------

    candidates = semantic_search(

        query,

        top_k=100

    )

    now = datetime.now(timezone.utc)

    temporal_results = []

    # -----------------------------------------
    # Apply Temporal Filter
    # -----------------------------------------

    for score, post in candidates:

        created = parse_date(

            post.get("createdAt", "")

        )

        if created is None:

            continue

        age = (now - created).days

        keep = False

        if window == "7d":

            keep = age <= 7

        elif window == "30d":

            keep = age <= 30

        elif window == "180d":

            keep = age <= 180

        elif window == "all":

            keep = True

        if keep:

            temporal_results.append(

                (score, post)

            )

    # -----------------------------------------
    # Metadata Filtering
    # -----------------------------------------

    filtered_posts = filter_posts(

        [post for _, post in temporal_results],

        subreddit=subreddit,

        author=author,

        time_window=None,

        min_score=min_score,

        min_comments=min_comments

    )

    allowed_ids = {

        post["id"]

        for post in filtered_posts

    }

    final_results = []

    for score, post in temporal_results:

        if post["id"] in allowed_ids:

            final_results.append(

                (score, post)

            )

    return final_results[:top_k]


# ---------------------------------------------------------
# Pretty Print
# ---------------------------------------------------------

def print_results(results):

    print()

    print("=" * 75)

    print("TEMPORAL SEARCH RESULTS")

    print("=" * 75)

    if not results:

        print("\nNo matching posts found.\n")

        return

    for i, (score, post) in enumerate(results, start=1):

        print()

        print(f"{i}. {post['title']}")

        print(f"Similarity   : {score:.3f}")

        print(f"Date         : {post['createdAt']}")

        print(f"Time Window  : {post['time_window']}")

        print(f"Subreddit    : {post['subreddit']}")

        print(f"Author       : {post['author']}")

        print(f"Score        : {post['score']}")

        print(f"Comments     : {post['numComments']}")

        print("-" * 75)


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    results = temporal_search(

        query="LLM inference",

        window="7d",

        subreddit="LocalLLaMA",

        min_score=0,

        min_comments=0,

        top_k=10

    )

    print_results(results)