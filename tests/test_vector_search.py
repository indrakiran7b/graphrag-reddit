from retrieval.vector_search import semantic_search

results = semantic_search(

    "LLM inference",

    top_k=5

)

print()

print("=" * 60)

print("SEMANTIC SEARCH RESULTS")

print("=" * 60)

print()

for score, post in results:

    print(f"Score : {score:.3f}")

    print(post["title"])

    print(post["subreddit"])

    print("-" * 60)