"""Model of knitted structure as a set of crossing wales using artin braid groups.

This module provides the Wale_Braid class which represents complex cable knitting patterns as mathematical braid structures,
using concepts from algebraic topology to model how wales cross over and under each other.
"""
from knit_graphs.artin_wale_braids.Wale_Braid_Word import Wale_Braid_Word
from knit_graphs.artin_wale_braids.Wale_Group import Wale_Group


class Wale_Braid:
    """A model of knitted structure as a set of crossing wales using Artin braid groups.

    This class represents complex cable knitting patterns using mathematical braid theory,
    where wales are treated as strands in a braid and their crossings are represented as braid operations.
    This provides a formal mathematical framework for analyzing and manipulating cable patterns.

    Attributes:
        wale_groups (list[Wale_Group]): The collection of wale groups that participate in the braid structure.
        wale_words (list[Wale_Braid_Word]): The sequence of braid words that describe the crossing operations between wales.
    """

    def __init__(self, wale_groups: list[Wale_Group], wale_words: list[Wale_Braid_Word]) -> None:
        """Initialize a wale braid with the specified groups and braid words.

        Args:
            wale_groups (list[Wale_Group]): The wale groups that participate in this braid structure.
            wale_words (list[Wale_Braid_Word]): The sequence of braid words describing the crossing operations.
        """
        self.wale_groups: list[Wale_Group] = wale_groups
        self.wale_words: list[Wale_Braid_Word] = wale_words

    def reduce(self) -> None:
        """Simplify the braid by removing pairs of braid words that invert each other.

        This method modifies the wale_words list by identifying and removing adjacent pairs of braid words that are inverses of each other,
         effectively canceling out their operations to create a simplified but equivalent braid representation.
        """
        reduced_words: list[Wale_Braid_Word] = []
        remaining_words: list[Wale_Braid_Word] = [*self.wale_words[1:]]
        while len(remaining_words) > 0:
            if len(reduced_words) == 0:
                reduced_words.append(remaining_words.pop(0))
            else:
                next_word = remaining_words.pop(0)
                current_word = reduced_words[-1]
                if next_word.is_inversion(current_word):
                    reduced_words.pop()  # remove current word because its inverted
                else:
                    reduced_words.append(next_word)
        self.wale_words = reduced_words
