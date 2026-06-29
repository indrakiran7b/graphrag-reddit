from collections import defaultdict
import re

from neo4j import GraphDatabase

from graph.entity_extractor import extract_entities
from graph.neo4j_config import (
    NEO4J_URI,
    NEO4J_USER,
    NEO4J_PASSWORD,
)

# ---------------------------------------------------------
# Neo4j Connection
# ---------------------------------------------------------

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD),
)

# ---------------------------------------------------------
# Cypher Queries
# ---------------------------------------------------------

DIRECT_QUERY = """
MATCH (p:Post)-[:MENTIONS]->(e)
WHERE e.id = $entity
RETURN p
"""

FULLTEXT_QUERY = """
CALL db.index.fulltext.queryNodes(
    'postIndex',
    $keyword
)
YIELD node, score

RETURN
    node AS p,
    score

LIMIT 20
"""

EXPANSION_QUERY = """
MATCH (e {id:$entity})-[r:CO_OCCURS]->(x)

WHERE r.weight >= 2

MATCH (p:Post)-[:MENTIONS]->(x)

RETURN
    p,
    x.id AS related_entity,
    r.weight AS weight

ORDER BY r.weight DESC

LIMIT 15
"""

# ---------------------------------------------------------
# Keyword Extraction
# ---------------------------------------------------------

STOPWORDS = {
    "the",
    "is",
    "are",
    "what",
    "how",
    "why",
    "can",
    "could",
    "should",
    "would",
    "i",
    "a",
    "an",
    "of",
    "for",
    "to",
    "on",
    "in",
    "at",
    "using",
    "use",
    "with",
    "and",
    "or",
    "from",
}


def extract_keywords(query):

    words = re.findall(
        r"[a-zA-Z0-9_]+",
        query.lower(),
    )

    return [
        w
        for w in words
        if len(w) > 2
        and w not in STOPWORDS
    ]


# ---------------------------------------------------------
# Graph Search
# ---------------------------------------------------------

def graph_search(query, top_k=5):

    query_entities = extract_entities(
        {
            "title": query,
            "selfText": "",
        }
    )

    query_keywords = [

    k

    for k in extract_keywords(query)

    if k.upper() not in {

        e.upper()

        for e in query_entities

    }

]

    print()

    print("Query Entities :", query_entities)

    print("Keywords       :", query_keywords)

    post_scores = defaultdict(float)

    matched_entities = defaultdict(set)

    post_data = {}

    with driver.session() as session:

        # -------------------------------------------------
        # 1. Direct Entity Search
        # -------------------------------------------------

        for entity in query_entities:

            records = session.run(
                DIRECT_QUERY,
                entity=entity,
            )

            for record in records:

                node = record["p"]

                props = dict(node)

                post_id = props["id"]

                props["id"] = post_id

                post_data[post_id] = props

                post_scores[post_id] += 5

                matched_entities[post_id].add(entity)
                        
        # -------------------------------------------------
        # 2. Full-text Search
        # -------------------------------------------------

        for keyword in query_keywords:

            records = session.run(
                FULLTEXT_QUERY,
                keyword=keyword,
            )
            
            for record in records:

                node = record["p"]

                props = dict(node)

                post_id = props["id"]

                props["id"] = post_id

                post_data[post_id] = props

                neo4j_score = record["score"]

                post_scores[post_id] += neo4j_score * 2

                matched_entities[post_id].add(keyword)

        # -------------------------------------------------
        # 3. Graph Expansion
        # -------------------------------------------------

        for entity in query_entities:

            records = session.run(
                EXPANSION_QUERY,
                entity=entity,
            )

            for record in records:

                node = record["p"]

                props = dict(node)

                post_id = props["id"]

                props["id"] = post_id

                post_data[post_id] = props

                related_entity = record[
                    "related_entity"
                ]

                weight = min(
                    record["weight"] or 1,
                    5,
                )

                post_scores[post_id] += (
                    weight * 0.2
                )

                matched_entities[post_id].add(
                    related_entity
                )

        # -------------------------------------------------
        # 4. Multi-Entity Bonus
        # -------------------------------------------------

        for post_id, entities in matched_entities.items():

            # Small bonus for matching multiple
            # entities/keywords
            post_scores[post_id] += min(
                len(entities),
                5
            )

    # -------------------------------------------------
    # Ranking
    # -------------------------------------------------

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
    print("NEO4J GRAPH SEARCH")
    print("=" * 80)

    if not results:

        print("\nNo results found.\n")
        return

    for i, item in enumerate(
        results,
        start=1
    ):

        post = item["post"]

        print()

        print(f"{i}. {post.get('title','')}")

        print(
            f"Score      : {item['score']}"
        )

        print(
            f"Author     : {post.get('author','Unknown')}"
        )

        print(
            f"Subreddit  : {post.get('subreddit','Unknown')}"
        )

        entities = item.get(
            "matched_entities",
            []
        )

        if entities:

            print(
                "Matches    : "
                + ", ".join(entities)
            )

        print("-" * 80)


# ---------------------------------------------------------
# Close Driver
# ---------------------------------------------------------

def close():

    driver.close()


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    query = "LLM inference"

    results = graph_search(

        query=query,

        top_k=10

    )

    print_results(results)

    close()