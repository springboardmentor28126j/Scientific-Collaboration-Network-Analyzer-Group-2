from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publication import PublicationStatus
from app.models.user import User, UserRole
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import (
    PublicationStatusStats,
    SuperAdminDashboard,
    InstitutionDashboard,
    ResearcherDashboard,
    ReviewerDashboard,
)


class DashboardService:
    def __init__(self, session: AsyncSession):
        self.repository = DashboardRepository(session)

    def _build_status_stats(
        self,
        counts: dict[PublicationStatus, int],
    ) -> PublicationStatusStats:
        return PublicationStatusStats(
            draft=counts[PublicationStatus.DRAFT],
            submitted=counts[PublicationStatus.SUBMITTED],
            under_review=counts[PublicationStatus.UNDER_REVIEW],
            revision_required=counts[PublicationStatus.REVISION_REQUIRED],
            accepted=counts[PublicationStatus.ACCEPTED],
            rejected=counts[PublicationStatus.REJECTED],
            published=counts[PublicationStatus.PUBLISHED],
            archived=counts[PublicationStatus.ARCHIVED],
        )

    async def get_dashboard(
        self,
        current_user: User,
    ) -> SuperAdminDashboard | InstitutionDashboard | ResearcherDashboard | ReviewerDashboard:

        if current_user.role == UserRole.SUPER_ADMIN:
            total_publications = await self.repository.total_publications()

            total_institutions = await self.repository.total_institutions()

            total_researchers = await self.repository.total_researchers()

            total_reviewers = await self.repository.total_reviewers()

            status_counts = await self.repository.publication_status_counts()

            top_researchers = await self.repository.top_researchers()

            return SuperAdminDashboard(
                total_publications=total_publications,
                publication_status=self._build_status_stats(status_counts),
                total_institutions=total_institutions,
                total_researchers=total_researchers,
                total_reviewers=total_reviewers,
                top_researchers=top_researchers,
            )
        elif current_user.role == UserRole.INSTITUTION_ADMIN:
            institution_id = current_user.institution_id

            status_counts = await self.repository.publication_status_counts(
                institution_id=institution_id,
            )

            return InstitutionDashboard(
                total_publications=await self.repository.total_publications(
                    institution_id=institution_id,
                ),
                publication_status=self._build_status_stats(status_counts),
                total_researchers=await self.repository.total_researchers(
                    institution_id=institution_id,
                ),
                total_reviewers=await self.repository.total_reviewers(
                    institution_id=institution_id,
                ),
                top_researchers=await self.repository.top_researchers(
                    institution_id=current_user.institution_id,
                ),
            )
        elif current_user.role == UserRole.RESEARCHER:
            my_publications = await self.repository.researcher_publications(
                current_user.id,
            )

            coauthored_publications = await self.repository.coauthored_publications(
                current_user.id,
            )

            status_counts = await self.repository.researcher_status_counts(
                current_user.id,
            )

            return ResearcherDashboard(
                my_publications=my_publications,
                coauthored_publications=coauthored_publications,
                publication_status=self._build_status_stats(
                    status_counts,
                ),
            )
        elif current_user.role == UserRole.REVIEWER:
            return ReviewerDashboard(
                assigned_reviews=await self.repository.assigned_reviews(
                    current_user.id,
                ),
                pending_reviews=await self.repository.pending_reviews(
                    current_user.id,
                ),
                completed_reviews=await self.repository.completed_reviews(
                    current_user.id,
                ),
            )
