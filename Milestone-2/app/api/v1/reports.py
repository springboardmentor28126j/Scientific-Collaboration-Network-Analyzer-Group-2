from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_session
from app.models.institution import Institution
from app.models.research import InstitutionalCollaboration, Project, Publication
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["Reports"])


def institution_id_for(user: User):
    if user.institution_id is None:
        raise HTTPException(status_code=400, detail="Select an institution-scoped account")
    return user.institution_id


async def publication_rows(session: AsyncSession, institution_id):
    return list((await session.scalars(
        select(Publication)
        .where(Publication.institution_id == institution_id)
        .order_by(Publication.created_at.desc())
    )).all())


@router.get("/summary")
async def report_summary(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> dict[str, int]:
    institution_id = institution_id_for(user)

    async def count(model, *conditions):
        return await session.scalar(select(func.count()).select_from(model).where(*conditions)) or 0

    return {
        "publications": await count(Publication, Publication.institution_id == institution_id),
        "published_publications": await count(Publication, Publication.institution_id == institution_id, Publication.status == "PUBLISHED"),
        "projects": await count(Project, Project.institution_id == institution_id),
        "active_projects": await count(Project, Project.institution_id == institution_id, Project.status == "ACTIVE"),
    }


@router.get("/research")
async def research_report(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> dict[str, int]:
    institution_id = institution_id_for(user)
    return {"publications": await session.scalar(select(func.count()).select_from(Publication).where(Publication.institution_id == institution_id)) or 0, "projects": await session.scalar(select(func.count()).select_from(Project).where(Project.institution_id == institution_id)) or 0}


@router.get("/collaborations")
async def collaboration_report(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> dict[str, int]:
    return {"collaborations": await session.scalar(select(func.count()).select_from(InstitutionalCollaboration).where(InstitutionalCollaboration.institution_id == institution_id_for(user))) or 0}


@router.get("/institution")
async def institution_report(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> dict[str, int]:
    institution_id = institution_id_for(user)
    return {"institutions": await session.scalar(select(func.count()).select_from(Institution).where(Institution.id == institution_id)) or 0, "members": await session.scalar(select(func.count()).select_from(User).where(User.institution_id == institution_id)) or 0}


@router.get("/publications.xlsx")
async def export_publications_xlsx(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> Response:
    try:
        from openpyxl import Workbook
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="Excel export dependency is not installed") from exc

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Publications"
    sheet.append(["Title", "Type", "Status", "DOI", "Published on", "Created at"])
    for publication in await publication_rows(session, institution_id_for(user)):
        sheet.append([
            publication.title,
            publication.publication_type,
            publication.status,
            publication.doi or "",
            publication.published_on.isoformat() if publication.published_on else "",
            publication.created_at.isoformat(),
        ])
    for column in sheet.columns:
        sheet.column_dimensions[column[0].column_letter].width = min(
            max(len(str(cell.value or "")) for cell in column) + 2, 50
        )
    stream = BytesIO()
    workbook.save(stream)
    return Response(
        stream.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="publications.xlsx"'},
    )


@router.get("/publications.pdf")
async def export_publications_pdf(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> Response:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="PDF export dependency is not installed") from exc

    stream = BytesIO()
    document = SimpleDocTemplate(stream, pagesize=A4)
    styles = getSampleStyleSheet()
    rows = [["Title", "Type", "Status", "DOI"]]
    for publication in await publication_rows(session, institution_id_for(user)):
        rows.append([
            Paragraph(publication.title, styles["BodyText"]),
            publication.publication_type,
            publication.status,
            publication.doi or "—",
        ])
    table = Table(rows, colWidths=[250, 90, 80, 100], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    document.build([Paragraph("Publication Report", styles["Title"]), Spacer(1, 16), table])
    return Response(
        stream.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="publications.pdf"'},
    )
