import json

from graph.entity_extractor import extract_entities


with open(
    "data/raw/reddit_posts.json",
    "r",
    encoding="utf-8"
) as f:

    posts = json.load(f)


print()

print("=" * 60)
print("ENTITY EXTRACTION")
print("=" * 60)

for post in posts[:5]:

    print()

    print(post["title"])

    print("-" * 60)

    entities = extract_entities(post)

    if entities:

        for entity in entities:

            print("•", entity)

    else:

        print("No entities found.")