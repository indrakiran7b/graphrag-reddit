import gradio as gr

from retrieval.vector_search import semantic_search
from retrieval.graph_search import graph_search
from retrieval.hybrid_search import hybrid_search
from retrieval.temporal_search import temporal_search

from ingestion.live_scraper import scrape_live_topic

from llm.gemini_client import ask_gemini


# ---------------------------------------------------------
# Format Search Results
# ---------------------------------------------------------

def format_results(results, search_type):

    if not results:

        return "No results found."

    output = ""

    # -----------------------------------------------------
    # Semantic Search
    # -----------------------------------------------------

    if search_type == "Semantic":

        for i, (score, doc) in enumerate(results, start=1):

            output += f"""
### {i}. {doc['title']}

Type: {doc['type']}

Similarity: {score:.3f}

Author: {doc['author']}

Subreddit: {doc['subreddit']}

Date: {doc['createdAt']}

------------------------------------------------------------

"""

    # -----------------------------------------------------
    # Graph Search
    # -----------------------------------------------------

    elif search_type == "Graph":

        for i, item in enumerate(results, start=1):

            post = item["post"]

            output += f"""
### {i}. {post['title']}

Score: {item['score']}

Author: {post.get("author","")}

Subreddit: {post.get("subreddit","")}

Matched:
{", ".join(item.get("matched_entities", []))}

------------------------------------------------------------

"""

    # -----------------------------------------------------
    # Hybrid Search
    # -----------------------------------------------------

    elif search_type == "Hybrid":

        for i, item in enumerate(results, start=1):

            post = item["post"]

            output += f"""
### {i}. {post['title']}

Fusion Score: {item['score']:.4f}

Author: {post.get("author","")}

Subreddit: {post.get("subreddit","")}

"""

            comments = item.get(
                "matched_comments",
                []
            )

            if comments:

                output += "\nRelevant Comments\n\n"

                for comment in comments[:3]:

                    text = comment["text"].replace("\n", " ")

                    if len(text) > 180:

                        text = text[:180] + "..."

                    output += (
                        f"- {comment['author']}: "
                        f"{text}\n"
                    )

            output += """

------------------------------------------------------------

"""

    # -----------------------------------------------------
    # Temporal Search
    # -----------------------------------------------------

    else:

        for i, (score, post) in enumerate(results, start=1):

            output += f"""
### {i}. {post['title']}

Similarity: {score:.3f}

Date: {post['createdAt']}

Window: {post['time_window']}

Author: {post['author']}

Subreddit: {post['subreddit']}

------------------------------------------------------------

"""

    return output


# ---------------------------------------------------------
# Format Live Scraper Results
# ---------------------------------------------------------

def format_scraped_posts(posts):

    if not posts:

        return "No posts found."

    output = ""

    for i, post in enumerate(posts, start=1):

        output += f"""
### {i}. {post.get('title', 'No Title')}

**Author:** {post.get('author', 'Unknown')}

**Subreddit:** {post.get('subreddit', 'Unknown')}

**Score:** {post.get('score', 0)}

**Comments:** {post.get('numComments', 0)}

**Created:** {post.get('createdAt', '')}

**URL:** {post.get('url', '')}

------------------------------------------------------------

"""

    return output

# ---------------------------------------------------------
# Search Function
# ---------------------------------------------------------

