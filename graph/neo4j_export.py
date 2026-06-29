from neo4j import GraphDatabase

from graph.graph_builder import load_graph
from graph.neo4j_config import (
    NEO4J_URI,
    NEO4J_USER,
    NEO4J_PASSWORD,
)


driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)


def create_node(tx, node_id, properties):

    label = properties.get("type", "Node")

    props = dict(properties)
    props["id"] = str(node_id)

    query = f"""
    MERGE (n:{label} {{id:$id}})
    SET n += $props
    """

    tx.run(
        query,
        id=str(node_id),
        props=props
    )


def create_relationship(tx, source, target, relation, properties):

    query = f"""
    MATCH (a {{id:$source}})
    MATCH (b {{id:$target}})
    MERGE (a)-[r:{relation}]->(b)
    SET r += $props
    """

    tx.run(
        query,
        source=str(source),
        target=str(target),
        props=properties
    )


def export_graph(graph):

    with driver.session() as session:

        print("\nConnected to Neo4j.")

        print("\nUploading nodes...")

        count = 0

        for node_id, props in graph.nodes(data=True):

            session.execute_write(
                create_node,
                node_id,
                props
            )

            count += 1

        print(f"Uploaded {count} nodes.")

        print("\nUploading relationships...")

        count = 0

        for source, target, key, props in graph.edges(
            keys=True,
            data=True
        ):

            relation = props.get("relation", "RELATED_TO")

            rel_props = dict(props)
            rel_props.pop("relation", None)

            session.execute_write(
                create_relationship,
                source,
                target,
                relation,
                rel_props
            )

            count += 1

        print(f"Uploaded {count} relationships.")

    driver.close()

    print("\nDone.")


if __name__ == "__main__":

    print("Loading graph...")

    graph = load_graph()

    export_graph(graph)