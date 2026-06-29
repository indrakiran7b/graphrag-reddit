import re
import spacy

print("Loading spaCy model...")

nlp = spacy.load("en_core_web_sm")

print("spaCy model loaded.\n")


# ---------------------------------------------------------
# Allowed spaCy Entity Types
# ---------------------------------------------------------

ALLOWED_LABELS = {
    "ORG",
    "PERSON",
    "PRODUCT",
    "GPE",
    "LOC",
    "EVENT",
}


# ---------------------------------------------------------
# AI Terms
# ---------------------------------------------------------

AI_TERMS = {

    # Models
    "LLM",
    "GPT",
    "ChatGPT",
    "Claude",
    "Gemini",
    "Llama",
    "Gemma",
    "Mistral",
    "Qwen",
    "Whisper",
    "NLLB",

    # Frameworks
    "LangChain",
    "LlamaIndex",
    "PyTorch",
    "TensorFlow",
    "Transformers",
    "ONNX",

    # Databases
    "Neo4j",
    "Milvus",
    "FAISS",
    "Chroma",

    # Companies
    "OpenAI",
    "Anthropic",
    "Google",
    "Microsoft",
    "Meta",
    "NVIDIA",

    # Technologies
    "CUDA",
    "GPU",
    "API",
    "RAG",
    "GraphRAG",
    "Spark",
    "PySpark",
    "Databricks",

}
ENTITY_TYPES = {

    # Models
    "LLM": "Model",
    "GPT": "Model",
    "ChatGPT": "Model",
    "Claude": "Model",
    "Gemini": "Model",
    "Llama": "Model",
    "Gemma": "Model",
    "Mistral": "Model",
    "Qwen": "Model",
    "Whisper": "Model",
    "NLLB": "Model",

    # Frameworks
    "LangChain": "Framework",
    "LlamaIndex": "Framework",
    "PyTorch": "Framework",
    "TensorFlow": "Framework",
    "Transformers": "Framework",

    # Vector Databases
    "Neo4j": "Database",
    "FAISS": "Database",
    "Milvus": "Database",
    "Chroma": "Database",

    # Companies
    "OpenAI": "Company",
    "Anthropic": "Company",
    "Google": "Company",
    "Microsoft": "Company",
    "Meta": "Company",
    "NVIDIA": "Company",

    # Technologies
    "CUDA": "Technology",
    "GPU": "Hardware",
    "API": "Technology",
    "RAG": "Technique",
    "GraphRAG": "Technique",
    "Spark": "Framework",
    "PySpark": "Framework",
    "Databricks": "Platform",

}


# ---------------------------------------------------------
# Blacklist
# ---------------------------------------------------------

BLACKLIST = {

    "Thread",
    "Discussion",
    "Question",
    "Repository",
    "Repo",
    "Post",
    "Posts",
    "Comment",
    "Comments",
    "submitted",
    "Job",
    "Jobs",
    "Job Postings",
    "Hiring",
    "Monthly",
    "Weekly",

}


NOISE_PREFIX = (

    "Technical",
    "Handling",
    "Architecture",
    "Models",
    "Questions",

)


USERNAME = re.compile(r"^/?u/")
URL = re.compile(r"https?://")
NUMBER = re.compile(r"^\d+$")


# ---------------------------------------------------------
# Normalize
# ---------------------------------------------------------

def normalize(entity):

    entity = entity.strip()

    entity = re.sub(r"\s+", " ", entity)

    entity = entity.strip("[](){}.,:; ")

    replacements = {

        "LLMs": "LLM",
        "LLMs": "LLM",
        "GPUs": "GPU",
        "APIs": "API",

    }

    for old, new in replacements.items():

        entity = entity.replace(old, new)

    return entity


# ---------------------------------------------------------
# Validate
# ---------------------------------------------------------

def is_valid(entity):

    if len(entity) < 3:
        return False

    if len(entity) > 35:
        return False

    if entity in BLACKLIST:
        return False

    if USERNAME.search(entity):
        return False

    if URL.search(entity):
        return False

    if NUMBER.match(entity):
        return False

    if any(entity.startswith(x) for x in NOISE_PREFIX):
        return False

    if len(entity.split()) > 3:
        return False

    if re.search(r"[\[\]{}()<>]", entity):
        return False

    if re.search(r"[=:;]", entity):
        return False

    if re.search(r"\d{4,}", entity):
        return False

    if re.search(r"[\\/]", entity):
        return False

    if entity.islower():
        return False

    return True


# ---------------------------------------------------------
# Extract
# ---------------------------------------------------------

def extract_entities(post):

    text = (
        post.get("title", "")
        + "\n"
        + post.get("selfText", "")
    )

    doc = nlp(text)

    entities = set()

    # -----------------------------
    # spaCy
    # -----------------------------

    for ent in doc.ents:

        if ent.label_ not in ALLOWED_LABELS:
            continue

        entity = normalize(ent.text)

        if not is_valid(entity):
            continue

        entities.add(entity)

    # -----------------------------
    # AI Dictionary
    # -----------------------------

    lower = text.lower()

    for keyword in AI_TERMS:

        pattern = r"\b" + re.escape(keyword.lower()) + r"s?\b"

        if re.search(pattern, lower):

            entities.add(keyword)

    return sorted(entities)


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    sample = {

        "title": "Building an LLM inference pipeline with PyTorch and LangChain",

        "selfText": """
        We are using Whisper,
        OpenAI APIs,
        Neo4j,
        CUDA GPUs.
        """

    }

    print(extract_entities(sample))