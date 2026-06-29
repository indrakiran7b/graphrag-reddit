import json
import pickle
from itertools import combinations

import networkx as nx

from graph.entity_extractor import (
    extract_entities,
    ENTITY_TYPES
)


# ---------------------------------------------------------
# Build Knowledge Graph
# ---------------------------------------------------------

def build_graph(posts):

    graph = nx.MultiDiGraph()

    # -------------------------------------------------
    # Split Posts and Comments
    # -------------------------------------------------

    reddit_posts = [

        p for p in posts

        if p.get("type") == "post"

    ]

    reddit_comments = [

        c for c in posts

        if c.get("type") == "comment"

    ]

    # =================================================
    # POSTS
    # =================================================

    for post in reddit_posts:

        post_id = post["id"]

        title = post.get("title", "")
        body = post.get("selfText", "")
        author = post.get("author", "Unknown")
        subreddit = post.get("subreddit", "Unknown")
        timestamp = post.get("createdAt", "")
        date = timestamp[:10]
        score = post.get("score", 0)
        comments = post.get("numComments", 0)
        url = post.get("url", "")

        graph.add_node(

            post_id,

            type="Post",

            title=title,

            text=body,

            body=body,

            timestamp=timestamp,

            score=score,

            comments=comments,

            subreddit=subreddit,

            author=author,

            url=url

        )

        graph.add_node(

            author,

            type="Author"

        )

        graph.add_edge(

            author,

            post_id,

            relation="WRITES"

        )

        graph.add_node(

            subreddit,

            type="Subreddit"

        )

        graph.add_edge(

            post_id,

            subreddit,

            relation="POSTED_IN"

        )

        graph.add_node(

            date,

            type="Date"

        )

        graph.add_edge(

            post_id,

            date,

            relation="POSTED_ON"

        )

        entities = extract_entities(post)

        for entity in entities:

            entity_type = ENTITY_TYPES.get(

                entity,

                "Entity"

            )

            graph.add_node(

                entity,

                type=entity_type

            )

            graph.add_edge(

                post_id,

                entity,

                relation="MENTIONS"

            )

        for e1, e2 in combinations(entities, 2):

            if graph.has_edge(e1, e2):

                edge_data = graph.get_edge_data(e1, e2)

                first_key = next(iter(edge_data))

                edge_data[first_key]["weight"] = (

                    edge_data[first_key].get("weight", 1)

                    + 1

                )

            else:

                graph.add_edge(

                    e1,

                    e2,

                    relation="CO_OCCURS",

                    weight=1

                )

            if graph.has_edge(e2, e1):

                edge_data = graph.get_edge_data(e2, e1)

                first_key = next(iter(edge_data))

                edge_data[first_key]["weight"] = (

                    edge_data[first_key].get("weight", 1)

                    + 1

                )

            else:

                graph.add_edge(

                    e2,

                    e1,

                    relation="CO_OCCURS",

                    weight=1

                )

    # =================================================
    # COMMENTS
    # =================================================

    for comment in reddit_comments:

        comment_id = comment["id"]

        body = comment.get("body", "")

        author = comment.get("author", "Unknown")

        post_id = comment.get("postId")

        timestamp = comment.get("createdAt", "")

        graph.add_node(

            comment_id,

            type="Comment",

            text=body,

            body=body,

            author=author,

            timestamp=timestamp,

            score=comment.get("score", 0)

        )

        graph.add_node(

            author,

            type="Author"

        )

        graph.add_edge(

            author,

            comment_id,

            relation="WRITES"

        )

        if post_id in graph:

            graph.add_edge(

                comment_id,

                post_id,

                relation="COMMENTS_ON"

            )

        entities = extract_entities({

            "title": "",

            "selfText": body

        })

        for entity in entities:

            entity_type = ENTITY_TYPES.get(

                entity,

                "Entity"

            )

            graph.add_node(

                entity,

                type=entity_type

            )

            graph.add_edge(

                comment_id,

                entity,

                relation="MENTIONS"

            )

        for e1, e2 in combinations(entities, 2):

            if graph.has_edge(e1, e2):

                edge_data = graph.get_edge_data(e1, e2)

                first_key = next(iter(edge_data))

                edge_data[first_key]["weight"] = (

                    edge_data[first_key].get("weight", 1)

                    + 1

                )

            else:

                graph.add_edge(

                    e1,

                    e2,

                    relation="CO_OCCURS",

                    weight=1

                )

            if graph.has_edge(e2, e1):

                edge_data = graph.get_edge_data(e2, e1)

                first_key = next(iter(edge_data))

                edge_data[first_key]["weight"] = (

                    edge_data[first_key].get("weight", 1)

                    + 1

                )

            else:

                graph.add_edge(

                    e2,

                    e1,

                    relation="CO_OCCURS",

                    weight=1

                )

    return graph


# ---------------------------------------------------------
# Save Graph
# ---------------------------------------------------------

def save_graph(

    graph,

    path="data/raw/reddit_graph.pkl"

):

    with open(path, "wb") as f:

        pickle.dump(graph, f)

    print(f"\nGraph saved to {path}")


# ---------------------------------------------------------
# Load Graph
# ---------------------------------------------------------

def load_graph(

    path="data/raw/reddit_graph.pkl"

):

    with open(path, "rb") as f:

        return pickle.load(f)


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

def print_graph_summary(graph):

    print()

    print("=" * 70)
    print("GRAPH SUMMARY")
    print("=" * 70)

    print()

    print("Nodes :", graph.number_of_nodes())
    print("Edges :", graph.number_of_edges())

    print()

    node_types = {}

    for _, data in graph.nodes(data=True):

        node_type = data.get("type")

        node_types[node_type] = node_types.get(node_type, 0) + 1

    print("Node Types")
    print("-" * 40)

    for node_type, count in sorted(node_types.items()):

        print(f"{node_type:<12} : {count}")

    print()

    print("Sample Relationships")
    print("-" * 40)

    shown = 0

    for u, v, key, data in graph.edges(keys=True, data=True):

        relation = data.get("relation")

        weight = data.get("weight")

        if weight is None:

            print(f"{u} -- {relation} --> {v}")

        else:

            print(f"{u} -- {relation}({weight}) --> {v}")

        shown += 1

        if shown == 20:
            break


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    with open(

        "data/raw/reddit_posts.json",

        "r",

        encoding="utf-8"

    ) as f:

        posts = json.load(f)

    graph = build_graph(posts)

    print_graph_summary(graph)

    save_graph(graph)