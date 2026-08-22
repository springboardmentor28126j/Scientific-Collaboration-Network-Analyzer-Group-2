import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.api.deps import get_institution_service
from app.core.dependencies import require_superuser
from app.schemas.institution import InstitutionRead, InstitutionRegister
from app.services.institution_service import InstitutionService

router = APIRouter(prefix="/institutions", tags=["Institutions"])


@router.post(
    "/register",
    response_model=InstitutionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Self-register a new institution",
    description=(
        "Public endpoint — any institution can register itself with its "
        "name, address, and logo, plus admin credentials for the "
        "institution's first (and initially only) admin user. Sends a "
        "verification email to the admin; the admin account is inactive "
        "until that link is used (see POST /auth/verify-email)."
    ),
)
async def register_institution(
    name: str = Form(...),
    address: str = Form(...),
    admin_full_name: str = Form(...),
    admin_email: str = Form(...),
    admin_password: str = Form(...),
    turnstile_token: str = Form(...),
    logo: UploadFile = File(...),
    institution_service: InstitutionService = Depends(get_institution_service),
):
    payload = InstitutionRegister(
        name=name,
        address=address,
        admin_full_name=admin_full_name,
        admin_email=admin_email,
        admin_password=admin_password,
    )
    institution, _admin = await institution_service.register(payload, logo, turnstile_token)
    return institution


@router.get(
    "",
    response_model=list[InstitutionRead],
    summary="List all institutions on the platform (superuser only)",
    dependencies=[Depends(require_superuser)],
)
async def list_institutions(
    institution_service: InstitutionService = Depends(get_institution_service),
):
    return await institution_service.list_institutions()


@router.patch(
    "/{institution_id}/activate",
    response_model=InstitutionRead,
    summary="Activate an institution (superuser only)",
    dependencies=[Depends(require_superuser)],
)
async def activate_institution(
    institution_id: uuid.UUID,
    institution_service: InstitutionService = Depends(get_institution_service),
):
    return await institution_service.set_institution_active(institution_id, True)


@router.patch(
    "/{institution_id}/deactivate",
    response_model=InstitutionRead,
    summary="Deactivate an institution (superuser only)",
    description=(
        "Instantly locks out every user belonging to this institution, "
        "including already-issued access tokens — checked on every "
        "request, not just at login."
    ),
    dependencies=[Depends(require_superuser)],
)
async def deactivate_institution(
    institution_id: uuid.UUID,
    institution_service: InstitutionService = Depends(get_institution_service),
):
    return await institution_service.set_institution_active(institution_id, False)
