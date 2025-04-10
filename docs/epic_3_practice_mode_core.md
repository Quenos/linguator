# Epic 3: Practice Mode - Core Functionality

*   **Goal:** Implement the core practice engine, allowing users to test their knowledge of selected word pairs using a primary question type (e.g., flashcards) and receive immediate feedback.
*   **Tickets:**

    1.  **Ticket: Practice Mode UI Shell & Session Start**
        *   **Background:** Create the basic UI structure for the Practice Mode screen. Implement the logic to start a practice session (e.g., fetch a set number of word pairs).
        *   **Acceptance Criteria:**
            *   A dedicated page/section exists for Practice Mode.
            *   A "Start Practice" button initiates a session.
            *   On start, the application fetches a predefined number (e.g., 10) of word pairs using the `GET /word-pairs` endpoint (or a dedicated practice endpoint).
            *   The UI transitions to the first question display state.
            *   Basic layout for question display, answer input, and feedback is present.
        *   **Tech Suggestions:** Frontend routing, State management.

    2.  **Ticket: Flashcard Question Display Logic**
        *   **Background:** Implement the logic to display one side of a word pair (e.g., the source word) as a flashcard question.
        *   **Acceptance Criteria:**
            *   The Practice Mode UI displays the source word of the current word pair.
            *   A "Show Answer" button or similar mechanism is present.
            *   UI elements for user interaction (e.g., revealing the answer) are clear.
        *   **Tech Suggestions:** Frontend component for flashcard display.

    3.  **Ticket: Flashcard Answer Reveal & Feedback**
        *   **Background:** Implement the logic to reveal the other side of the flashcard (the target word) and allow the user to indicate if they knew the answer correctly.
        *   **Acceptance Criteria:**
            *   Clicking "Show Answer" reveals the target word.
            *   Buttons like "Correct" and "Incorrect" are displayed.
            *   User selection (Correct/Incorrect) is captured.
            *   Feedback is visually presented (e.g., color change, message).
        *   **Tech Suggestions:** Frontend state updates, UI event handling.

    4.  **Ticket: Practice Session Navigation (Next Question)**
        *   **Background:** Implement the logic to move from one question to the next within the practice session.
        *   **Acceptance Criteria:**
            *   After providing feedback (Correct/Incorrect), clicking a "Next" button loads the next word pair in the session.
            *   The UI updates to display the next flashcard question.
            *   The session ends when all word pairs have been reviewed.
            *   A summary screen is displayed upon session completion (basic: "Session Complete!").
        *   **Tech Suggestions:** State management for current question index, session state.

    5.  **Ticket: API Endpoint for Practice Session Data** (Optional but Recommended)
        *   **Background:** Create a dedicated API endpoint to fetch word pairs specifically for a practice session, potentially allowing for future logic like selecting based on difficulty or category.
        *   **Acceptance Criteria:**
            *   A `GET /practice-session` endpoint exists.
            *   The endpoint returns a structured list of word pairs suitable for a practice session (e.g., randomized, limited count).
            *   The Practice Mode UI uses this endpoint instead of the generic `GET /word-pairs`.
        *   **Tech Suggestions:** API route definition, Database query optimization. 