from google import genai

from config import GEMINI_API_KEY


# ---------------------------------------------------------
# Configure Gemini
# ---------------------------------------------------------

if not GEMINI_API_KEY:

    raise ValueError(
        "GEMINI_API_KEY not found. Please check your .env file."
    )

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ---------------------------------------------------------
# Build Prompt
# ---------------------------------------------------------

def build_prompt(question, retrieved_posts):

    context = ""

    for i, item in enumerate(retrieved_posts, start=1):

        post = item["post"]

        context += f"""
====================================================
POST {i}
====================================================

Title:
{post.get("title", "")}

Author:
{post.get("author", "")}

Subreddit:
{post.get("subreddit", "")}

Content:
{post.get("text", "")}

"""

        # -------------------------------------------------
        # Relevant Comments
        # -------------------------------------------------

        comments = item.get("matched_comments", [])

        if comments:

            context += "\nRelevant Comments\n"

            for j, comment in enumerate(comments[:5], start=1):

                context += f"""

Comment {j}

Author:
{comment.get("author", "")}

Content:
{comment.get("text", "")}

"""

        context += """

----------------------------------------------------
"""

    prompt = f"""
You are an AI assistant that answers questions using Reddit discussions.

You MUST answer ONLY from the Reddit posts and comments provided.

Rules

- Use ONLY the retrieved Reddit context.
- Never invent information.
- Combine evidence from multiple Reddit posts whenever appropriate.
- Use supporting comments to strengthen your answer.
- If users disagree, clearly explain the different viewpoints.
- Mention the subreddit whenever it helps provide context.
- Ignore memes, spam and advertisements.
- If there is not enough evidence, explicitly state that.

Question

{question}


Retrieved Reddit Discussions

{context}


Return your answer in exactly this format:

Summary

Supporting Reddit Discussions

Key Takeaways
"""

    return prompt


# ---------------------------------------------------------
# Ask Gemini
# ---------------------------------------------------------

def ask_gemini(question, retrieved_posts):

    prompt = build_prompt(
        question,
        retrieved_posts
    )

    try:

        response = client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt,

        )

        if hasattr(response, "text") and response.text:

            return response.text

        return "No response generated."

    except Exception as e:

        return f"Gemini Error: {e}"


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    from retrieval.hybrid_search import hybrid_search

    question = "How can I optimize LLM inference?"

    print()
    print("Searching Reddit...\n")

    posts = hybrid_search(

        question,

        top_k=5

    )

    print("Generating answer...\n")

    answer = ask_gemini(

        question,

        posts

    )

    print("=" * 80)
    print("GEMINI ANSWER")
    print("=" * 80)

    print(answer)