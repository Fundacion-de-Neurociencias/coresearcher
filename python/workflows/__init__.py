"""
CoResearcher OS Research Workflows - Sprint 5
End-to-end scientific workflows that connect all system components.
"""

# Security tier: COMMUNITY — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "COMMUNITY"

from .research_scout import ResearchScout
from .hypothesis_discovery import HypothesisDiscovery
from .grant_writer import GrantWriter

__all__ = ["ResearchScout", "HypothesisDiscovery", "GrantWriter"]