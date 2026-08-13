from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load AI embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_paper_text(paper):
    """
    Combine important research-paper fields
    for semantic comparison.
    """

    title = paper.title or ""
    abstract = paper.abstract or ""
    keywords = paper.keywords or ""

    return f"{title}. {abstract}. {keywords}"


def recommend_papers(
    user_interest: str,
    papers: list,
    top_n: int = 5
):
    """
    Recommend research papers based on
    semantic similarity with user interests.
    """

    if not user_interest or not papers:
        return []

    # Convert user interest into embedding
    interest_embedding = model.encode(
        [user_interest]
    )

    # Prepare paper text
    paper_texts = [
        get_paper_text(paper)
        for paper in papers
    ]

    # Convert papers into embeddings
    paper_embeddings = model.encode(
        paper_texts
    )

    # Calculate similarity
    similarities = cosine_similarity(
        interest_embedding,
        paper_embeddings
    )[0]

    # Attach similarity score
    recommendations = []

    for paper, score in zip(
        papers,
        similarities
    ):

        recommendations.append({
            "paper": paper,
            "similarity": round(
                float(score) * 100,
                2
            )
        })

    # Highest similarity first
    recommendations.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    return recommendations[:top_n]