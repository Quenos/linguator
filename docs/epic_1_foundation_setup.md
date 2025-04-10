# Epic 1: Foundation & Setup

*   **Goal:** Establish the basic project structure, database schema, API framework, and localization infrastructure necessary to support the language learning application features.
*   **Tickets:**

    1.  **Ticket: Project Initialization & CI/CD Setup**
        *   **Background:** Create the initial repository, set up the build system (e.g., Node.js with npm/yarn, Python with pip/poetry), configure basic linting/formatting, and establish a simple CI/CD pipeline (e.g., GitHub Actions) for automated checks and builds.
        *   **Acceptance Criteria:**
            *   Repository created and accessible.
            *   Basic project structure (src, tests, docs) is in place.
            *   A "hello world" equivalent endpoint or basic app shell runs successfully.
            *   Linting and formatting checks pass.
            *   CI pipeline runs on push/PR.
        *   **Tech Suggestions:** Git, Docker (optional), Node.js/Python/Go, GitHub Actions/GitLab CI.

    2.  **Ticket: Database Schema Design & Setup (Word Pairs)**
        *   **Background:** Define and implement the initial database schema required to store word pairs, including source/target language, categories, and example sentences. Set up database connection logic.
        *   **Acceptance Criteria:**
            *   Database schema (SQL script or migration file) is created for the `word_pairs` table (or equivalent).
            *   Table includes columns for ID, source word, target word, category, example sentence, creation/update timestamps.
            *   A migration tool (if applicable) is set up.
            *   The application can connect to the database (dev environment).
        *   **Tech Suggestions:** PostgreSQL/MySQL/SQLite, Prisma/SQLAlchemy/TypeORM (ORM), Flyway/Alembic (Migrations).

    3.  **Ticket: Basic API Structure & CRUD for Word Pairs**
        *   **Background:** Implement the foundational API structure (e.g., RESTful endpoints, routing) and create the basic Create, Read, Update, Delete (CRUD) operations for word pairs.
        *   **Acceptance Criteria:**
            *   API endpoints exist for `POST /word-pairs`, `GET /word-pairs`, `GET /word-pairs/{id}`, `PUT /word-pairs/{id}`, `DELETE /word-pairs/{id}`.
            *   These endpoints successfully interact with the database to perform CRUD operations.
            *   Basic request validation is implemented (e.g., required fields).
            *   API responses follow a consistent format (e.g., JSON).
        *   **Tech Suggestions:** Express/FastAPI/Gin (Web Framework), REST principles.

    4.  **Ticket: Localization Framework Implementation**
        *   **Background:** Integrate a localization library/framework (e.g., i18next, Flask-Babel) into the application to handle multiple languages. Set up the structure for translation files.
        *   **Acceptance Criteria:**
            *   A localization library is added as a dependency.
            *   Configuration for supported languages (EN, IT, RU) is present.
            *   Structure for storing translation strings (e.g., JSON, PO files) is created.
            *   A simple example of a localized string is successfully displayed in the UI/API response based on a language preference (e.g., header).
        *   **Tech Suggestions:** i18next (JS), Flask-Babel (Python), gettext utilities. 