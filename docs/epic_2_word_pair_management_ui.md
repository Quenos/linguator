# Epic 2: Word Pair Management UI

*   **Goal:** Enable users to visually interact with their word lists: adding new pairs, viewing existing ones, editing, and deleting them through a user-friendly interface.
*   **Tickets:**

    1.  **Ticket: Word Pair List View UI**
        *   **Background:** Create the main UI component to display the list of existing word pairs fetched from the API. This view should be clear and allow easy scanning of words.
        *   **Acceptance Criteria:**
            *   A dedicated page/section exists for viewing word pairs.
            *   The UI calls the `GET /word-pairs` endpoint on load.
            *   Word pairs are displayed in a list or table format, showing source word, target word, and category.
            *   Basic loading and error states are handled.
        *   **Tech Suggestions:** React/Vue/Svelte/HTMX (Frontend Framework), CSS/TailwindCSS (Styling).

    2.  **Ticket: Add New Word Pair Form UI**
        *   **Background:** Implement the form interface for users to input new word pairs (source, target, category, example sentence).
        category are grammatical names like: Noun, pronoun, verb etc etc
        All fields are required.
        *   **Acceptance Criteria:**
            *   A form with input fields for source word, target word, category (dropdown/select), and example sentence is displayed.
            *   A "Save" button calls the `POST /word-pairs` endpoint with the form data.
            *   Basic client-side validation (e.g., required fields) is present.
            *   Successful submission clears the form and potentially updates the list view.
            *   User feedback is provided on success or failure.
        *   **Tech Suggestions:** HTML forms, Frontend Framework components.

    3.  **Ticket: Edit Word Pair Modal/View UI**
        *   **Background:** Create the UI functionality to allow editing of an existing word pair. This could be a modal or a separate edit view.
        *   **Acceptance Criteria:**
            *   An "Edit" button/icon is available for each word pair in the list view.
            *   Clicking "Edit" populates a form (similar to the Add form) with the selected word pair's data (fetched via `GET /word-pairs/{id}`).
            *   A "Save" button calls the `PUT /word-pairs/{id}` endpoint with the updated data.
            *   User feedback is provided on success or failure.
            *   The list view is updated upon successful edit.
        *   **Tech Suggestions:** Modals, Separate routing, Frontend state management.

    4.  **Ticket: Delete Word Pair Functionality UI**
        *   **Background:** Implement the UI mechanism for deleting a word pair, including a confirmation step.
        *   **Acceptance Criteria:**
            *   A "Delete" button/icon is available for each word pair in the list view.
            *   Clicking "Delete" prompts the user for confirmation (e.g., "Are you sure?").
            *   Upon confirmation, the `DELETE /word-pairs/{id}` endpoint is called.
            *   The list view is updated upon successful deletion.
            *   User feedback is provided.
        *   **Tech Suggestions:** Confirmation dialogs/modals.

    5.  **Ticket: Basic Word Pair Search/Filter UI**
        *   **Background:** Implement a simple search input or filter mechanism (e.g., by category) on the Word Pair List View UI.
        *   **Acceptance Criteria:**
            *   A search input field is present on the list view page.
            *   Typing in the search field filters the displayed list based on source or target word (client-side or server-side via API).
            *   (Optional) A dropdown allows filtering by category.
            *   The list updates dynamically based on the search/filter criteria.
        *   **Tech Suggestions:** Client-side filtering (JS), Server-side filtering (API parameter `?search=...` or `?category=...`). 