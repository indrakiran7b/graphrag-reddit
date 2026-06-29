from retrieval.temporal_search import temporal_search, print_results

results = temporal_search(

    query="LLM",

    window="7d",

    subreddit="LocalLLaMA",

    top_k=10

)

print_results(results)
