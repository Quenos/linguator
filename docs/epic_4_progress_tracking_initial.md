# Epic 4: Progress Tracking - Initial Implementation

*   **Goal:** Provide users with fundamental insights into their learning progress by recording practice session results and displaying basic statistics.
*   **Tickets:**

    1.  **Ticket: Performance Data Model & API Endpoint**
        *   **Background:** Define the database schema and API endpoint required to store user performance data (e.g., which words were answered correctly/incorrectly during practice).
        *   **Acceptance Criteria:**
            *   Database schema (SQL/migration) created for a `practice_results` table (or similar), linked to `word_pairs`. Include columns for word pair ID, timestamp, correct/incorrect status.
            *   A `POST /practice-results` endpoint exists to record the outcome of a single question review or a batch of results from a session.
            *   The endpoint successfully saves performance data to the database.
        *   **Tech Suggestions:** Database schema design, API endpoint implementation.

    2.  **Ticket: Record Practice Results from Session**
        *   **Background:** Integrate the performance recording logic into the Practice Mode flow. When a user marks a flashcard as "Correct" or "Incorrect", send this data to the backend API.
        *   **Acceptance Criteria:**
            *   After a user provides feedback ("Correct"/"Incorrect") in Practice Mode, a request is made to the `POST /practice-results` endpoint.
            *   The request includes the relevant word pair ID and the outcome.
            *   Data is successfully saved for each question reviewed in a session.
        *   **Tech Suggestions:** Frontend API call integration, Event handling.

    3.  **Ticket: Basic Progress Statistics API Endpoint**
        *   **Background:** Create an API endpoint that calculates and returns basic progress statistics based on the recorded `practice_results`.
        *   **Acceptance Criteria:**
            *   A `GET /progress/stats` endpoint exists.
            *   The endpoint returns data like: total unique words practiced, overall accuracy percentage (correct / total attempts).
            *   The calculations correctly query the `practice_results` data.
        *   **Tech Suggestions:** API endpoint implementation, Database aggregation queries (COUNT, AVG).

    4.  **Ticket: Progress Tracking UI - Display Basic Stats**
        *   **Background:** Create a simple UI section to display the basic progress statistics fetched from the API.
        *   **Acceptance Criteria:**
            *   A dedicated page/section exists for Progress Tracking.
            *   The UI calls the `GET /progress/stats` endpoint on load.
            *   The fetched statistics (total words practiced, accuracy %) are clearly displayed.
            *   Basic loading and error states are handled.
        *   **Tech Suggestions:** Frontend component, API data fetching. 