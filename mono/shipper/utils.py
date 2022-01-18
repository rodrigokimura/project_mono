import re
from typing import Iterator, List, NamedTuple


class CompoundWord(str):
    """String with spaces"""


class Morpheme(str):
    """Substring of a word"""


class Word:

    def __init__(self, text) -> None:
        self.text = text

    @property
    def morphemes(self) -> List[Morpheme]:
        ex = r'([^aeiou]*[aeiou]*)|[aeiou]*[^aeiou]*[aeiou]*'
        root = self.text
        morphemes = []
        while root != '':
            end = re.match(ex, root).end()
            morphemes.append(root[0:end].lower())
            root = root[end:]
        return morphemes

    def __str__(self) -> str:
        return self.text


class PortmanteauConfig(NamedTuple):
    parent: Word
    index: int
    onwards: bool

    def __str__(self) -> str:
        if self.onwards:
            return ''.join(self.parent.morphemes[:self.index])
        else:
            return ''.join(self.parent.morphemes[self.index:])


class Portmanteau:

    def __init__(self, first_config: PortmanteauConfig, second_config: PortmanteauConfig, inverted: bool = False) -> None:
        self.first_config = first_config
        self.second_config = second_config
        self.inverted = inverted

    def __str__(self) -> str:
        return str(self.first_config) + str(self.second_config)

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
        return self.first_parent.replace(self.first_partial, '')

    @property
    def second_remainder(self) -> str:
        return self.second_parent.replace(self.second_partial, '')

    @property
    def first_summary(self):
        if self.first_config.onwards:
            return (
                (self.first_partial, True),
                (self.first_remainder, False),
            )
        else:
            return (
                (self.first_remainder, False),
                (self.first_partial, True),
            )

    @property
    def second_summary(self):
        if self.second_config.onwards:
            return (
                (self.second_partial, True),
                (self.second_remainder, False),
            )
        else:
            return (
                (self.second_remainder, False),
                (self.second_partial, True),
            )


class WordPair:

    def __init__(self, first: Word, second: Word) -> None:
        self.first = first
        self.second = second

    def __str__(self) -> str:
        return f"{self.first} + {self.second}"

    def get_portmanteaus(self, same_direction: bool = False) -> List[Portmanteau]:
        morphemes_a = self.first.morphemes
        morphemes_b = self.second.morphemes

        portmanteaus = []
        for i in range(1, len(morphemes_a)):
            for j in range(1, len(morphemes_b)):
                if same_direction:
                    p = Portmanteau(
                        PortmanteauConfig(self.first, i, True),
                        PortmanteauConfig(self.second, j, True),
                        inverted=False,
                    )
                    portmanteaus.append(p)
                    p = Portmanteau(
                        PortmanteauConfig(self.second, j, True),
                        PortmanteauConfig(self.first, i, True),
                        inverted=True,
                    )
                    portmanteaus.append(p)
                p = Portmanteau(
                    PortmanteauConfig(self.first, i, True),
                    PortmanteauConfig(self.second, j, False),
                    inverted=False,
                )
                portmanteaus.append(p)
                p = Portmanteau(
                    PortmanteauConfig(self.second, j, True),
                    PortmanteauConfig(self.first, i, False),
                    inverted=True,
                )
                portmanteaus.append(p)
        return portmanteaus


class CompoundWordPair:

    def __init__(self, first: CompoundWord, second: CompoundWord) -> None:
        self.first = first
        self.second = second

    @property
    def word_pairs(self) -> Iterator[WordPair]:
        for w_1 in self.first.split():
            for w_2 in self.second.split():
                yield WordPair(Word(w_1), Word(w_2))

    def get_portmanteaus(self, same_direction: bool = False) -> List[Portmanteau]:
        portmanteaus = []
        for pair in self.word_pairs:
            portmanteaus.extend(pair.get_portmanteaus(same_direction))
        return sorted(portmanteaus, key=lambda p: str(p))
