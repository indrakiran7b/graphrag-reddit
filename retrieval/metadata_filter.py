# ---------------------------------------------------------
# Metadata Filter
# ---------------------------------------------------------

def filter_posts(

    posts,

    subreddit=None,

    author=None,

    time_window=None,

    min_score=None,

    min_comments=None,

):

    filtered = []

    for post in posts:

        if subreddit is not None:

            if post.get("subreddit", "").lower() != subreddit.lower():

                continue

        if author is not None:

            if post.get("author", "").lower() != author.lower():

                continue

        if time_window is not None:

            if post.get("time_window") != time_window:

                continue

        if min_score is not None:

            if post.get("score", 0) < min_score:

                continue

        if min_comments is not None:

            if post.get("numComments", 0) < min_comments:

                continue

        filtered.append(post)

    return filtered