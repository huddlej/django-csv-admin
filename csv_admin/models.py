from django.contrib.contenttypes.models import ContentType
from django.db import models


class CsvFile(models.Model):
    """
    Associated an uploaded CSV file with a Django content type.

    The relationship between the file and the content type is used to look up an
    admin form for that content type. Forms validate CSV data and import the
    validated data into Django models.
    """
    csv = models.FileField(upload_to="csv_admin")
    content_type = models.ForeignKey(ContentType)
    added_on = models.DateTimeField(auto_now_add=True)