def search(

    query,

    search_type,

    window,

    top_k

):

    if not query.strip():

        return "", "Please enter a query."

    # -----------------------------------------------------
    # Semantic Search
    # -----------------------------------------------------

    if search_type == "Semantic":

        results = semantic_search(

            query,

            top_k=int(top_k)

        )

        gemini_input = [

            {

                "post": doc

            }

            for _, doc in results

        ]

    # -----------------------------------------------------
    # Graph Search
    # -----------------------------------------------------

    elif search_type == "Graph":

        results = graph_search(

            query,

            top_k=int(top_k)

        )

        gemini_input = results

    # -----------------------------------------------------
    # Hybrid Search
    # -----------------------------------------------------

    elif search_type == "Hybrid":

        results = hybrid_search(

            query,

            top_k=int(top_k)

        )

        gemini_input = results

    # -----------------------------------------------------
    # Temporal Search
    # -----------------------------------------------------

    else:

        results = temporal_search(

            query=query,

            window=window,

            top_k=int(top_k)

        )

        gemini_input = [

            {

                "post": post

            }

            for _, post in results

        ]

    formatted_results = format_results(

        results,

        search_type

    )

    answer = ask_gemini(

        query,

        gemini_input

    )

    return (

        formatted_results,

        answer

    )


# ---------------------------------------------------------
# Live Reddit Scraper
# ---------------------------------------------------------

def live_scrape(

    topic,

    limit

):

    if not topic.strip():

        return "Please enter a topic."

    posts = scrape_live_topic(

        topic=topic,

        limit=int(limit)

    )

    return format_scraped_posts(posts)


# ---------------------------------------------------------
# Theme
# ---------------------------------------------------------

TITLE = """
# 🚀 Reddit Hybrid GraphRAG

Semantic Search • Graph Search • Hybrid Search • Temporal Search

🆕 Live Reddit Topic Scraper

Powered by Neo4j + Sentence Transformers + Gemini 2.5 Flash
"""


# ---------------------------------------------------------
# Gradio Interface
# ---------------------------------------------------------

with gr.Blocks(

    title="Reddit Hybrid GraphRAG"

) as demo:

    gr.Markdown(TITLE)

    with gr.Tabs():
        
                # -------------------------------------------------
        # Search Tab
        # -------------------------------------------------

        with gr.Tab("Search"):

            with gr.Row():

                query = gr.Textbox(

                    label="Query",

                    placeholder="Ask a question about Reddit discussions..."

                )

            with gr.Row():

                search_type = gr.Dropdown(

                    choices=[

                        "Hybrid",

                        "Semantic",

                        "Graph",

                        "Temporal"

                    ],

                    value="Hybrid",

                    label="Search Type"

                )

                window = gr.Dropdown(

                    choices=[

                        "7d",

                        "30d",

                        "180d",

                        "all"

                    ],

                    value="7d",

                    label="Temporal Window"

                )

                top_k = gr.Slider(

                    minimum=1,

                    maximum=10,

                    value=5,

                    step=1,

                    label="Top K"

                )

            search_button = gr.Button(

                "Search",

                variant="primary"

            )

            gr.Markdown("## Retrieved Results")

            results_box = gr.Markdown()

            gr.Markdown("## Gemini Answer")

            answer_box = gr.Markdown()

            search_button.click(

                fn=search,

                inputs=[

                    query,

                    search_type,

                    window,

                    top_k

                ],

                outputs=[

                    results_box,

                    answer_box

                ]

            )

        # -------------------------------------------------
        # Live Reddit Scraper Tab
        # -------------------------------------------------

        with gr.Tab("Live Reddit Scraper"):

            topic = gr.Textbox(

                label="Topic",

                placeholder="Example: LLM inference"

            )

            limit = gr.Slider(

                minimum=1,

                maximum=20,

                value=10,

                step=1,

                label="Number of Posts"

            )

            scrape_button = gr.Button(

                "Scrape Reddit",

                variant="primary"

            )

            gr.Markdown("## Scraped Reddit Posts")

            scraped_posts = gr.Markdown()

            scrape_button.click(

                fn=live_scrape,

                inputs=[

                    topic,

                    limit

                ],

                outputs=scraped_posts

            )
            
            # ---------------------------------------------------------
# Launch
# ---------------------------------------------------------

if __name__ == "__main__":

    demo.launch(

        server_name="127.0.0.1",

        server_port=7860,

        share=False,

        debug=True

    )