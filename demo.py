"""
demo.py

End-to-end demonstration of the Reddit Hybrid GraphRAG pipeline.

This script demonstrates:

1. Semantic Search
2. Graph Search
3. Hybrid Search
4. Temporal Search
5. Gemini Answer Generation
"""

from retrieval.vector_search import semantic_search, print_results as print_vector
from retrieval.graph_search import graph_search, print_results as print_graph
from retrieval.hybrid_search import hybrid_search, print_results as print_hybrid
from retrieval.temporal_search import temporal_search, print_results as print_temporal
from llm.gemini_client import ask_gemini


def separator(title):

    print()
    print("=" * 100)
    print(title)
    print("=" * 100)
    print()


def demo_semantic():

    separator("1. SEMANTIC SEARCH")

    query = "What is Qwen 3?"

    print("Query:", query)

    results = semantic_search(
        query,
        top_k=5
    )

    print_vector(results)

    return results


def demo_graph():

    separator("2. GRAPH SEARCH")

    query = "LLM inference"

    print("Query:", query)

    results = graph_search(
        query,
        top_k=5
    )

    print_graph(results)

    return results


def demo_hybrid():

    separator("3. HYBRID SEARCH")

    query = "Best way to optimize LLM inference"

    print("Query:", query)

    results = hybrid_search(
        query,
        top_k=5
    )

    print_hybrid(results)

    print()

    print("=" * 80)
    print("GEMINI ANSWER")
    print("=" * 80)
    print()

    answer = ask_gemini(
        query,
        results
    )

    print(answer)

    return results


def demo_temporal():

    separator("4. TEMPORAL SEARCH")

    query = "LLM"

    print("Query :", query)
    print("Window: Last7Days")

    results = temporal_search(
        query=query,

        window="7d",

        top_k=5

    )

    print_temporal(results)

    print()

    print("=" * 80)
    print("GEMINI ANSWER")
    print("=" * 80)
    print()

    answer = ask_gemini(

        query,

        [

            {

                "post": post

            }

            for _, post in results

        ]

    )

    print(answer)

    return results


def main():

    separator("HYBRID GRAPHRAG DEMO")

    demo_semantic()

    demo_graph()

    demo_hybrid()

    demo_temporal()

    print()

    print("=" * 100)
    print("DEMO COMPLETED SUCCESSFULLY")
    print("=" * 100)


if __name__ == "__main__":

    main()