import uuid

from django.db import models


class Ship(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name_a = models.CharField(max_length=100)
    last_name_a = models.CharField(max_length=100)
    first_name_b = models.CharField(max_length=100)
    last_name_b = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.first_name_a} {self.last_name_a} + {self.first_name_b} {self.last_name_b}'

    def generate_ship(self):
        import re
        ex = r'([^aeiou]*[aeiou]*)|[aeiou]*[^aeiou]*[aeiou]*'
        root = self.first_name_a + self.last_name_a
        output = ''
        while root != '':
            end = re.match(ex, root).end()
            output += root[0:end]
            root = root[end:]
        return output
