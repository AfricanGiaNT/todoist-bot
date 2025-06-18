import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from telegram import Update, Message, User, Chat
from telegram.ext import ContextTypes
import asyncio

from telegram_bot import handlers
from config.loader import find_project_section

class TestHandlers(unittest.TestCase):
    def _create_mock_update_context(self, text: str):
        """Helper to create mock Update and Context objects."""
        update = MagicMock(spec=Update)
        update.message = MagicMock(spec=Message)
        update.message.from_user = MagicMock(spec=User)
        update.message.chat = MagicMock(spec=Chat)
        update.message.text = text
        update.message.reply_text = AsyncMock()
        update.message.reply_html = AsyncMock()
        
        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.args = text.split(' ')[1:] if ' ' in text else []
        
        return update, context

    def test_start(self):
        """Test the /start command handler."""
        async def run():
            update, context = self._create_mock_update_context("/start")
            await handlers.start(update, context)
            update.message.reply_html.assert_called_once_with(
                "Welcome to the Todoist Bot! Add tasks by sending a message. Use /help for more commands."
            )
        asyncio.run(run())

    def test_help_command(self):
        """Test the /help command handler."""
        async def run():
            update, context = self._create_mock_update_context("/help")
            await handlers.help_command(update, context)
            update.message.reply_text.assert_called_once()
        asyncio.run(run())

    @patch('telegram_bot.handlers.find_project_section')
    @patch('telegram_bot.handlers.create_task')
    def test_add_task_handler_success(self, mock_create_task, mock_find_project_section):
        """Test add_task_handler with project/section mapping."""
        async def run():
            update, context = self._create_mock_update_context("/add buy some work food")
            
            mock_task = MagicMock()
            mock_task.content = "buy some work food"
            mock_create_task.return_value = mock_task
            mock_find_project_section.return_value = ("Work", "Groceries")

            async def mock_to_thread(func, *args, **kwargs):
                return func(*args, **kwargs)

            with patch('asyncio.to_thread', new=mock_to_thread):
                await handlers.add_task_handler(update, context)

            mock_find_project_section.assert_called_once()
            mock_create_task.assert_called_once_with(
                unittest.mock.ANY,
                "buy some work food",
                project_name="Work",
                section_name="Groceries"
            )
            update.message.reply_text.assert_called_once_with("Task 'buy some work food' added successfully!")

        asyncio.run(run())

    @patch('telegram_bot.handlers.complete_task')
    @patch('telegram_bot.handlers.find_task_by_content')
    def test_complete_task_handler_success(self, mock_find_task, mock_complete_task):
        """Test the complete_task_handler for a successful task completion."""
        async def run():
            update, context = self._create_mock_update_context("/complete Finish the report")
            
            mock_found_task = MagicMock()
            mock_found_task.content = "Finish the report"
            mock_found_task.id = "task123"
            mock_find_task.return_value = mock_found_task
            mock_complete_task.return_value = True

            async def mock_to_thread(func, *args, **kwargs):
                return func(*args, **kwargs)

            with patch('asyncio.to_thread', new=mock_to_thread):
                await handlers.complete_task_handler(update, context)

            mock_find_task.assert_called_once_with(unittest.mock.ANY, "Finish the report")
            mock_complete_task.assert_called_once_with(unittest.mock.ANY, "task123")
            update.message.reply_text.assert_called_once_with("Task 'Finish the report' completed!")

        asyncio.run(run())

    @patch('telegram_bot.handlers.find_task_by_content')
    def test_complete_task_handler_not_found(self, mock_find_task):
        """Test the complete_task_handler when the task is not found."""
        async def run():
            update, context = self._create_mock_update_context("/complete Non-existent task")
            mock_find_task.return_value = None

            async def mock_to_thread(func, *args, **kwargs):
                return func(*args, **kwargs)

            with patch('asyncio.to_thread', new=mock_to_thread):
                await handlers.complete_task_handler(update, context)
            
            mock_find_task.assert_called_once_with(unittest.mock.ANY, "Non-existent task")
            update.message.reply_text.assert_called_once_with("Task 'Non-existent task' not found.")

        asyncio.run(run())

    def test_add_task_with_separator(self):
        """Test adding a task using a separator for categorization."""
        async def run():
            # Simulate a command using the new format
            update, context = self._create_mock_update_context(
                "/add Fix the pump - farming guide"
            )

            mock_task = MagicMock()
            mock_task.content = "Fix the pump"

            with patch('telegram_bot.handlers.create_task') as mock_create_task, \
                 patch('asyncio.to_thread') as mock_to_thread:
                
                mock_create_task.return_value = mock_task
                
                async def passthrough(func, *args, **kwargs):
                    return func(*args, **kwargs)
                mock_to_thread.side_effect = passthrough

                await handlers.add_task_handler(update, context)

                # Verify create_task is called with the clean title and correct project
                mock_create_task.assert_called_once_with(
                    unittest.mock.ANY,
                    "Fix the pump",
                    project_name="AI Automations",
                    section_name="Farming-guide"
                )
                update.message.reply_text.assert_called_once_with("Task 'Fix the pump' added successfully!")

        asyncio.run(run())

    def test_add_task_to_ai_automations_project(self):
        """Test adding a task that maps to the 'AI Automations' project and a specific section."""
        async def run():
            # Simulate a command with keywords for project "AI" and section "guide"
            update, context = self._create_mock_update_context("/add Create a new guide for AI farming")
            
            mock_task = MagicMock()
            mock_task.content = "Create a new guide for AI farming"
            
            # Patch the backend functions
            with patch('telegram_bot.handlers.create_task') as mock_create_task, \
                 patch('asyncio.to_thread') as mock_to_thread:

                mock_create_task.return_value = mock_task
                
                # Make to_thread call the function directly for the test
                async def passthrough(func, *args, **kwargs):
                    return func(*args, **kwargs)
                mock_to_thread.side_effect = passthrough

                await handlers.add_task_handler(update, context)

                # Verify that create_task was called with the correct project and section
                mock_create_task.assert_called_once_with(
                    unittest.mock.ANY,
                    "Create a new guide for AI farming",
                    project_name="AI Automations",
                    section_name="Farming-guide"
                )
                update.message.reply_text.assert_called_once_with("Task 'Create a new guide for AI farming' added successfully!")

        asyncio.run(run())


