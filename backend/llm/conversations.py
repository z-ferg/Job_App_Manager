from openai import OpenAI
from typing import List

import os
import math

# Modify OpenAI's API key and API base to use the server.
openai_api_key = os.getenv('ARC_API_KEY')
openai_api_base = "https://llm-api.arc.vt.edu/api/v1"

SYSTEM_PROMPT = {
    "role":     "system",
    "content":  "You are a helpful assistant."
}

""" ARC LLM API Documentation is found here:
    https://www.docs.arc.vt.edu/ai/011_llm_api_arc_vt_edu.html
"""

# ====================================================================== #
#  ARC LLM Helpers                                                       #
# ====================================================================== #

def arc_llm():
    return OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_base,
    )

def llm_chat(client, messages):
    return client.chat.completions.create(
        model="gpt-oss-120b",
        messages= [SYSTEM_PROMPT] + messages,
    )

# ====================================================================== #
#  LLM-Interactive Functions                                             #
# ====================================================================== #

""" Very rudimentary function for taking a prompt and asking the LLM
    Example Args:
        prompt = "Tell me about Virginia Tech?"
"""
def chat_func(prompt: str) -> str:
    message = [{"role": "user", "content": prompt}]
    return llm_chat(arc_llm(), message).choices[0].message.content


""" Given a list of document titles, will use LLM to match query to relevant data
    Example Args:
        docs = ['Map of Virginia', 'Chemistry 101', 'Introduction to Economics']
        query = "Where is Virginia Tech located?"
        task = "Given a question, retrieve passages that answer it"
        limit = 1 (Use -1 for entire list)
"""
def semantic_search(docs: List[str], query: str, task: str, limit: int = -1) -> str:
    client = arc_llm()
    
    def embed(texts):
        response = client.embeddings.create(model="Qwen3-Embedding-4B", input=texts)
        return [item.embedding for item in response.data]

    def cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))
    
    doc_vectors = embed(docs)
    query_vector = embed([f"Instruct: {task}\nQuery: {query}"])[0]
    
    scores = [cosine(query_vector, v) for v in doc_vectors]
    sorted_docs = [doc for _, doc in sorted(zip(scores, docs), reverse=True)]
    return sorted_docs[limit - 1] if limit != -1 else sorted_docs


if __name__ == "__main__":
    print(chat_func("Tell me joke"), "\n\n")
    
    print(semantic_search(
        docs  = ['Map of Virginia', 'Chemistry 101', 'Introduction to Economics'],
        query = "What is the first element of the periodic table?",
        task  = "Given a question, retrieve passages that answer it"
    ))