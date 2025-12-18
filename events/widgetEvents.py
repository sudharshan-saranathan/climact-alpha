# Encoding: utf-8
# Module name: events
# Description: Event handling utilities for the Climact application

# Imports (standard)
from __future__ import annotations
from typing import Dict, Any

# Imports (third party)
from PySide6 import QtCore, QtWidgets


# Event handling utilities class
class EventBus(QtCore.QObject):
    """
    A utility class for handling custom events in the Climact application.
    """

    _instance: "EventBus | None" = None  # Singleton instance

    # Custom signals:
    instruction = QtCore.Signal(dict)

    # Singleton pattern implementation
    def __new__(cls) -> "EventBus":
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
        return cls._instance

    # Constructor
    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        super().__init__()
        self._initialized = True

    @classmethod
    def instance(cls) -> EventBus:
        """
        Get the singleton instance of the EventBus.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def send(self, command: str, payload: Any = None) -> None:
        """
        Emit a custom event with an optional payload.
        """
        message: Dict[str, Any] = {
            "command": command,
            "payload": payload,
        }  # Wrap in dict for extensibility

        self.instruction.emit(message)