class TestConfigLoader(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Load mappings once for all tests in this class."""
        cls.mappings = {
            "Work": {
                "keywords": ["work", "office", "meeting"],
                "sections": {
                    "Reports": ["report", "analysis", "summary"],
                    "General": ["task", "misc"]
                }
            },
            "Personal": {
                "keywords": ["personal", "home", "family"],
                "sections": {
                    "Groceries": ["buy", "groceries", "food"],
                    "Errands": ["errands", "chores"]
                }
            }
        }

    def test_find_project_and_section(self):
        """Test finding a specific project and section."""
        text = "I need to write a report for work"
        project, section = find_project_section(text, self.mappings)
        self.assertEqual(project, "Work")
        self.assertEqual(section, "Reports")

    def test_find_project_with_default_section(self):
        """Test finding a project and using the default section logic."""
        text = "A new work task"
        project, section = find_project_section(text, self.mappings)
        self.assertEqual(project, "Work")
        self.assertEqual(section, "General")

    def test_default_project_fallback(self):
        """Test the fallback to the default project when no keywords match."""
        text = "Some random thing to do"
        project, section = find_project_section(text, self.mappings)
        self.assertEqual(project, "Inbox")
        self.assertIsNone(section)
        
    def test_case_insensitivity(self):
        """Test that keyword matching is case-insensitive."""
        text = "BUY some FOOD for the family"
        project, section = find_project_section(text, self.mappings)
        self.assertEqual(project, "Personal")
        self.assertEqual(section, "Groceries")

    def test_find_personal_errands(self):
        """Test finding a personal errand task."""
        text = "run some personal errands"
        project, section = find_project_section(text, self.mappings)
        self.assertEqual(project, "Personal")
        self.assertEqual(section, "Errands")

    def test_config_keyword_case_insensitivity(self):
        """Test that keywords from the config are matched case-insensitively."""
        # Use a custom mapping with an uppercase keyword
        custom_mappings = {
            "Work": {
                "keywords": ["work"],
                "sections": {
                    "Reports": ["REPORT", "analysis"]
                }
            }
        }
        text = "I need to write a report for work"
        project, section = find_project_section(text, custom_mappings)
        self.assertEqual(project, "Work")
        self.assertEqual(section, "Reports")


class TestTodoistApi(unittest.TestCase):
    @patch('todoist.api.TodoistAPI')
    def test_get_or_create_project_with_emojis(self, MockTodoistAPI):
        """
        Tests that a project with emojis in its name can be matched
        with text that does not contain emojis.
        """
        mock_api_instance = MockTodoistAPI.return_value
        
        mock_project = MagicMock()
        mock_project.id = '12345'
        mock_project.name = 'Ai Automations 🤖💻'
        
        mock_api_instance.get_projects.return_value = [[mock_project]]
        
        # Import the function here to make sure we're testing the right thing
        from todoist.api import _get_or_create_project_by_name

        project_id = _get_or_create_project_by_name(mock_api_instance, "ai automations")
        
        self.assertEqual(project_id, '12345')
        mock_api_instance.add_project.assert_not_called()

    @patch('todoist.api.TodoistAPI')
    def test_get_or_create_section_with_emojis(self, MockTodoistAPI):
        """
        Tests that a section with emojis in its name can be matched
        with text that does not contain emojis.
        """
        mock_api_instance = MockTodoistAPI.return_value
        
        mock_section = MagicMock()
        mock_section.id = '67890'
        mock_section.name = 'My Section ✨'
        
        mock_api_instance.get_sections.return_value = [[mock_section]]
        
        from todoist.api import _get_or_create_section_by_name

        section_id = _get_or_create_section_by_name(
            mock_api_instance, "my section", project_id="123"
        )
        
        self.assertEqual(section_id, '67890')
        mock_api_instance.add_section.assert_not_called()


if __name__ == '__main__':
    unittest.main() 