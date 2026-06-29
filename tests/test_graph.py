from graph.graph_builder import load_graph

graph = load_graph()

print()

print("=" * 60)
print("GRAPH SUMMARY")
print("=" * 60)

print()

print("Nodes :", graph.number_of_nodes())

print("Edges :", graph.number_of_edges())

print()

print("=" * 60)
print("SAMPLE RELATIONSHIPS")
print("=" * 60)

print()

count = 0

for u, v, data in graph.edges(data=True):

    print(f"{u} ---{data['relation']}---> {v}")

    count += 1

    if count == 20:
        break