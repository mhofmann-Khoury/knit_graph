"""Module containing the base class for KnitGraphErrors"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from knit_graphs.Yarn import Yarn


class KnitGraphError(Exception):
    """Base class for KnitGraphErrors"""

    def __init__(self, message: str = "") -> None:
        super().__init__(f"{self.__class__.__name__}:\n\t{message}")


class Use_Cut_Yarn_ValueError(KnitGraphError, ValueError):
    """Exception for attempting to use yarn that has been cut from its carrier.
    This exception occurs when trying to perform knitting operations with yarn that has been severed from its carrier,
    making it impossible to continue yarn operations as the yarn is no longer connected to the carrier system."""

    def __init__(self, yarn: Yarn) -> None:
        """Initialize a cut yarn usage exception.

        Args:
            yarn (Yarn): The cut yarn that was used.
        """
        self.yarn: Yarn = yarn
        super().__init__(f"Cannot create more loops on a cut yarn: {self.yarn}")
