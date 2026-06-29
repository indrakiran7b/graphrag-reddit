import os

from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# API Keys
# -----------------------------

APIFY_TOKEN = os.getenv("APIFY_TOKEN")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# -----------------------------
# Reddit
# -----------------------------

MAX_POSTS = 20

SUBREDDITS = [

    "https://www.reddit.com/r/MachineLearning/",

    "https://www.reddit.com/r/LocalLLaMA/",

    "https://www.reddit.com/r/artificial/",

    "https://www.reddit.com/r/technology/",

    "https://www.reddit.com/r/ChatGPT/"

]

# -----------------------------
# Paths
# -----------------------------

RAW_JSON = "data/raw/reddit_posts.json"

GRAPH_FILE = "data/raw/reddit_graph.pkl"

VECTOR_FILE = "data/raw/vector_index.pkl"