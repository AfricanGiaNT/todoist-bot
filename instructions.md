✅ Telegram-to-Todoist Bot Development Plan (v1)

📌 Project Summary

This bot will let you send free-text task messages via Telegram, which it will interpret using AI and upload to Todoist. It will categorize tasks based on a predefined structure, assign urgency and deadlines from your input, and allow task edits, deletions, and completions. You'll use Cursor AI for both development and AI logic. The bot will be hosted on a server.

⸻

🔧 Functional Requirements

1. Telegram Bot
	•	Receive messages in free text format.
	•	Respond with confirmations and error messages.
	•	Support commands:
	•	/add – Add new task
	•	/edit – Edit a task
	•	/delete – Delete a task
	•	/complete – Mark task as complete
	•	/help – Show command guide

2. AI Processing (via Cursor AI)
	•	Parse and understand free-text task input.
	•	Extract:
	•	Task title
	•	Due date (from input like "by Friday")
	•	Urgency (e.g. "urgent" → priority 1)
	•	Project/category/subcategory (from phrases like "work reports")
	•	Handle task deduplication and vague inputs with follow-up prompts.

3. Todoist Integration
	•	Authenticate using API token.
	•	Match or create projects and sections based on predefined structure.
	•	Upload task with:
	•	Title
	•	Due date
	•	Priority
	•	Project & Section

4. Task Management Features
	•	Support edit, delete, and complete actions by ID or fuzzy match.
	•	Show task summary on successful creation/update.
	•	Optionally list recent tasks with /tasks.

⸻

🧠 AI Prompt Design (Sample)

Prompt Template (for AI understanding):

Input: "Finish monthly report by Friday, urgent, work reports"
Output:
{
  "title": "Finish monthly report",
  "due_date": "2025-06-21",
  "priority": 1,
  "project": "Work",
  "section": "Reports"
}

⸻

🧱 Tech Stack

Component	Stack
Telegram Bot	python-telegram-bot or telebot
AI Logic	Cursor AI
Task Processing	Custom logic w/ natural language
Todoist API	REST (OAuth/Token)
Hosting	Node/Express or Python Flask API
Database (Optional)	JSON / Local (if needed)

⸻

🗂 File Structure (Suggested)

project-root/
├── instructions.md
├── main.py / index.js
├── cursor_logic/       # AI parsing
├── telegram_bot/
│   └── handlers.py
├── todoist/
│   └── api.py
└── config/
    └── projects.json   # Predefined project/section mapping

⸻

🪜 Development Milestones

Milestone	Description
1. Bot Setup	Telegram bot + webhook on server
2. Todoist Auth	Token integration and sample task creation
3. AI Parsing	Integrate Cursor to extract task data
4. Command Handling	Implement /add, /edit, /delete, /complete
5. Project Mapping	Load and use predefined categories/subcategories
6. Testing	End-to-end flow with sample tasks
7. Deployment	Finalize hosting + webhook setup

⸻

### ✅ Milestone 2 Plan: Todoist Authentication & Task Creation

This plan outlines the steps to integrate the Todoist API for authentication and create a sample task. We will use environment variables for secure API token storage and the official `todoist-api-python` library for API interactions.

1.  **Project Structure Setup:**
    *   Create the following directories to organize the code as per the initial plan:
        *   `todoist/`
        *   `config/`

2.  **Dependency Management:**
    *   Create a `requirements.txt` file.
    *   Add the necessary libraries:
        *   `python-telegram-bot` (for the future)
        *   `todoist-api-python` (for Todoist integration)
        *   `python-dotenv` (for managing environment variables)

