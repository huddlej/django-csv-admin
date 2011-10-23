from django.contrib.contenttypes.models import ContentType
from django.db import models


class CsvFile(models.Model):
    csv = models.FileField(upload_to="csv_admin")
    content_type = models.ForeignKey(ContentType)
    added_on = models.DateTimeField(auto_now_add=True)
