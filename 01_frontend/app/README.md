# ResearchMesh Frontend

ResearchMesh is a comprehensive scientific collaboration network analyzer platform. It facilitates the management, peer review, and public access to research publications across various academic institutions.

## Features

- **Role-Based Dashboards**: Tailored views and capabilities for Super Admins, Institution Admins, Researchers, and Reviewers.
  - *Super Admin*: Manage institutions, oversee global platform health, and view top researchers.
  - *Institution Admin*: Manage users (researchers & reviewers) within their respective institution.
  - *Researcher*: Submit publications, manage drafts, invite co-authors, and curate references.
  - *Reviewer*: Access assigned papers, review content, and submit editorial decisions.
- **Public Library (Catalog)**: A public-facing searchable catalog of all published and archived research papers.
- **Advanced Publication Management**: Full lifecycle management of papers from Draft -> Submitted -> Under Review -> Revision Required -> Accepted -> Published.
- **Citation & References System**: Integrated lookup system to seamlessly add internal and external citations.
- **Automated Workflows**: Download PDFs, track co-authors, and monitor peer-review feedback.

## Tech Stack

- React 18 + TypeScript + Vite
- Tailwind CSS + shadcn/ui for UI components
- Zustand for state management
- React Query for data fetching and caching
- React Router v6 for navigation
- Recharts for dashboard analytics

## Local Development

To run the frontend application locally on your machine:

1. **Install Dependencies**
   Ensure you have Node.js and `pnpm` installed. Run the following command from this directory:
   ```bash
   pnpm install
   ```

2. **Environment Variables**
   Create a `.env` file in the root of the frontend folder and specify the backend API URL:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

3. **Start the Development Server**
   ```bash
   pnpm run dev
   ```
   The application will be available at `http://localhost:3000`.

## Production Deployment (Render.com)

This frontend is designed to be easily deployed as a Static Site on Render.com.

1. **Connect your Repository**
   Log into Render and create a new "Static Site". Connect your GitHub/GitLab repository.

2. **Configure the Build Settings**
   - **Build Command**: `pnpm install && pnpm run build`
   - **Publish Directory**: `dist`
   
3. **Environment Variables**
   Under the Advanced settings in Render, add your production environment variables:
   - `VITE_API_URL`: The URL of your deployed backend API (e.g., `https://api.your-backend.onrender.com`)

4. **Routing Configuration**
   Since this is a Single Page Application (SPA) using React Router, you must configure URL rewriting in Render so that all paths redirect to `index.html`.
   - In your Render dashboard, navigate to the **Redirects/Rewrites** tab for your Static Site.
   - Add a rule:
     - **Source**: `/*`
     - **Destination**: `/index.html`
     - **Action**: `Rewrite`

5. **Deploy**
   Save the changes and trigger a manual deploy if necessary. Render will automatically build the site and deploy your frontend.