3.  **Configuration:**
    *   Create a `.env` file to store the Todoist API token. **This file should not be committed to version control.**
    *   Create a `.gitignore` file and add `.env` to it.
    *   You will need to get your API token from the [Todoist Developer Console](https://todoist.com/app/settings/integrations/developer) and add it to the `.env` file as `TODOIST_API_TOKEN="YOUR_TOKEN_HERE"`.

4.  **Todoist API Module (`todoist/api.py`):**
    *   Create a new file `todoist/api.py`.
    *   Implement a function `create_task(api_token, task_content)` inside this file.
    *   This function will:
        *   Initialize the Todoist API client using the provided `api_token`.
        *   Use the client to create a new task with the given `task_content`.
        *   Include error handling for API exceptions.
        *   Return the created task object or `None` on failure.

5.  **Main Application Logic (`main.py`):**
    *   Update `main.py` to:
        *   Load environment variables from the `.env` file.
        *   Retrieve the `TODOIST_API_TOKEN`.
        *   Import the `create_task` function from `todoist.api`.
        *   Call `create_task` with a sample task content (e.g., "Buy milk") to test the integration.
        *   Print a confirmation message with the new task's details upon success.

⸻

### 🚀 Milestone 4 Plan: Command Handling

This plan focuses on implementing the core command structure for the Telegram bot. We'll start with `/add` and `/complete` for initial functionality, alongside `/start` and `/help`. For simplicity and to follow an incremental approach, task selection for the `/complete` command will be based on an exact title match. More complex commands like `/edit` and `/delete`, and more advanced features like fuzzy matching or AI-based parsing, will be deferred to later milestones.

1.  **Refactor `main.py` for Telegram Bot Integration:**
    *   Restructure `main.py` to initialize and run the `python-telegram-bot` `Application`.
    *   The main execution block will now start the bot to poll for updates, rather than running a one-off script.
    *   Create `telegram_bot/handlers.py` to house the logic for command handlers.

2.  **Implement `/start` and `/help` Handlers:**
    *   **Code:** In `telegram_bot/handlers.py`, create `start()` and `help_command()` functions.
        *   `start`: Responds with a welcome message.
        *   `help_command`: Lists the available commands.
    *   **Integrate:** In `main.py`, register these functions as command handlers.
    *   **Test:** Create `test_main.py` to write unit tests that verify the responses for `/start` and `/help`.

3.  **Implement Simple `/add` Command:**
    *   **Code (`telegram_bot/handlers.py`):**
        *   Create an `add_task()` handler that extracts the task description from the user's message.
        *   It will call the existing `todoist.api.create_task` function.
        *   It will reply with a confirmation message upon success or an error if the API call fails.
    *   **Integrate:** Register the `/add` command handler in `main.py`.
    *   **Test:** Add a test that mocks `create_task` and verifies it's called with the correct task content.

4.  **Implement Task Search and Completion Logic:**
    *   **Code (`todoist/api.py`):**
        *   Create `find_task_by_content(content)`: Fetches active tasks and returns the first task object with an exact content match.
        *   Create `close_task(task_id)`: Closes a task by its ID.
    *   **Code (`telegram_bot/handlers.py`):**
        *   Create a `complete_task()` handler.
        *   This handler will use `find_task_by_content` to get the task ID.
        *   If a task is found, it will call `close_task` and confirm completion to the user.
        *   If not found, it will send a "Task not found" message.
    *   **Integrate:** Register the `/complete` command handler in `main.py`.
    *   **Test:** Write a test to simulate the `/complete` command, mocking the new functions in `todoist/api.py` to verify the logic.

#### **Alternative Approach**

*   **Stateful Conversation Handlers:** Instead of simple command handlers, we could use `python-telegram-bot`'s `ConversationHandler`. For example, `/edit` could trigger a conversation where the bot asks "Which task would you like to edit?" and then "What should be the new content?". This is more robust and user-friendly but adds significant complexity. The current plan prioritizes a stateless, simpler implementation first.

#### **Critique of Plan**

*   **Completeness:** This plan establishes the bot's core command-response loop and implements the most essential features (`add`, `complete`). It correctly defers more complex features.
*   **Simplicity:** Relying on an "exact match" for task content is a limitation. If multiple tasks share the same name, the bot will only act on the first one it finds. This is an acceptable trade-off for this stage of development. We will address this by implementing task selection by ID in a future milestone.
*   **Dependencies:** The plan correctly identifies the new functions required in `todoist/api.py` and outlines the test-driven approach for each new piece of functionality.

⸻

### 🧩 Milestone 5 Plan: Project Mapping

This plan covers loading and using a predefined project/section structure from a JSON file to automatically categorize tasks. This will replace the AI parsing placeholder with a keyword-based mapping system as a first iteration.

1.  **Define Project/Section Mapping Configuration:**
    *   **Action:** Create `config/projects.json`. This file will define keywords that map user input to Todoist projects and sections.
    *   **Structure:** The JSON will contain projects, their associated keywords, and nested sections with their own keywords.
    *   **Testing:** No direct tests for the JSON file itself, but its structure will be validated by the loader tests.

2.  **Implement Configuration Loader and Parser:**
    *   **File:** Create a new module `config/loader.py`.
    *   **Code (`config/loader.py`):**
        *   `load_project_mappings()`: Reads `config/projects.json` and returns the content.
        *   `find_project_section(text_input, mappings)`: Takes the user's message and the mappings, finds the first matching keyword, and returns the corresponding `(project_name, section_name)`. It will default to a pre-defined location if no keywords are found.
    *   **Testing (`test_main.py`):** Write unit tests for `find_project_section` to ensure it correctly identifies projects and sections from sample sample text inputs.

3.  **Enhance Todoist API for Projects and Sections:**
    *   **File:** `todoist/api.py`.
    *   **Code:**
        *   Modify `create_task` to accept `project_name` and `section_name` as arguments.
        *   Implement helper functions to get or create projects and sections by name, returning their IDs. These functions will handle the necessary API calls to prevent duplicates.
        *   The updated `create_task` will use these helpers to get the correct IDs before creating the task.
    *   **Testing:** Add tests to mock the Todoist API client and verify that `create_task` attempts to find/create projects and sections before creating the task itself.

4.  **Integrate Project Mapping into `/add` Command:**
    *   **File:** `telegram_bot/handlers.py`.
    *   **Code (`add_task` handler):**
        *   Load the mappings using `load_project_mappings`.
        *   Use `find_project_section` to determine the project and section from the user's input.
        *   Call the refactored `todoist.api.create_task` with the task content and the determined project/section names.
    *   **Testing:** Update the test for the `/add` command to verify that it calls the new `config` and `todoist` functions correctly.

#### **Alternative Approach**

*   **Direct AI-based Categorization:** Instead of a keyword mapping file, we could have the AI directly return the `project` and `section` in its structured output (as shown in the initial plan). This would make the bot more flexible and intelligent, as it could handle phrases like "for my work report" without needing explicit keywords. However, this adds complexity in prompt engineering and dependency on the AI model's reliability. The keyword approach is a more deterministic and robust starting point.

#### **Critique of Plan**

*   **Completeness:** The plan provides a full, test-driven path to implementing project/section mapping, from configuration to final integration.
*   **Simplicity:** The keyword-based approach is a pragmatic first step before introducing a full AI-parsing model. It avoids AI-related complexities for now. The "first match wins" logic for keyword detection is a simple and predictable rule.
*   **Potential Issues:** The need to fetch/create projects and sections on-the-fly will add latency to task creation. For this stage, this is acceptable. A caching mechanism for project/section IDs can be added later as an optimization.

⸻

🧪 Self-Critique
	•	✅ Completeness: Covers all major functionality including parsing, task management, and integration.
	•	⚠️ Gaps: Error handling flows and how user clarifications are captured in AI response still need detailed design.
	•	🧠 Suggestion: Add a fallback step where if parsing fails (e.g., "do the thing"), AI can ask follow-up questions in chat.

⸻

✅ Final Instructions

This will be saved as instructions.md and should be referenced during each step of development to stay aligned. Feel free to regenerate when new features or changes are introduced.

--- @execution-plan.mdc 