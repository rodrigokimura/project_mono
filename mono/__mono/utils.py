from django.core.exceptions import ValidationError


def validate_file_size(file, size):
    if file.size > size * 1024 * 1024:
        raise ValidationError("Max size of file is %s MiB" % size)
    return file
