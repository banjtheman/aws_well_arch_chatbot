import numpy as np
import openai
import pandas as pd
import tiktoken

EMBEDDING_MODEL = "text-embedding-ada-002"

MAX_SECTION_LEN = 1500
SEPARATOR = "\n* "
ENCODING = "cl100k_base"

encoding = tiktoken.get_encoding(ENCODING)
separator_len = len(encoding.encode(SEPARATOR))

# Embedding code


def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> list[float]:
    result = openai.Embedding.create(model=model, input=text)
    return result["data"][0]["embedding"]


def vector_similarity(x: list[float], y: list[float]) -> float:
    """
    Returns the similarity between two vectors.

    Because OpenAI Embeddings are normalized to length 1, the cosine similarity is the same as the dot product.
    """
    return np.dot(np.array(x), np.array(y))


def order_document_sections_by_query_similarity(
    query: str, contexts: dict[(str, str), np.array]
) -> list[(float, (str, str))]:
    """
    Find the query embedding for the supplied query, and compare it against all of the pre-calculated document embeddings
    to find the most relevant sections.

    Return the list of document sections, sorted by relevance in descending order.
    """
    query_embedding = get_embedding(query)

    document_similarities = sorted(
        [
            (vector_similarity(query_embedding, doc_embedding), doc_index)
            for doc_index, doc_embedding in contexts.items()
        ],
        reverse=True,
    )

    return document_similarities


def get_context(question: str, context_embeddings: dict, df: pd.DataFrame) -> str:
    """
    Fetch relevant
    """
    most_relevant_document_sections = order_document_sections_by_query_similarity(
        question, context_embeddings
    )

    chosen_sections = []
    chosen_sections_len = 0
    chosen_sections_indexes = []

    for _, section_index in most_relevant_document_sections:
        # Add contexts until we run out of space.
        print(section_index)
        document_section = df.loc[
            (df["title"] == section_index[0]) & (df["url"] == section_index[1])
        ]

        # Location of values
        num_tokens = document_section.values[0][3]
        curr_text = document_section.values[0][2]

        chosen_sections_len += +num_tokens + separator_len
        if chosen_sections_len > MAX_SECTION_LEN:
            break

        chosen_sections.append(SEPARATOR + curr_text.replace("\n", " "))
        chosen_sections_indexes.append(str(section_index))

    # Useful diagnostic information
    print(f"Selected {len(chosen_sections)} document sections:")
    print("\n".join(chosen_sections_indexes))

    context = "".join(chosen_sections)

    return (
        context,
        chosen_sections_indexes,
    )


def get_answer_from_chatgpt(
    query: str,
    df: pd.DataFrame,
    document_embeddings: dict[(str, str), np.array],
) -> str:
    context, docs = get_context(query, document_embeddings, df)

    #     if show_prompt:
    #         print(prompt)

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are an AWS Certified Solutions Architect. Your role is to help customers understand best practices on building on AWS. Return your response in markdown, so you can bold and highlight important steps for customers. If the answer cannot be found within the  contexnt, write 'I could not find an answer'",
            },
            {
                "role": "system",
                "content": f"Use the following context from the AWS Well-Architected Framework to answer the user's query .\nContext:\n{context}",
            },
            {"role": "user", "content": f"{query}"},
        ],
    )

    answer = response["choices"][0]["message"]["content"].strip(" \n")

    return answer, docs