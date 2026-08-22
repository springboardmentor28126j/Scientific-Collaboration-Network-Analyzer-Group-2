import io
import uuid

import httpx
import fitz
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.publication import PublicationStatus
from app.models.publication_chunk import PublicationChunk
from app.repositories.publication_chunk_repository import (
    PublicationChunkRepository,
)
from app.repositories.publication_repository import PublicationRepository


class PublicationIndexingService:
    def __init__(self, session: AsyncSession):
        self.session = session

        self.publications = PublicationRepository(session)
        self.chunks = PublicationChunkRepository(session)

    async def extract_and_store_chunks(
        self,
        publication_id: uuid.UUID,
    ) -> int:

        publication = await self.publications.get_by_id(
            publication_id,
        )

        if publication is None:
            raise NotFoundError("Publication not found.")

        if publication.status not in (
            PublicationStatus.PUBLISHED,
            PublicationStatus.ARCHIVED,
        ):
            raise ConflictError("Only published or archived publications can be indexed.")

        if not publication.pdf_url:
            raise ConflictError("Publication does not have a PDF.")

        async with httpx.AsyncClient(
            timeout=60.0,
            follow_redirects=True,
        ) as client:
            response = await client.get(
                publication.pdf_url,
            )

        response.raise_for_status()

        pdf = fitz.open(
            stream=io.BytesIO(response.content),
            filetype="pdf",
        )

        await self.chunks.delete_by_publication(
            publication.id,
        )

        chunks: list[PublicationChunk] = []

        chunk_index = 0

        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()

            if not text:
                continue

            # Temporary simple chunking.
            page_chunks = self._chunk_text(text)

            for content in page_chunks:
                chunks.append(
                    PublicationChunk(
                        publication_id=publication.id,
                        page_number=page_number,
                        chunk_index=chunk_index,
                        content=content,
                    )
                )

                chunk_index += 1

        pdf.close()

        await self.chunks.create_many(chunks)

        await self.session.commit()

        return len(chunks)

    @staticmethod
    def _chunk_text(
        text: str,
        chunk_size: int = 1500,
        overlap: int = 200,
    ) -> list[str]:

        chunks = []

        start = 0

        while start < len(text):
            end = start + chunk_size

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start += chunk_size - overlap

        return chunks
