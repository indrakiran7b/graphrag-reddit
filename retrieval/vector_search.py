import json
import pickle

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------
# Load Embedding Model
# ---------------------------------------------------------

print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded.\n")


# ---------------------------------------------------------
# Create Documents
# ---------------------------------------------------------

def create_documents(items):

    documents = []

    for item in items:

        item_type = item.get("type", "").lower()

        # ---------------------------------------
        # Reddit Post
        # ---------------------------------------

        if item_type == "post":

            text = (
                item.get("title", "")
                + "\n"
                + item.get("selfText", "")
            )

            documents.append({

                "id": item["id"],

                "type": "Comment",

                "postId": item.get("postId", ""),

                "postTitle": item.get("postTitle", ""),

                "parentPost": None,

                "title": "[Comment] " + item.get("postTitle", ""),

                "text": text,

                "body": text,

                "author": item.get("author", ""),

                "subreddit": item.get("subreddit", ""),

                "createdAt": item.get("createdAt", ""),

                "time_window": item.get("time_window", ""),

                "score": item.get("score", 0),

                "numComments": 0,

                "url": item.get("permalink", "")

            })

        # ---------------------------------------
        # Reddit Comment
        # ---------------------------------------

        elif item_type == "comment":

            text = item.get("body", "")

            documents.append({

                "id": item["id"],

                "type": "Comment",

                "postId": item.get("postId", ""),

                "postTitle": item.get("postTitle", ""),

                "title": "[Comment] " + item.get("postTitle", ""),

                "text": text,

                "author": item.get("author", ""),

                "subreddit": "",

                "createdAt": item.get("createdAt", ""),

                "time_window": item.get("time_window", ""),

                "score": item.get("score", 0),

                "numComments": 0,

                "url": item.get("permalink", "")

            })

    return documents


# ---------------------------------------------------------
# Build Embeddings
# ---------------------------------------------------------

def build_embeddings(documents):

    corpus = [

        doc["text"]

        for doc in documents

    ]

    embeddings = model.encode(

        corpus,

        convert_to_numpy=True,

        show_progress_bar=True

    )

    return embeddings


# ---------------------------------------------------------
# Save Index
# ---------------------------------------------------------

def save_index(documents, embeddings):

    with open(

        "data/raw/vector_index.pkl",

        "wb"

    ) as f:

        pickle.dump(

            {

                "documents": documents,

                "embeddings": embeddings

            },

            f

        )

    print("Vector index saved.")


# ---------------------------------------------------------
# Load Index
# ---------------------------------------------------------

def load_index():

    with open(

        "data/raw/vector_index.pkl",

        "rb"

    ) as f:

        return pickle.load(f)


# ---------------------------------------------------------
# Semantic Search
# ---------------------------------------------------------

def semantic_search(

    query,

    top_k=5

):

    index = load_index()

    documents = index["documents"]

    embeddings = index["embeddings"]

    query_embedding = model.encode(

        [query],

        convert_to_numpy=True

    )

    similarities = cosine_similarity(

        query_embedding,

        embeddings

    )[0]

    ranked = sorted(

        zip(similarities, documents),

        key=lambda x: x[0],

        reverse=True

    )

    return ranked[:top_k]


# ---------------------------------------------------------
# Pretty Print
# ---------------------------------------------------------

def print_results(results):

    print()

    print("=" * 70)
    print("SEMANTIC SEARCH RESULTS")
    print("=" * 70)

    for i, (score, doc) in enumerate(results, start=1):

        print()

        print(f"{i}. {doc['title']}")

        print(f"Type        : {doc['type']}")

        print(f"Similarity  : {score:.3f}")

        print(f"Author      : {doc['author']}")

        print(f"Date        : {doc['createdAt']}")

        print(f"Time Window : {doc['time_window']}")

        if doc["type"] == "Post":

            print(f"Subreddit   : {doc['subreddit']}")

        else:

            print(f"Post        : {doc['postTitle']}")

        print("-" * 70)


# ---------------------------------------------------------
# Build Index
# ---------------------------------------------------------

if __name__ == "__main__":

    with open(

        "data/raw/reddit_posts.json",

        "r",

        encoding="utf-8"

    ) as f:

        items = json.load(f)

    documents = create_documents(items)

    embeddings = build_embeddings(documents)

    save_index(

        documents,

        embeddings

    )

    print()

    print("Documents :", len(documents))

    print("Embeddings :", embeddings.shape)

    print()

    post_count = sum(

        1

        for d in documents

        if d["type"] == "Post"

    )

    comment_count = sum(

        1

        for d in documents

        if d["type"] == "Comment"

    )

    print("Posts    :", post_count)

    print("Comments :", comment_count)