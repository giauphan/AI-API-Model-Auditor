"""
Module for representing proxy chain hops and analyzing observations across hops.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class HopObservation(BaseModel):
    """
    Observations for a specific hop in a proxy chain.
    """

    model_config = ConfigDict(extra="forbid")

    changed_model_id: Optional[str] = None
    inserted_prompts: List[str] = Field(default_factory=list)
    rewritten_headers: Dict[str, str] = Field(default_factory=dict)
    protocol_translation: Optional[str] = None
    fallback_event: Optional[str] = None


class Hop(BaseModel):
    """
    Represents a single hop in a proxy chain.
    """

    model_config = ConfigDict(extra="forbid")

    hop_id: str
    observations: HopObservation = Field(default_factory=HopObservation)


class ProxyChain(BaseModel):
    """
    Represents a chain of proxy hops.
    """

    model_config = ConfigDict(extra="forbid")

    hops: List[Hop] = Field(default_factory=list)

    def add_hop(self, hop: Hop) -> None:
        """
        Appends a hop to the proxy chain.
        """
        self.hops.append(hop)

    def get_hop(self, hop_id: str) -> Optional[Hop]:
        """
        Retrieves a hop by its ID.
        """
        for hop in self.hops:
            if hop.hop_id == hop_id:
                return hop
        return None

    def compare_chains(self, other: "ProxyChain") -> bool:
        """
        Compares this proxy chain with another.
        Returns True if both chains have exactly the same hops in the same order
        with the exact same observations.
        """
        if len(self.hops) != len(other.hops):
            return False

        for self_hop, other_hop in zip(self.hops, other.hops):
            if self_hop != other_hop:
                return False
        return True
