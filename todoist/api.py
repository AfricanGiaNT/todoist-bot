import os
import logging
import re
from todoist_api_python.api import TodoistAPI

logger = logging.getLogger(__name__)

def _sanitize_name(name: str) -> str:
    """Removes emojis and extra whitespace from a string."""
    # Remove any character that is not a letter, number, or whitespace
    sanitized = re.sub(r'[^\w\s]', '', name)
    # Replace multiple whitespace characters with a single space
    return re.sub(r'\s+', ' ', sanitized).strip()

def _get_or_create_project_by_name(api: TodoistAPI, project_name: str):
    """Finds a project by name or creates it if it doesn't exist."""
    if not project_name:
        return None
    try:
        projects_pages = api.get_projects()
        sanitized_target_name = _sanitize_name(project_name).lower()

        for page in projects_pages:
            for project in page:
                if _sanitize_name(project.name).lower() == sanitized_target_name:
                    return project.id
        # If not found, create it
        logger.info(f"Project '{project_name}' not found. Creating it.")
        new_project = api.add_project(name=project_name)
        return new_project.id
    except Exception as e:
        logger.error(f"Error handling project '{project_name}': {e}", exc_info=True)
        return None

def _get_or_create_section_by_name(api: TodoistAPI, section_name: str, project_id: str):
    """Finds a section by name within a project or creates it."""
    if not section_name or not project_id:
        return None
    try:
        sections_pages = api.get_sections(project_id=project_id)
        sanitized_target_name = _sanitize_name(section_name).lower()

        for page in sections_pages:
            for section in page:
                if _sanitize_name(section.name).lower() == sanitized_target_name:
                    return section.id
        # If not found, create it
        logger.info(f"Section '{section_name}' not found in project. Creating it.")
        new_section = api.add_section(name=section_name, project_id=project_id)
        return new_section.id
    except Exception as e:
        logger.error(f"Error handling section '{section_name}': {e}", exc_info=True)
        return None

def create_task(api_token: str, task_content: str, project_name: str = None, section_name: str = None, due_string: str = None, priority: int = None):
    """
    Creates a new task in Todoist, automatically handling projects and sections.
    """
    try:
        api = TodoistAPI(api_token)
        project_id = None
        if project_name:
            project_id = _get_or_create_project_by_name(api, project_name)

        section_id = None
        if project_id and section_name:
            section_id = _get_or_create_section_by_name(api, section_name, project_id)

        task = api.add_task(
            content=task_content,
            project_id=project_id,
            section_id=section_id,
            due_string=due_string,
            priority=priority
        )
        return task
    except Exception as e:
        logger.error(f"Error creating task: {e}", exc_info=True)
        return None

def find_tasks_by_name(api_token: str, task_name: str):
    """
    Finds active tasks that contain the given name (case-insensitive).
    """
    try:
        api = TodoistAPI(api_token)
        tasks_pages = api.get_tasks()
        found_tasks = []

        for page in tasks_pages:
            for task in page:
                if hasattr(task, 'content') and task_name.strip().lower() in task.content.strip().lower():
                    found_tasks.append(task)
        return found_tasks
    except Exception as e:
        logger.error(f"Error finding tasks: {e}", exc_info=True)
        return []

def find_task_by_content(api_token: str, task_content: str):
    """
    Finds an active task by its exact content.
    """
    try:
        api = TodoistAPI(api_token)
        tasks_pages = api.get_tasks()
        for page in tasks_pages:
            for task in page:
                if task.content.strip() == task_content.strip():
                    return task
        return None
    except Exception as e:
        logger.error(f"Error finding task by content: {e}", exc_info=True)
        return None

def update_task_content(api_token: str, task_id: str, new_content: str):
    """
    Updates the content of an existing task.
    """
    try:
        api = TodoistAPI(api_token)
        is_success = api.update_task(task_id=task_id, content=new_content)
        return is_success
    except Exception as e:
        logger.error(f"Error updating task: {e}", exc_info=True)
        return False

def delete_task(api_token: str, task_id: str):
    """
    Deletes a task.
    """
    try:
        api = TodoistAPI(api_token)
        is_success = api.delete_task(task_id=task_id)
        return is_success
    except Exception as e:
        logger.error(f"Error deleting task: {e}", exc_info=True)
        return False

def complete_task(api_token: str, task_id: str):
    """
    Marks a task as complete.
    """
    try:
        api = TodoistAPI(api_token)
        is_success = api.close_task(task_id=task_id)
        return is_success
    except Exception as e:
        logger.error(f"Error completing task: {e}", exc_info=True)
        return False 