from fastapi import HTTPException, status

from app.models.user import User, UserRole, AffiliationStatus


def require_verified_affiliation(current_user: User) -> None:
    """
    Blocks a researcher whose institution claim hasn't been verified yet from
    creating institution-tagged resources (publications, projects). Without
    this, a PENDING or REJECTED researcher's unverified institution_id would
    still leak into that institution's reports/moderation views the moment
    they create something -- before an admin ever signed off on the
    affiliation, defeating the point of the approval workflow.

    Independent researchers (no institution_id at all) and APPROVED ones
    pass straight through -- this only blocks the specific case where an
    institution claim exists but hasn't (or no longer) checks out.
    """
    if current_user.role != UserRole.RESEARCHER or current_user.institution_id is None:
        return
    if current_user.affiliation_status != AffiliationStatus.APPROVED:
        status_label = current_user.affiliation_status.value.replace("_", " ")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Your institution affiliation is still {status_label}. "
                "You'll be able to create institution-linked work once your institution admin approves it."
            ),
        )
