import pickle
from collections import defaultdict

from graph.entity_extractor import extract_entities


# ---------------------------------------------------------
# Load Graph
# ---------------------------------------------------------

def load_graph(path="data/raw/reddit_graph.pkl"):

    with open(path, "rb") as f:
        return pickle.load(f)


# ---------------------------------------------------------
# Graph Search
# ---------------------------------------------------------

def graph_search(query, top_k=5):

    graph = load_graph()

    query_entities = extract_entities({
        "title": query,
        "selfText": ""
    })

    print("\nQuery Entities:", query_entities)

    post_scores = defaultdict(float)
    matched_entities = defaultdict(set)
    post_data = {}

    # =====================================================
    # DIRECT ENTITY MATCH
    # =====================================================

    for entity in query_entities:

        if entity not in graph:
            continue

        for post_id in graph.predecessors(entity):

            node = graph.nodes[post_id]

            if node.get("type") != "Post":
                continue

            # Strong weight for exact entity match
            post_scores[post_id] += 10

            matched_entities[post_id].add(entity)

            post = dict(node)
            post["id"] = post_id

            post_data[post_id] = post

    # =====================================================
    # GRAPH EXPANSION
    # =====================================================

    for entity in query_entities:

        if entity not in graph:
            continue

        for related_entity in graph.successors(entity):

            if graph.nodes[related_entity].get("type") != "Entity":
                continue

            edge_data = graph.get_edge_data(entity, related_entity)

            if edge_data is None:
                continue

            relation_found = False
            edge_weight = 1

            for _, attrs in edge_data.items():

                if attrs.get("relation") == "CO_OCCURS":

                    relation_found = True
                    # Ignore weak relationships
                    if edge_weight < 2:
                        continue
                    break

            if not relation_found:
                continue

            for post_id in graph.predecessors(related_entity):

                node = graph.nodes[post_id]

                if node.get("type") != "Post":
                    continue

                # Weighted graph expansion
                post_scores[post_id] += 0.25 * edge_weight

                matched_entities[post_id].add(related_entity)

                post = dict(node)
                post["id"] = post_id

                post_data[post_id] = post

    # =====================================================
    # BONUS FOR MULTIPLE MATCHES
    # =====================================================

    for post_id in matched_entities:

        matches = len(matched_entities[post_id])

        if matches > 1:

            # Stronger bonus for multiple independent matches
            post_scores[post_id] += matches * 2

    # =====================================================
    # SORT
    # =====================================================

    ranked = sorted(
        post_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    results = []

    for post_id, score in ranked[:top_k]:

        results.append({

            "score": round(score, 2),

            "matched_entities": sorted(
                matched_entities[post_id]
            ),

            "post": post_data[post_id]

        })

    return results


# ---------------------------------------------------------
# Pretty Print
# ---------------------------------------------------------

def print_results(results):

    print()

    print("=" * 80)
    print("GRAPH SEARCH RESULTS")
    print("=" * 80)

    if not results:

        print("\nNo results found.\n")
        return

    for i, item in enumerate(results, start=1):

        post = item["post"]

        print()

        print(f"{i}. {post['title']}")

        print(f"Graph Score : {item['score']}")

        print(
            "Matched Entities :",
            ", ".join(item["matched_entities"])
        )

        print(f"Author      : {post['author']}")

        print(f"Subreddit   : {post['subreddit']}")

        print("-" * 80)


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    results = graph_search(

        "LLM inference with PyTorch",

        top_k=10

    )

    print_results(results)