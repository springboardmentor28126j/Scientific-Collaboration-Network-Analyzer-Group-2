
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_recommendations(search_text, publications):

    if not publications:
        return []

    titles = [
        publication.title
        for publication in publications
        if publication.title
    ]

    if not titles:
        return []

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    title_vectors = vectorizer.fit_transform(titles)

    search_vector = vectorizer.transform(
        [search_text]
    )

    similarities = cosine_similarity(
        search_vector,
        title_vectors
    )[0]

    results = []

    valid_publications = [
        publication
        for publication in publications
        if publication.title
    ]

    for publication, similarity in zip(
        valid_publications,
        similarities
    ):

        percentage = round(
            similarity * 100,
            2
        )

        if percentage > 0:

            results.append({
                "id": publication.id,
                "researcher_id": publication.researcher_id,
                "title": publication.title,
                "publication_type": publication.publication_type,
                "publication_year": publication.publication_year,
                "match_percentage": percentage
            })

    results.sort(
        key=lambda x: x["match_percentage"],
        reverse=True
    )

    return results[:10]
