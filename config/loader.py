import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def load_project_mappings():
    """Loads the project and section mappings from config/projects.json."""
    config_path = Path(__file__).parent / "projects.json"
    with open(config_path, "r") as f:
        return json.load(f)

def find_project_section(text_input, mappings):
    """
    Finds the project and section for a given text input based on keywords.
    It prioritizes section keywords over project keywords.
    """
    text_lower = text_input.lower()
    logger.debug(f"Searching for project/section in: '{text_lower}'")

    # First, check for section keywords for a more specific match
    for project_name, project_data in mappings.items():
        if "sections" in project_data:
            for section_name, section_keywords in project_data["sections"].items():
                if any(keyword.lower() in text_lower for keyword in section_keywords):
                    logger.debug(f"Found section keyword match: P='{project_name}', S='{section_name}'")
                    return project_name, section_name

    # If no section keywords match, check for project-level keywords
    for project_name, project_data in mappings.items():
        if "keywords" in project_data and any(
            keyword.lower() in text_lower for keyword in project_data["keywords"]
        ):
            # Default to a general section if one is not specified
            logger.debug(f"Found project keyword match: P='{project_name}'")
            return project_name, "General"

    logger.debug("No keywords matched. Defaulting to Inbox.")
    return "Inbox", None  # Default project if no keywords match 