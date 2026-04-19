"""Base agent class with common functionality."""

import logging
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Base class for all AutoHome agents."""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"autohome.agents.{name}")

    @abstractmethod
    async def run(self, **kwargs):
        """Execute the agent's main task."""

    def log_start(self):
        self.logger.info("Agent [%s] started", self.name)

    def log_complete(self, result_count: int = 0):
        self.logger.info("Agent [%s] completed. Results: %d", self.name, result_count)

    def log_error(self, error: Exception):
        self.logger.error("Agent [%s] error: %s", self.name, error, exc_info=True)
