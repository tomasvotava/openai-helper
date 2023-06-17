"""Context provider scans specified directory and gathers files based on specified configuration.
This context can then be provided as a context for OpenAI models.
"""

import logging
import re
from pathlib import Path
from typing import Generator

import tiktoken

logger = logging.getLogger(__name__)


class ContextProvider:
    """Context provider scans specified directory and gathers files based on specified configuration.
    This context can then be provided as a context for OpenAI models.
    """

    def __init__(
        self,
        directory: str | Path,
        *,
        regex_whitelist: str | None = None,
        regex_blacklist: str | None = None,
        allow_hidden: bool = False,
        recursive: bool = True,
        allow_hidden_subdirectories: bool = False,
        regex_path_whitelist: str | None = None,
        regex_path_blacklist: str | None = None,
        skip_unreadable: bool = True,
        skip_empty: bool = False,
    ):
        self.directory = Path(directory)
        self.regex_whitelist = re.compile(regex_whitelist) if regex_whitelist else None
        self.regex_blacklist = re.compile(regex_blacklist) if regex_blacklist else None
        self.allow_hidden = allow_hidden
        self.recursive = recursive
        self.allow_hidden_subdirectories = allow_hidden_subdirectories
        self.regex_path_whitelist = re.compile(regex_path_whitelist) if regex_path_whitelist else None
        self.regex_path_blacklist = re.compile(regex_path_blacklist) if regex_path_blacklist else None
        self.skip_unreadable = skip_unreadable
        self.skip_empty = skip_empty

    def _file_matches(self, path: Path) -> bool:
        """Check if file matches the provider's configuration"""
        if not self.allow_hidden and path.name.startswith("."):
            return False
        if self.regex_whitelist and not self.regex_whitelist.search(path.name):
            return False
        if self.regex_blacklist and self.regex_blacklist.search(path.name):
            return False
        if self.regex_path_whitelist and not self.regex_path_whitelist.search(str(path)):
            return False
        if self.regex_path_blacklist and self.regex_path_blacklist.search(str(path)):
            return False
        return True

    def iter_file_paths(self, top: Path | None = None) -> Generator[Path, None, None]:
        """Iterate over all file paths in the directory (recursively), yield files that match the
        provider's configuration"""
        top = top or self.directory
        for path in top.iterdir():
            if path.is_file():
                if self._file_matches(path):
                    yield path
            elif self.recursive and path.is_dir():
                if self.allow_hidden_subdirectories or not path.name.startswith("."):
                    yield from self.iter_file_paths(path)

    def iter_files(self, top: Path | None = None) -> Generator[tuple[int, Path, str], None, None]:
        """Iterate over all matching files from the directory tree. It yields tuples
        of (lenght in tokens, path, file content)"""
        encoding = tiktoken.encoding_for_model("gpt-4")
        for path in self.iter_file_paths(top):
            try:
                content = path.read_text().strip()
            except UnicodeDecodeError:
                logger.error("Failed to read file %s", path)
                if self.skip_unreadable:
                    continue
                raise
            if self.skip_empty and not content:
                continue
            tokens = len(encoding.encode(content, disallowed_special=()))
            yield tokens, path, content

    def calculate_tokens(self, top: Path | None = None) -> int:
        """Calculate total number of tokens in all matching files"""
        return sum(tokens for tokens, _, __ in self.iter_files(top))

    def get_context(self) -> str:
        """Get a string containing the context to be passed on to the model itself. It contains a relative
        path to each file along with its content"""
        return "\n\n\n".join(
            f"// File '{path.relative_to(self.directory)}'\n{content}\n" for _, path, content in self.iter_files()
        )
