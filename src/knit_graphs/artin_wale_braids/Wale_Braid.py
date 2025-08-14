"""Model of knitted structure as a set of crossing wales using artin braid groups"""
from knit_graphs.artin_wale_braids.Wale_Braid_Word import Wale_Braid_Word
from knit_graphs.artin_wale_braids.Wale_Group import Wale_Group


class Wale_Braid:
    """
        Models a knitted structure as a set of crossing wales using artin braid groups
    """
    def __init__(self, wale_groups: list[Wale_Group], wale_words: list[Wale_Braid_Word]) -> None:
        self.wale_groups: list[Wale_Group] = wale_groups
        self.wale_words: list[Wale_Braid_Word] = wale_words

    def reduce(self) -> None:
        """
           Modifies wale_words by removing any braid words that invert each other
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
