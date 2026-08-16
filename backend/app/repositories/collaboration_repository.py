from sqlalchemy import select, func, desc, or_, and_
from sqlalchemy.orm import Session, joinedload

from app.models.collaboration import (
    Collaboration, CollaborationPublication, CollaborationRequest, CollaborationRequestStatus,
)
from app.models.publication import Publication, PublicationAuthor
from app.models.researcher import ResearcherProfile, ResearcherSkill, ResearcherInterest
from app.models.user import User


def _ordered_pair(researcher_a_id: int, researcher_b_id: int) -> tuple[int, int]:
    """Collaboration is an undirected edge -- always store it with the
    smaller researcher_id first so 'does an edge exist between A and B'
    is a single lookup instead of two (see the ck_collaboration_ordered_pair
    constraint on the table itself)."""
    return (researcher_a_id, researcher_b_id) if researcher_a_id < researcher_b_id else (researcher_b_id, researcher_a_id)


def _researcher_context_options(relationship_attr=None):
    """Builds the joinedload chain needed to construct a ResearcherBrief
    (user -> institution, department). Pass a relationship attribute (e.g.
    Collaboration.researcher1) when querying through it, or nothing when
    ResearcherProfile is the query's own root entity."""
    if relationship_attr is None:
        return [
            joinedload(ResearcherProfile.user).joinedload(User.institution),
            joinedload(ResearcherProfile.department),
        ]
    return [
        joinedload(relationship_attr).joinedload(ResearcherProfile.user).joinedload(User.institution),
        joinedload(relationship_attr).joinedload(ResearcherProfile.department),
    ]


def get_researcher_with_context(db: Session, researcher_id: int) -> ResearcherProfile | None:
    stmt = select(ResearcherProfile).where(ResearcherProfile.researcher_id == researcher_id)
    stmt = stmt.options(*_researcher_context_options())
    return db.scalar(stmt)


# --- Collaborations (established edges) ---

def get_collaboration_between(db: Session, researcher_a_id: int, researcher_b_id: int) -> Collaboration | None:
    lo, hi = _ordered_pair(researcher_a_id, researcher_b_id)
    return db.scalar(
        select(Collaboration).where(Collaboration.researcher1_id == lo, Collaboration.researcher2_id == hi)
    )


def get_or_create_collaboration(db: Session, researcher_a_id: int, researcher_b_id: int) -> tuple[Collaboration, bool]:
    existing = get_collaboration_between(db, researcher_a_id, researcher_b_id)
    if existing is not None:
        return existing, False
    lo, hi = _ordered_pair(researcher_a_id, researcher_b_id)
    collaboration = Collaboration(researcher1_id=lo, researcher2_id=hi)
    db.add(collaboration)
    db.commit()
    db.refresh(collaboration)
    return collaboration, True


def get_by_id(db: Session, collaboration_id: int) -> Collaboration | None:
    stmt = select(Collaboration).where(Collaboration.collaboration_id == collaboration_id)
    stmt = stmt.options(
        *_researcher_context_options(Collaboration.researcher1),
        *_researcher_context_options(Collaboration.researcher2),
        joinedload(Collaboration.shared_publications).joinedload(CollaborationPublication.publication),
    )
    return db.scalar(stmt)


