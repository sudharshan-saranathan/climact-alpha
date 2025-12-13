# Encoding: utf-8
# Module name: opts
# Description: Default options and configurations for the application

# Imports (standard)
from __future__ import annotations
from dataclasses import dataclass
from enum import Flag


# Default options and configurations for the application
@dataclass(frozen=True)
class ClimactMeta:
    app_name: str = "Climact"
    app_version: str = "1.0.0"
    org_name: str = "EnERG Lab"
    org_domain: str = "www.energlab.com"


# Feature flags for enabling/disabling components
class ClimactFlags(Flag):
    NONE = 0
    ENABLE_AGENTS = 1
    ENABLE_SOLVER = 2


# Default flags
global_flags = ClimactFlags.NONE


# Exported names
__all__ = ["ClimactMeta", "ClimactFlags", "global_flags"]
