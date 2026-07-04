import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Load a lightweight, high-performance semantic embedding model from HuggingFace
# 'all-MiniLM-L6-v2' maps sentences to a 384-dimensional dense vector space.
_model = None

def get_embeddings_model():
    """
    Singleton function to load and cache the SentenceTransformer model in memory.
    This prevents reloading the heavy model parameters on every function call.
    """
    global _model
    if _model is None:
        # Load the model; this will download it from HuggingFace on the first run
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def calculate_similarity_scores(job_description: str, candidates: list, min_threshold: float = 0.0) -> list:
    """
    Compares a job description with a list of candidates using semantic embeddings
    and FAISS vector indexing.

    Args:
        job_description (str): The text of the job requirements.
        candidates (list): A list of dictionary candidate records containing 'id' and 'resume_text'.
        min_threshold (float, optional): Score threshold (0.0 to 100.0) to filter results.

    Returns:
        list: A list of dicts with keys 'candidate_id', 'semantic_score', ordered by score descending.
    """
    if not candidates or not job_description:
        return []

    # 1. Load the embedding model
    model = get_embeddings_model()

    # 2. Extract resume texts and map to candidate IDs
    resume_texts = [cand["resume_text"] for cand in candidates]
    candidate_ids = [cand["id"] for cand in candidates]

    # 3. Generate embeddings (vectors) for the candidate resumes
    # Convert vectors to float32 NumPy array as required by FAISS
    candidate_embeddings = model.encode(resume_texts, convert_to_numpy=True).astype('float32')

    # 4. Generate embedding for the job description query
    query_embedding = model.encode([job_description], convert_to_numpy=True).astype('float32')

    # 5. Get vector dimensions
    dimension = candidate_embeddings.shape[1]

    # 6. Initialize FAISS index
    # We use IndexFlatIP (Inner Product) which acts as Cosine Similarity
    # if our vectors are normalized. IndexFlatL2 compares Euclidean distance.
    # We will normalize vectors to make inner product exactly equal to Cosine Similarity.
    faiss.normalize_L2(candidate_embeddings)
    faiss.normalize_L2(query_embedding)

    index = faiss.IndexFlatIP(dimension)
    
    # 7. Add candidate vectors to the vector database index
    index.add(candidate_embeddings)

    # 8. Query the index to find the similarity distances
    # k is the number of candidates to search for (we search all of them)
    k = len(candidates)
    scores, indices = index.search(query_embedding, k)

    # 9. Map search results back to candidate records and filter by threshold
    matches = []
    # index.search returns a 2D array, we extract row 0
    for rank in range(k):
        score = float(scores[0][rank])
        idx = int(indices[0][rank])

        # Convert similarity score (from -1.0 to 1.0) into a percentage (from 0% to 100%)
        # Score mapping: percentage = max(0.0, (score * 100))
        percentage_score = round(max(0.0, score * 100), 2)

        if percentage_score >= min_threshold:
            matches.append({
                "candidate_id": candidate_ids[idx],
                "semantic_score": percentage_score
            })

    # Sort matches by score descending
    matches.sort(key=lambda x: x["semantic_score"], reverse=True)

    return matches
