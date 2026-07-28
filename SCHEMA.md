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

| Column | Type | Notes |
|---------|------|------|
| id | INTEGER PK | autoincrement |
| name | VARCHAR(255) | unique, not null |
| short_name | VARCHAR(100) | nullable |
| institution_type | VARCHAR(100) | nullable |
| email | VARCHAR(255) | unique, not null |
| phone | VARCHAR(20) | nullable |
| website | VARCHAR(255) | nullable |
| address | VARCHAR(500) | nullable |
| city | VARCHAR(100) | not null |
| state | VARCHAR(100) | not null |
| country | VARCHAR(100) | not null |
| postal_code | VARCHAR(20) | nullable |
| status | VARCHAR(30) | default 'Active' |
| created_at | TIMESTAMP | default now() |

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

The database schema is designed to support the Scientific Collaboration Network Analyzer by providing separate entities for Users, Researchers, and Institutions.

- The **Users** table manages authentication, user roles, and account information.
- The **Researchers** table stores academic profiles, research interests, skills, affiliations, and department details for each researcher.
- The **Institutions** table maintains detailed information about universities, colleges, and research organizations, including contact information and location details.
- A **one-to-one relationship** exists between Users and Researchers through `user_id`, ensuring that each researcher has a unique user account.
- A **one-to-many relationship** exists between Institutions and Researchers through `institution_id`, allowing one institution to have multiple researchers while each researcher belongs to a single institution.
- This schema is designed to be scalable so that future modules such as Publications, Conferences, Collaborations, Citations, and File Uploads can reference `researchers.id` and `institutions.id` without requiring major structural changes.

## Migration strategy
Alembic manages all schema changes going forward. Milestone 1 ships a single
initial migration `0001_initial.py` creating all three tables above.
Future migrations will introduce:
- publications
- conferences
- collaborations
- citations
- file uploads