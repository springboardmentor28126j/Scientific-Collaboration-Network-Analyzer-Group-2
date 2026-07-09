# Database Schema

## Tables

### 1. Researchers

- id (Primary Key)
- full_name
- email
- institution
- department
- specialization
- h_index
- total_publications

---

### 2. Research Papers

- id (Primary Key)
- title
- abstract
- publication_year
- journal
- doi

---

### 3. Institutions

- id (Primary Key)
- institution_name
- country
- city
- website
- established_year

---

### 4. Collaborations

- id (Primary Key)
- researcher_1_id (Foreign Key)
- researcher_2_id (Foreign Key)
- paper_id (Foreign Key)
- collaboration_year

---

## Relationships

- One Institution → Many Researchers
- One Research Paper → Many Collaborations
- One Researcher → Multiple Collaborations