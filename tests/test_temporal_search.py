from retrieval.temporal_search import (
    temporal_search,
    print_results,
)

results = temporal_search(
    query="LLM inference",
    window="7d",
    top_k=10,
)

print_results(results)
