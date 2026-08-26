"""Explainable, local recommendation helpers for the research portal."""
import re
from collections import Counter

STOP_WORDS = {"a", "an", "and", "are", "as", "at", "by", "for", "from", "in", "into", "is", "of", "on", "or", "the", "to", "with", "using", "based", "research", "study", "analysis", "system"}


def tokens(text: str | None) -> set[str]:
    # Two-character terms such as AI and ML are meaningful in research search.
    return {word for word in re.findall(r"[a-zA-Z][a-zA-Z0-9-]{1,}", (text or "").lower()) if word not in STOP_WORDS}


def keyword_suggestions(title: str | None, abstract: str | None, limit: int = 6) -> list[str]:
    weighted = Counter(tokens(abstract))
    weighted.update({word: 3 for word in tokens(title)})
    return [word.replace("-", " ").title() for word, _ in weighted.most_common(limit)]


def paper_score(query: str, title: str | None, abstract: str | None) -> tuple[int, list[str]]:
    query_words = tokens(query)
    if not query_words:
        return 0, []
    title_words, abstract_words = tokens(title), tokens(abstract)
    # A short search such as "heal" should discover "healthcare".  The
    # matching word is returned so the percentage remains understandable.
    def matching_words(query_terms, document_terms):
        return {document for query_term in query_terms for document in document_terms if document == query_term or document.startswith(query_term)}
    title_hits = matching_words(query_words, title_words)
    abstract_hits = matching_words(query_words, abstract_words)
    coverage = (len(title_hits) * 3 + len(abstract_hits)) / (len(query_words) * 4)
    score = min(99, round(coverage * 100))
    return score, sorted(title_hits | abstract_hits)


def profile_score(source, candidate) -> tuple[int, list[str]]:
    source_skills = tokens(f"{source.skills or ''} {source.research_interest or ''}")
    candidate_skills = tokens(f"{candidate.skills or ''} {candidate.research_interest or ''}")
    shared = source_skills & candidate_skills
    if not source_skills or not candidate_skills:
        return 0, []
    score = round((len(shared) / max(1, len(source_skills | candidate_skills))) * 100)
    if source.institution_id == candidate.institution_id:
        score = min(99, score + 10)
    return score, sorted(shared)
