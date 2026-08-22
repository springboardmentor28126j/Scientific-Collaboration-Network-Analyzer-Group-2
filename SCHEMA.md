# Milestone 1 — Database Schema (ERD-level)

## Entities

### users
| Column        | Type          | Notes                              |
|---------------|---------------|-------------------------------------|
| id            | INTEGER PK    | autoincrement                       |
| email         | VARCHAR(255)  | unique, not null                    |
| password_hash | VARCHAR(255)  | not null (bcrypt via passlib)       |
| role          | VARCHAR(30)   | researcher \| institution_admin \| reviewer \| system_admin |
| is_active     | BOOLEAN       | default true                        |
| created_at    | TIMESTAMP     | default now()                       |

### institutions
| Column     | Type          | Notes            |
|------------|---------------|-------------------|
| id         | INTEGER PK    | autoincrement     |
| name       | VARCHAR(255)  | not null          |
| address    | VARCHAR(500)  | nullable          |
| created_at | TIMESTAMP     | default now()     |

### researchers
| Column              | Type          | Notes                                |
|---------------------|---------------|----------------------------------------|
| id                  | INTEGER PK    | autoincrement                          |
| user_id             | INTEGER FK -> users.id | unique (1:1 with user)        |
| institution_id      | INTEGER FK -> institutions.id | nullable                |
| department          | VARCHAR(255)  | nullable                               |
| research_interests  | TEXT          | nullable                               |
| skills              | TEXT          | nullable                               |
| affiliations        | TEXT          | nullable                               |
| created_at          | TIMESTAMP     | default now()                          |

## Relationships
- `users.id` 1---1 `researchers.user_id` (a User "is" a Researcher when role=researcher)
- `institutions.id` 1---N `researchers.institution_id`

## Rationale
This is intentionally the minimal slice of Modules 1 & 2 needed to satisfy
Milestone 1's exit criteria (auth completed, user mgmt functional, researcher
module completed). Publication/Collaboration/Conference/Citation tables are
deferred to Milestones 2–3 per the doc's own week-wise plan, and will FK into
`researchers.id` and `institutions.id` later without needing to touch this
schema.

## Migration strategy
Alembic manages all schema changes going forward. Milestone 1 ships a single
initial migration `0001_initial.py` creating all three tables above.
