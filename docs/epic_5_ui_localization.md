# Epic 5: UI Localization Implementation

*   **Goal:** Translate all user-facing text in the application UI into the target languages: English (EN), Italian (IT), and Russian (RU), ensuring a consistent experience across languages.
*   **Tickets:**

    1.  **Ticket: Extract UI Strings & Create Translation Files**
        *   **Background:** Identify all user-facing strings in the existing UI components (Word Pair Management, Practice Mode, Progress Tracking, common elements). Extract these into the translation file format chosen in the Foundation epic. Create initial EN, IT, RU files.
        *   **Acceptance Criteria:**
            *   All hardcoded UI strings are replaced with references to the localization framework (e.g., `t('greeting')`).
            *   Translation files (e.g., `en.json`, `it.json`, `ru.json`) are created containing keys for all extracted strings.
            *   English translations are complete.
            *   Placeholders are present for Italian and Russian translations.
        *   **Tech Suggestions:** Manual extraction or i18n tooling/scripts.

    2.  **Ticket: Implement Language Selection Mechanism**
        *   **Background:** Provide a way for the user (or the application) to select the desired language and ensure the localization framework uses the correct translations.
        *   **Acceptance Criteria:**
            *   A UI element (e.g., dropdown, buttons) allows selecting EN, IT, or RU.
            *   Selecting a language updates the application's locale setting.
            *   The UI re-renders with strings from the selected language's translation file.
            *   The selected language preference persists (e.g., in local storage or user settings if applicable).
        *   **Tech Suggestions:** Frontend state management, Local Storage, Context API/Redux.

    3.  **Ticket: Populate Italian Translations**
        *   **Background:** Fill in the Italian (`it`) translation file with accurate translations for all keys identified in the extraction step.
        *   **Acceptance Criteria:**
            *   The `it.json` (or equivalent) file contains Italian translations for all UI strings.
            *   Selecting "Italian" in the UI displays the application interface in Italian.
        *   **Tech Suggestions:** Collaboration with translators or using translation services.

    4.  **Ticket: Populate Russian Translations**
        *   **Background:** Fill in the Russian (`ru`) translation file with accurate translations for all keys identified in the extraction step.
        *   **Acceptance Criteria:**
            *   The `ru.json` (or equivalent) file contains Russian translations for all UI strings.
            *   Selecting "Russian" in the UI displays the application interface in Russian.
        *   **Tech Suggestions:** Collaboration with translators or using translation services. 