import uuid

from django.db import models

from .utils import (
    CompoundWordPair, Portmanteau as _Portmanteau, PortmanteauConfig, Word,
)


class Ship(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_1 = models.CharField(max_length=100)
    name_2 = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name_1} + {self.name_2}'

    def generate_portmanteaus(self):
        cwp = CompoundWordPair(self.name_1, self.name_2)
        portmanteaus = [
            Portmanteau(
                ship=self,
                first_parent=p.first_parent,
                first_index=p.first_config.index,
                first_flag_onwards=p.first_config.onwards,
                second_parent=p.second_parent,
                second_index=p.second_config.index,
                second_flag_onwards=p.second_config.onwards,
                is_inverted=p.inverted,
            )
            for p in cwp.get_portmanteaus(same_direction=False)
        ]
        Portmanteau.objects.bulk_create(portmanteaus)


class Portmanteau(models.Model):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE, related_name='portmanteaus')
    first_parent = models.CharField(max_length=100)
    first_index = models.SmallIntegerField()
    first_flag_onwards = models.BooleanField()
    second_parent = models.CharField(max_length=100)
    second_index = models.SmallIntegerField()
    second_flag_onwards = models.BooleanField()
    is_inverted = models.BooleanField()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._Portmanteau = _Portmanteau(
            PortmanteauConfig(Word(self.first_parent), self.first_index, self.first_flag_onwards),
            PortmanteauConfig(Word(self.second_parent), self.second_index, self.second_flag_onwards),
        )

    def __str__(self) -> str:
        return str(self._Portmanteau)

    @property
    def first_partial(self):
        return str(self._Portmanteau.first_partial)

    @property
    def second_partial(self):
        return str(self._Portmanteau.second_partial)

    @property
    def first_summary(self):
        return self._Portmanteau.first_summary

    @property
    def second_summary(self):
        return self._Portmanteau.second_summary
