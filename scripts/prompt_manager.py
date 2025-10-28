"""
Prompt Manager for Translation System
Loads and manages prompts from separate files for better maintainability.
"""

from pathlib import Path
from typing import Dict, Any

class PromptManager:
    """Manages prompt templates for the translation system."""

    def __init__(self, prompts_dir: str = "prompts"):
        """Initialize the prompt manager.

        Args:
            prompts_dir: Directory containing prompt files
        """
        self.prompts_dir = Path(prompts_dir)
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> Dict[str, str]:
        """Load all prompt files from the prompts directory.

        Returns:
            Dictionary mapping prompt names to their content
        """
        prompts = {}

        if not self.prompts_dir.exists():
            raise FileNotFoundError(f"Prompts directory not found: {self.prompts_dir}")

        # Load each .txt file in the prompts directory
        for prompt_file in self.prompts_dir.glob("*.txt"):
            prompt_name = prompt_file.stem  # filename without extension
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompts[prompt_name] = f.read().strip()
            except Exception as e:
                print(f"Warning: Could not load prompt file {prompt_file}: {e}")

        # Validate required prompts
        required = ['system', 'translation']
        for req in required:
            if req not in prompts:
                raise ValueError(f"Required prompt file missing: {req}.txt")

        return prompts

    def get_system_prompt(self) -> str:
        """Get the system prompt for the LLM.

        Returns:
            System prompt string
        """
        return self.prompts['system']

    def get_translation_prompt(self, content: str, metadata: Dict[str, Any]) -> str:
        """Get the translation prompt with filled variables.

        Args:
            content: The content to translate
            metadata: Metadata about the content (url, title, authors, etc.)

        Returns:
            Formatted translation prompt
        """
        # Prepare variables for the prompt
        authors_str = ', '.join(metadata['authors']) if metadata['authors'] else 'Unknown'

        # No content length limit - let the API handle token limits
        # The API will return an error if the content is too long
        content_to_translate = content

        # Fill in the prompt template
        prompt = self.prompts['translation'].format(
            url=metadata['url'],
            title=metadata['title'],
            authors=authors_str,
            content=content_to_translate,
            translated_title=metadata['title'],
            appropriate_subcategory='General',  # Will be determined by LLM
            tag1='tag1', tag2='tag2', tag3='tag3',  # Will be determined by LLM
            original_english_title=metadata['title'],
            author_name=authors_str
        )

        return prompt

    def get_validation_prompt(self, original: str, translated: str) -> str:
        """Get the validation prompt for checking translation quality.

        Args:
            original: Original text excerpt
            translated: Translated text excerpt

        Returns:
            Formatted validation prompt
        """
        if 'validation' not in self.prompts:
            return None

        return self.prompts['validation'].format(
            original=original[:1000],  # Use excerpt for validation
            translated=translated[:1000]
        )

    def reload_prompts(self):
        """Reload all prompts from disk.

        Useful for development when prompts are being edited.
        """
        self.prompts = self._load_prompts()
        print(f"Reloaded {len(self.prompts)} prompts from {self.prompts_dir}")