def list_for_researcher(db: Session, researcher_id: int, page: int = 1, page_size: int = 10) -> tuple[list[Collaboration], int]:
    base = select(Collaboration).where(
        or_(Collaboration.researcher1_id == researcher_id, Collaboration.researcher2_id == researcher_id)
    )
    total = db.scalar(select(func.count()).select_from(base.subquery()))

    stmt = base.options(
        *_researcher_context_options(Collaboration.researcher1),
        *_researcher_context_options(Collaboration.researcher2),
    )
    stmt = (
        stmt.order_by(desc(Collaboration.last_collaboration), desc(Collaboration.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(db.scalars(stmt).unique().all())
    return items, total


def recompute_metrics(db: Session, collaboration: Collaboration) -> Collaboration:
    """
    Finds every publication where both sides of the pair appear as an author
    (primary or co-author), syncs collaboration_publication to match exactly
    (adds new shared publications, drops ones that no longer apply -- e.g.
    a co-author was removed), and recomputes strength/first/last from that
    set. Idempotent and safe to call repeatedly.
    """
    r1, r2 = collaboration.researcher1_id, collaboration.researcher2_id

    def authored_publication_ids(researcher_id: int) -> set[int]:
        primary = select(Publication.publication_id).where(Publication.primary_author_id == researcher_id)
        co = select(PublicationAuthor.publication_id).where(PublicationAuthor.researcher_id == researcher_id)
        return set(db.scalars(primary)) | set(db.scalars(co))

    shared_ids = authored_publication_ids(r1) & authored_publication_ids(r2)
    existing_links = {cp.publication_id: cp for cp in collaboration.shared_publications}

    for pub_id in shared_ids - existing_links.keys():
        db.add(CollaborationPublication(collaboration_id=collaboration.collaboration_id, publication_id=pub_id))
    for pub_id, link in existing_links.items():
        if pub_id not in shared_ids:
            db.delete(link)
    db.flush()

    if shared_ids:
        dates = [
            d for d in db.scalars(
                select(Publication.publication_date).where(Publication.publication_id.in_(shared_ids))
            ).all() if d is not None
        ]
        if dates:
            collaboration.first_collaboration = min(dates)
            collaboration.last_collaboration = max(dates)

    collaboration.strength = len(shared_ids)
    db.commit()
    db.refresh(collaboration)
    return collaboration


def sync_pair_on_publication(db: Session, researcher_a_id: int, researcher_b_id: int) -> None:
    """
    Called after a publication is created/updated. If these two researchers
    already have an established collaboration, keep its strength/dates fresh
    immediately. Deliberately does NOT create a new Collaboration just
    because two people co-authored something -- becoming collaborators in
    this network is a deliberate connect/accept action (see
    CollaborationRequest), not an automatic side effect of authorship.
    """
    collaboration = get_collaboration_between(db, researcher_a_id, researcher_b_id)
    if collaboration is not None:
        recompute_metrics(db, collaboration)


def sync_all_pairs_for_publication(db: Session, publication: Publication) -> None:
    author_ids = {publication.primary_author_id} | {ca.researcher_id for ca in publication.co_authors}
    author_ids = list(author_ids)
    for i in range(len(author_ids)):
        for j in range(i + 1, len(author_ids)):
            sync_pair_on_publication(db, author_ids[i], author_ids[j])


# --- Collaboration requests (the connect / accept flow) ---

def get_pending_request_between(db: Session, researcher_a_id: int, researcher_b_id: int) -> CollaborationRequest | None:
    return db.scalar(
        select(CollaborationRequest).where(
            CollaborationRequest.status == CollaborationRequestStatus.PENDING,
            or_(
                and_(CollaborationRequest.requester_id == researcher_a_id, CollaborationRequest.addressee_id == researcher_b_id),
                and_(CollaborationRequest.requester_id == researcher_b_id, CollaborationRequest.addressee_id == researcher_a_id),
            ),
        )
    )


def get_request_by_id(db: Session, collaboration_request_id: int) -> CollaborationRequest | None:
    stmt = select(CollaborationRequest).where(CollaborationRequest.collaboration_request_id == collaboration_request_id)
    stmt = stmt.options(
        *_researcher_context_options(CollaborationRequest.requester),
        *_researcher_context_options(CollaborationRequest.addressee),
    )
    return db.scalar(stmt)


def list_requests(
    db: Session, researcher_id: int, direction: str | None = None, status_filter: CollaborationRequestStatus | None = None
) -> list[CollaborationRequest]:
    stmt = select(CollaborationRequest)
    if direction == "incoming":
        stmt = stmt.where(CollaborationRequest.addressee_id == researcher_id)
    elif direction == "outgoing":
        stmt = stmt.where(CollaborationRequest.requester_id == researcher_id)
    else:
        stmt = stmt.where(
            or_(CollaborationRequest.addressee_id == researcher_id, CollaborationRequest.requester_id == researcher_id)
        )
    if status_filter is not None:
        stmt = stmt.where(CollaborationRequest.status == status_filter)

    stmt = stmt.options(
        *_researcher_context_options(CollaborationRequest.requester),
        *_researcher_context_options(CollaborationRequest.addressee),
    )
    stmt = stmt.order_by(desc(CollaborationRequest.created_at))
    return list(db.scalars(stmt).unique().all())


# --- Network graph (ego network centered on one researcher) ---

def ego_network(db: Session, researcher_id: int, depth: int = 2, max_nodes: int = 60):
    """BFS outward from researcher_id along Collaboration edges up to
    `depth` hops. Returns (researchers, collaborations)."""
    visited = {researcher_id}
    frontier = {researcher_id}
    edges: dict[int, Collaboration] = {}

    for _ in range(max(1, depth)):
        if not frontier or len(visited) >= max_nodes:
            break
        stmt = select(Collaboration).where(
            or_(Collaboration.researcher1_id.in_(frontier), Collaboration.researcher2_id.in_(frontier))
        )
        next_frontier = set()
        for collaboration in db.scalars(stmt).all():
            edges[collaboration.collaboration_id] = collaboration
            for rid in (collaboration.researcher1_id, collaboration.researcher2_id):
                if rid not in visited:
                    next_frontier.add(rid)
        visited |= next_frontier
        frontier = next_frontier

    node_ids = list(visited)[:max_nodes]
    stmt = select(ResearcherProfile).where(ResearcherProfile.researcher_id.in_(node_ids))
    stmt = stmt.options(*_researcher_context_options())
    researchers = list(db.scalars(stmt).unique().all())
    return researchers, list(edges.values())


# --- Suggested collaborators ---

def suggested_collaborators(db: Session, researcher_id: int, limit: int = 10):
    """
    Ranks non-connected researchers by (1) mutual collaborators -- people
    the researcher's own collaborators are connected to -- then (2) shared
    skills/research interests. Excludes the researcher themselves, anyone
    already collaborating with them, and anyone with a pending request
    (either direction) already in flight.
    Returns a list of (ResearcherProfile, reason, mutual_count, shared_interest_count) tuples.
    """
    existing_collab_ids = set(
        db.scalars(select(Collaboration.researcher1_id).where(Collaboration.researcher2_id == researcher_id))
    ) | set(
        db.scalars(select(Collaboration.researcher2_id).where(Collaboration.researcher1_id == researcher_id))
    )
    pending_ids = set(
        db.scalars(
            select(CollaborationRequest.addressee_id).where(
                CollaborationRequest.requester_id == researcher_id,
                CollaborationRequest.status == CollaborationRequestStatus.PENDING,
            )
        )
    ) | set(
        db.scalars(
            select(CollaborationRequest.requester_id).where(
                CollaborationRequest.addressee_id == researcher_id,
                CollaborationRequest.status == CollaborationRequestStatus.PENDING,
            )
        )
    )
    excluded = existing_collab_ids | pending_ids | {researcher_id}

    mutual_counts: dict[int, int] = {}
    for collaborator_id in existing_collab_ids:
        their_partners = set(
            db.scalars(select(Collaboration.researcher1_id).where(Collaboration.researcher2_id == collaborator_id))
        ) | set(
            db.scalars(select(Collaboration.researcher2_id).where(Collaboration.researcher1_id == collaborator_id))
        )
        for partner_id in their_partners - excluded:
            mutual_counts[partner_id] = mutual_counts.get(partner_id, 0) + 1

    me = db.scalar(
        select(ResearcherProfile)
        .options(
            joinedload(ResearcherProfile.skills).joinedload(ResearcherSkill.skill),
            joinedload(ResearcherProfile.interests).joinedload(ResearcherInterest.interest),
        )
        .where(ResearcherProfile.researcher_id == researcher_id)
    )
    my_skill_ids = {rs.skill_id for rs in me.skills} if me else set()
    my_interest_ids = {ri.interest_id for ri in me.interests} if me else set()

    candidate_ids = set(mutual_counts.keys())
    if my_skill_ids:
        candidate_ids |= set(
            db.scalars(
                select(ResearcherSkill.researcher_id).where(
                    ResearcherSkill.skill_id.in_(my_skill_ids), ResearcherSkill.researcher_id.notin_(excluded)
                )
            )
        )
    if my_interest_ids:
        candidate_ids |= set(
            db.scalars(
                select(ResearcherInterest.researcher_id).where(
                    ResearcherInterest.interest_id.in_(my_interest_ids), ResearcherInterest.researcher_id.notin_(excluded)
                )
            )
        )
    candidate_ids -= excluded
    if not candidate_ids:
        return []

    stmt = (
        select(ResearcherProfile)
        .options(
            joinedload(ResearcherProfile.skills).joinedload(ResearcherSkill.skill),
            joinedload(ResearcherProfile.interests).joinedload(ResearcherInterest.interest),
        )
        .where(ResearcherProfile.researcher_id.in_(candidate_ids))
    )
    stmt = stmt.options(*_researcher_context_options())
    candidates = list(db.scalars(stmt).unique().all())

    results = []
    for candidate in candidates:
        shared = len({ri.interest_id for ri in candidate.interests} & my_interest_ids)
        shared += len({rs.skill_id for rs in candidate.skills} & my_skill_ids)
        mutual = mutual_counts.get(candidate.researcher_id, 0)
        if mutual > 0:
            reason = f"{mutual} mutual collaborator{'s' if mutual != 1 else ''}"
        elif shared > 0:
            reason = "Shares research interests or skills with you"
        else:
            reason = "You might know them"
        results.append((candidate, reason, mutual, shared))

    results.sort(key=lambda t: (t[2], t[3]), reverse=True)
    return results[:limit]
