"""Utility classes to handle portmanteaus"""
import re
from typing import Iterator, List, NamedTuple


class CompoundWord(str):
    """String with spaces"""


class Morpheme(str):
    """Substring of a word"""


class Word:
    """Represent word (no spaces)"""

    def __init__(self, text) -> None:
        self.text = text

    @property
    def morphemes(self) -> List[Morpheme]:
        """
        Split word in morphemes
        """
        ex = r"([^aeiou]*[aeiou]*)|[aeiou]*[^aeiou]*[aeiou]*"
        root = self.text
        morphemes = []
        while root != "":
            end = re.match(ex, root).end()
            morphemes.append(root[0:end].lower())
            root = root[end:]
        return morphemes

    def __str__(self) -> str:
        return self.text


class PortmanteauConfig(NamedTuple):
    """Named tuple hold portmanteau configuration"""

    parent: Word
    index: int
    onwards: bool

    def __str__(self) -> str:
        """Build part of the portmanteau"""
        if self.onwards:
            return "".join(self.parent.morphemes[: self.index])
        return "".join(self.parent.morphemes[self.index :])


class Portmanteau:
    """
    Represent a portmanteau
    """

    def __init__(
        self,
        first: PortmanteauConfig,
        second: PortmanteauConfig,
        inverted: bool = False,
    ) -> None:
        self.first_config = first
        self.second_config = second
        self.inverted = inverted

    def __str__(self) -> str:
        return str(self.first_config) + str(self.second_config)

    def __lt__(self, other):
        return str(self) < str(other)

    @property
    def first_parent(self) -> str:
        return str(self.first_config.parent).lower()

    @property
    def second_parent(self) -> str:
        return str(self.second_config.parent).lower()

    @property
    def first_partial(self) -> str:
        return str(self.first_config).lower()

    @property
    def second_partial(self) -> str:
        return str(self.second_config).lower()

    @property
    def first_remainder(self) -> str:
        return self.first_parent.replace(self.first_partial, "")

    @property
    def second_remainder(self) -> str:
        return self.second_parent.replace(self.second_partial, "")

    @property
    def first_summary(self):
        """
        Return details of the first part of portmanteau
        """
        if self.first_config.onwards:
            return (
                (self.first_partial, True),
                (self.first_remainder, False),
            )
        return (
            (self.first_remainder, False),
            (self.first_partial, True),
        )

    @property
    def second_summary(self):
        """
        Return details of the second part of portmanteau
        """
        if self.second_config.onwards:
            return (
                (self.second_partial, True),
                (self.second_remainder, False),
            )
        return (
            (self.second_remainder, False),
            (self.second_partial, True),
        )


class WordPair:
    """
    Pair of words
    """

    def __init__(self, first: Word, second: Word) -> None:
        self.first = first
        self.second = second

    def __str__(self) -> str:
        return f"{self.first} + {self.second}"

    def get_portmanteaus(
        self, same_direction: bool = False
    ) -> List[Portmanteau]:
        """
        Retrieve list of possible portmanteaus
        """
        morphemes_a = self.first.morphemes
        morphemes_b = self.second.morphemes

        portmanteaus = []
        for i in range(1, len(morphemes_a)):
            for j in range(1, len(morphemes_b)):
                if same_direction:
                    portmanteau = Portmanteau(
                        PortmanteauConfig(self.first, i, True),
                        PortmanteauConfig(self.second, j, True),
                        inverted=False,
                    )
                    portmanteaus.append(portmanteau)
                    portmanteau = Portmanteau(
                        PortmanteauConfig(self.second, j, True),
                        PortmanteauConfig(self.first, i, True),
                        inverted=True,
                    )
                    portmanteaus.append(portmanteau)
                portmanteau = Portmanteau(
                    PortmanteauConfig(self.first, i, True),
                    PortmanteauConfig(self.second, j, False),
                    inverted=False,
                )
                portmanteaus.append(portmanteau)
                portmanteau = Portmanteau(
                    PortmanteauConfig(self.second, j, True),
                    PortmanteauConfig(self.first, i, False),
                    inverted=True,
                )
                portmanteaus.append(portmanteau)
        return portmanteaus


class CompoundWordPair:
    """
    Pair of compound words (words with spaces)
    """

    def __init__(self, first: CompoundWord, second: CompoundWord) -> None:
        self.first = first
        self.second = second

    @property
    def word_pairs(self) -> Iterator[WordPair]:
        """
        Generate possible word pair combinations
        """
        for w_1 in self.first.split():
            for w_2 in self.second.split():
                yield WordPair(Word(w_1), Word(w_2))

    def get_portmanteaus(
        self, same_direction: bool = False
    ) -> List[Portmanteau]:
        """
        Retrieve list of all possible portmanteaus
        """
        portmanteaus = []
        for pair in self.word_pairs:
            portmanteaus.extend(pair.get_portmanteaus(same_direction))
        return sorted(portmanteaus)
