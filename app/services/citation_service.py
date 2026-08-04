from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.citation import Citation
from app.repositories.citation_repository import CitationRepository
from app.repositories.publication_repository import PublicationRepository
from app.schemas.citation import (
    CitationCreate,
    CitationUpdate,
)

from app.utils.citation_formatter import CitationFormatter
from app.utils.bibtex_exporter import BibTexExporter


class CitationService:

    @staticmethod
    def create_citation(
        db: Session,
        data: CitationCreate,
    ):

        publication = PublicationRepository.get_by_id(
            db,
            data.publication_id,
        )

        if publication is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publication not found",
            )

        citation = Citation(
            **data.model_dump()
        )

        style = data.citation_style.lower()

        if style == "apa":
            citation.formatted_citation = CitationFormatter.apa(citation)

        elif style == "ieee":
            citation.formatted_citation = CitationFormatter.ieee(citation)

        elif style == "mla":
            citation.formatted_citation = CitationFormatter.mla(citation)

        elif style == "chicago":
            citation.formatted_citation = CitationFormatter.chicago(citation)

        elif style == "harvard":
            citation.formatted_citation = CitationFormatter.harvard(citation)

        else:
            citation.formatted_citation = CitationFormatter.apa(citation)

        return CitationRepository.create(
            db,
            citation,
        )

    @staticmethod
    def get_all(
        db: Session,
    ):
        return CitationRepository.get_all(db)

    @staticmethod
    def get(
        db: Session,
        citation_id: UUID,
    ):

        citation = CitationRepository.get_by_id(
            db,
            citation_id,
        )

        if citation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Citation not found",
            )

        return citation

    @staticmethod
    def get_by_publication(
        db: Session,
        publication_id: UUID,
    ):

        publication = PublicationRepository.get_by_id(
            db,
            publication_id,
        )

        if publication is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publication not found",
            )

        return CitationRepository.get_by_publication(
            db,
            publication_id,
        )

    @staticmethod
    def update(
        db: Session,
        citation_id: UUID,
        data: CitationUpdate,
    ):

        citation = CitationRepository.get_by_id(
            db,
            citation_id,
        )

        if citation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Citation not found",
            )

        updates = data.model_dump(
            exclude_unset=True
        )

        for key, value in updates.items():
            setattr(citation, key, value)

        style = citation.citation_style.lower()

        if style == "apa":
            citation.formatted_citation = CitationFormatter.apa(citation)

        elif style == "ieee":
            citation.formatted_citation = CitationFormatter.ieee(citation)

        elif style == "mla":
            citation.formatted_citation = CitationFormatter.mla(citation)

        elif style == "chicago":
            citation.formatted_citation = CitationFormatter.chicago(citation)

        elif style == "harvard":
            citation.formatted_citation = CitationFormatter.harvard(citation)

        else:
            citation.formatted_citation = CitationFormatter.apa(citation)

        db.commit()
        db.refresh(citation)

        return citation

    @staticmethod
    def delete(
        db: Session,
        citation_id: UUID,
    ):

        citation = CitationRepository.get_by_id(
            db,
            citation_id,
        )

        if citation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Citation not found",
            )

        CitationRepository.delete(
            db,
            citation,
        )

        return {
            "message": "Citation deleted successfully"
        }

    @staticmethod
    def export_bibtex(
        db: Session,
        citation_id: UUID,
    ):

        citation = CitationRepository.get_by_id(
            db,
            citation_id,
        )

        if citation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Citation not found",
            )

        return BibTexExporter.export(citation)
