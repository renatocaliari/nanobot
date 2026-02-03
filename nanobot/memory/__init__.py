"""
Memory module for Nanobot

Provides persistent memory capabilities through Mem0.
Drop-in replacement for Supermemory - same API, better features.
"""

from .mem0_client import (
    Mem0Client,
    Mem0ClientSync,
)

# Backward compatibility - old imports now use Mem0
SupermemoryMCPClient = Mem0Client
SupermemoryMCPClientSync = Mem0ClientSync

__all__ = [
    "Mem0Client",
    "Mem0ClientSync",
    "SupermemoryMCPClient",  # Alias (uses Mem0 internally)
    "SupermemoryMCPClientSync",  # Alias (uses Mem0 internally)
]
