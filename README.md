# Invoice Management System

A full-stack, containerized web application designed for managing patients, generating invoices, and handling treatment records. It is specifically tailored for healthcare and therapy practices (e.g., Heilpraktiker, Physiotherapy), featuring customizable invoice templates, default billing items, automated PDF generation, and tax reporting.

## 🚀 Features

* **Patient Management**: Create, update, and manage patient profiles, including contact details and travel distances for automated billing.
* **Invoice Generation**: Create draft invoices, assign treatment dates, add custom billing items, and apply default items.
* **PDF Export**: Generate professional PDF documents including Invoices (HP, KG, etc.), Privacy Clauses, and Therapy Agreements.
* **Settings & Templates**: Configure default invoice items, privacy clauses, and therapy clauses to streamline repetitive tasks.
* TODO: (**Tax Reporting**: Automatically calculate and export yearly tax data (totals, date counts, kilometers traveled) to CSV.)
* **Responsive UI**: Modern, fast, and responsive user interface built with React and Vite.

## 🛠️ Tech Stack

**Backend**
* [FastAPI](https://fastapi.tiangolo.com/) - High-performance Python web framework.
* [SQLAlchemy](https://www.sqlalchemy.org/) & [Alembic](https://alembic.sqlalchemy.org/) - ORM and database migrations.
* [SQLite](https://www.sqlite.org/index.html) - Lightweight, file-based database.

**Frontend**
* [React](https://reactjs.org/) + [Vite](https://vitejs.dev/) - Blazing fast frontend tooling and UI library.
* [TypeScript](https://www.typescriptlang.org/) - Static typing for scalable code.

**Infrastructure**
* [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) - Containerization for dev and prod.
* [Nginx](https://nginx.org/) - Reverse proxy and static file serving for production.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your machine:
* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)
* Git

---

## 💻 Development Setup

The development environment utilizes `docker-compose.yml` to spin up the backend and frontend with hot-reloading enabled.

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd invoice
   ```

2. **Set up environment variables:**
   Copy the example environment file and configure it if necessary.
   ```bash
   cp .env.example .env
   ```

3. **Start the development containers:**
   ```bash
   docker-compose up --build
   ```
   *(Alternatively, if you are using the included `Makefile`, you can run `make up-dev`)*

4. **Access the application:**
   * **Frontend:** [http://localhost:5173](http://localhost:5173)
   * **Backend API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

5. **Database Migrations:**
   The backend container handles migrations automatically on startup via the `alembic upgrade head` command. To run them manually or generate new ones:
   ```bash
   docker-compose exec backend alembic revision --autogenerate -m "Your message"
   docker-compose exec backend alembic upgrade head
   ```

---

## 🌍 Production Setup

The production setup uses `docker-compose.prod.yml` to run optimized builds pulled from the projects github code repository. The frontend is served statically via Nginx, and the backend runs via an ASGI production server.

1. **Prepare the server:**
   Clone the repository to your production server.

2. **Configure production environment variables:**
   Ensure your `.env` file contains production-ready secrets and variables (e.g., secure passwords, correct domain names, restricted CORS origins).

3. **Build and start production containers:**
   Run the application in detached mode using the production compose file. (Or use the included `Makefile` with `make up-prod`. Be aware that this tries to run the certificate generation so the scripts folder should be present!)
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **SSL / HTTPS Certificates (Recommended):**
   The project includes scripts for managing SSL certificates (`scripts/renew-cert.sh` for Linux/macOS and `scripts/renew-cert.ps1` for Windows). 
   * Ensure your Nginx configuration (`frontend/nginx/default.conf`) is set up to handle port 443 and points to your generated certificates.
   * Run the renewal script periodically (e.g., via a cron job) to keep certificates up to date.

---

## 🗄️ Database Management

The application uses SQLite, meaning the database is stored as a local file inside the container, typically mounted via Docker volumes to persist data across container restarts.

* **Backups:** To back up your data, simply copy the `.sqlite3` file from the mounted volume location to a secure backup directory.
* **Restoring:** Stop the containers, replace the `.sqlite3` file with your backup, and restart the containers.

---

## 📁 Repository Structure

* `/backend` - FastAPI Python backend, SQLAlchemy models, Alembic migrations, and PDF generation logic.
* `/frontend` - React/Vite frontend application, UI components, and API client.
* `/scripts` - Helper scripts (e.g., SSL certificate renewal).
* `docker-compose.yml` - Configuration for local development.
* `docker-compose.prod.yml` - Configuration for production deployment.
* `Makefile` - Convenience commands for running builds, tests, and database migrations.