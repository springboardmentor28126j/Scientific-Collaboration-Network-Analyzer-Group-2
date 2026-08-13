# SCNA Friday Presentation Guide

## 1. Opening (20 seconds)

“Scientific Collaboration Network Analyzer is a central research-management platform. It manages researchers, institutions, publications, projects, conferences, citations, and collaborations. It has separate role workspaces and produces reports and network visualisations without using AI.”

## 2. Show System Admin dashboard

Say:

- “System Admin sees overall system statistics and can manage the platform.”
- “The notification bell shows unread activity.”
- “Account Approvals handles new role requests, and Account Directory connects a user to their researcher or institution workspace.”
- “Audit Log records important operations and Data Quality identifies incomplete records.”

## 3. Show modules

| Module | Explain/show |
| --- | --- |
| Researchers | Academic profile, department, skills, interests, affiliation |
| Institutions | Institution details and reporting scope |
| Publications | Authors, status, DOI validation, PDF upload, publication type |
| Projects | Funding, dates, status, researcher team assignment |
| Conferences | Event details and researcher participation |
| Citations | Publication-to-publication reference linking |
| Collaborations | Requests, pending/accepted/rejected status, project/publication link |
| Network | Interactive graph, researcher search, institution filter, detail panel |
| Reports | Institution charts and Excel/PDF export |

## 4. Role-based demonstration

### Institution Admin

“Institution Admin is restricted to one assigned institution. They can manage their institution’s researchers, publications, projects, reports, and reviewer assignments.”

### Publisher

“Publisher manages publication workflow: Draft, Submitted, Published, Archived. They can manage authors, DOI, citation records, and assign reviewers.”

### Reviewer

“Reviewer sees only publications assigned to that account. They receive a due date, add comments, and submit Approved, Changes Requested, or Rejected decision.”

### Researcher

“Researcher has a personal workspace showing only their own academic activity, linked profile, publications, collaborations, projects, and conferences.”

## 5. Show reviewer workflow

1. Login as Admin/Publisher.
2. Open **Reviews**.
3. Assign an active Reviewer to a publication and set a due date.
4. Login as that Reviewer.
5. Open **Reviews**, add comments, and select a decision.
6. Return to Admin and show Audit Log.

## 6. Explain reports

“Reports are generated for a selected institution. The report has researcher/publication/collaboration totals, publication status by year, top researchers, and collaboration activity. It can be exported as a real Excel workbook and server-generated PDF.”

## 7. Closing (15 seconds)

“The project meets the main modules: research management, publication repository, collaboration tracking, conference/project tracking, citations, dashboards, reports, notifications, and Docker readiness. The remaining production roadmap is automated testing, deployment pipeline, and advanced email/background processing.”

## Questions your mentor may ask

### How is security handled?

“Passwords are bcrypt-hashed. Login creates a JWT. Protected APIs check the token and role in the backend; the frontend sidebar is only for usability, not the security layer.”

### How are reports generated?

“The backend queries researcher, publication, and collaboration records for an institution, returns analytics JSON for charts, saves generated-report history, and exports the selected report through OpenPyXL for Excel and ReportLab for PDF.”

### How does the network graph work?

“Researchers are nodes. Shared publication authors and accepted collaboration records become edges. The edge weight represents repeated shared activity.”

### What happens after a user registers?

“A non-Researcher role stays pending. System Admin approves/rejects it, links it to the correct workspace when needed, and the user receives a notification/email if configured.”
