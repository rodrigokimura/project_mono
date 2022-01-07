import re
import uuid
from typing import List, Tuple

from django.db import models


def get_morphemes(word: str) -> List[str]:
    ex = r'([^aeiou]*[aeiou]*)|[aeiou]*[^aeiou]*[aeiou]*'
    root = word
    morphemes = []
    while root != '':
        end = re.match(ex, root).end()
        morphemes.append(root[0:end].lower())
        root = root[end:]
    return morphemes


def get_portmanteaus(a: str, b: str) -> List[Tuple[str, str, str]]:
    morphemes_a = get_morphemes(a)
    morphemes_b = get_morphemes(b)
    portmanteaus = []
    l_a = int(len(a) / 2)
    l_b = int(len(b) / 2)
    for i in range(1, l_a):
        for j in range(1, l_b):
            ab = (''.join(morphemes_a[:i]) + ''.join(morphemes_b[j:])).capitalize()
            portmanteaus.append(
                (a, b, ab)
            )
            ba = (''.join(morphemes_b[:j]) + ''.join(morphemes_a[i:])).capitalize()
            portmanteaus.append(
                (b, a, ba)
            )
    return portmanteaus


class Ship(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_1 = models.CharField(max_length=100)
    name_2 = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name_1} + {self.name_2}'

    @property
    def portmanteaus(self):
        names_1 = self.name_1.split()
        names_2 = self.name_2.split()
        portmanteaus = []
        for n_1 in names_1:
            for n_2 in names_2:
                portmanteaus.extend(get_portmanteaus(n_1, n_2))
        return portmanteaus
