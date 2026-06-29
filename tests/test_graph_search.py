from retrieval.graph_search import graph_search, print_results

results = graph_search(
    "LLM inference",
    top_k=5
)

print_results(results)