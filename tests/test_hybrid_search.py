from retrieval.hybrid_search import hybrid_search, print_results

results = hybrid_search(

    "LLM inference",

    top_k=5

)

print_results(results)