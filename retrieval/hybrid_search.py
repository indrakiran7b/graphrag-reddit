import json
from retrieval.graph_search import graph_search
from retrieval.vector_search import semantic_search
from retrieval.graph_search_networkx import graph_search


# ---------------------------------------------------------
# Load Parent Posts
# ---------------------------------------------------------

def load_posts():

    with open(

        "data/raw/reddit_posts.json",

        "r",

        encoding="utf-8"

    ) as f:

        items = json.load(f)

    return {

        item["id"]: item

        for item in items

        if item.get("type") == "post"

    }


# ---------------------------------------------------------
# Enrich Comments
# ---------------------------------------------------------

def enrich_vector_results(vector_results):

    posts = load_posts()

    enriched = []

    for score, doc in vector_results:

        if doc.get("type") == "Comment":

            parent = posts.get(

                doc.get("postId")

            )

            if parent:

                doc["parentPost"] = {

                    "id": parent["id"],

                    "title": parent["title"],

                    "body": parent.get("selfText", ""),

                    "author": parent["author"],

                    "subreddit": parent["subreddit"],

                    "createdAt": parent["createdAt"]

                }

        enriched.append(

            (score, doc)

        )

    return enriched


# ---------------------------------------------------------
# Reciprocal Rank Fusion
# ---------------------------------------------------------

def reciprocal_rank_fusion(
    vector_results,
    graph_results,
    k=60
):

    fused = {}

    # =====================================================
    # VECTOR RESULTS
    # =====================================================

    for rank, (_, doc) in enumerate(vector_results, start=1):

        # -------------------------
        # COMMENT
        # -------------------------

        if doc.get("type") == "Comment":

            parent = doc.get("parentPost")

            if parent:

                post_id = parent["id"]

                if post_id not in fused:

                    fused[post_id] = {

                        "score": 0,

                        "post": {

                            "id": parent["id"],

                            "title": parent["title"],

                            "text": parent["body"],

                            "author": parent["author"],

                            "subreddit": parent["subreddit"],

                            "type": "Post"

                        },

                        "matched_comments": []

                    }

                fused[post_id]["score"] += 1 / (k + rank)

                fused[post_id]["matched_comments"].append(doc)

            continue

        # -------------------------
        # POST
        # -------------------------

        post_id = doc["id"]

        if post_id not in fused:

            fused[post_id] = {

                "score": 0,

                "post": doc,

                "matched_comments": []

            }

        fused[post_id]["score"] += 1 / (k + rank)

    # =====================================================
    # GRAPH RESULTS
    # =====================================================

    for rank, result in enumerate(graph_results, start=1):

        doc = result["post"]

        post_id = doc["id"]

        if post_id not in fused:

            fused[post_id] = {

                "score": 0,

                "post": doc,

                "matched_comments": []

            }

        fused[post_id]["score"] += 1 / (k + rank)

    ranked = sorted(

        fused.values(),

        key=lambda x: x["score"],

        reverse=True

    )

    return ranked


# ---------------------------------------------------------
# Hybrid Search
# ---------------------------------------------------------

def hybrid_search(

    query,

    top_k=5

):

    vector_results = semantic_search(

        query,

        top_k=top_k

    )

    vector_results = enrich_vector_results(

        vector_results

    )

    graph_results = graph_search(

        query,

        top_k=top_k

    )

    return reciprocal_rank_fusion(

        vector_results,

        graph_results

    )[:top_k]


# ---------------------------------------------------------
# Pretty Print
# ---------------------------------------------------------

def print_results(results):

    print()

    print("=" * 70)
    print("HYBRID SEARCH RESULTS")
    print("=" * 70)

    if not results:

        print("No results found.")
        return

    for i, item in enumerate(results, start=1):

        doc = item["post"]

        print()
        print(f"{i}. {doc['title']}")

        print(f"Fusion Score : {item['score']:.4f}")
        print(f"Type         : {doc.get('type', 'Post')}")
        print(f"Author       : {doc.get('author', '')}")
        print(f"Subreddit    : {doc.get('subreddit', '')}")

        # ----------------------------------------
        # Matching Comments
        # ----------------------------------------

        comments = item.get("matched_comments", [])

        if comments:

            print()
            print(f"Relevant Comments ({len(comments)})")
            print("-" * 26)

            for j, comment in enumerate(comments[:3], start=1):

                text = comment.get("text", "").replace("\n", " ").strip()

                if len(text) > 180:
                    text = text[:180] + "..."

                print(f"{j}. {comment.get('author', 'Unknown')}")
                print(f"   {text}")
                print()

        print("-" * 70)

# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    results = hybrid_search(

        "LLM inference",

        top_k=10

    )

    print_results(results)