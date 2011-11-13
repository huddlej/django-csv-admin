from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
import operator


class CsvFile(models.Model):
    """
    Associated an uploaded CSV file with a Django content type.

    The relationship between the file and the content type is used to look up an
    admin form for that content type. Forms validate CSV data and import the
    validated data into Django models.
    """
    # Create a Q instance by ORing together Q instances for each content type
    # with a form defined in Django settings.
    content_type_choices = reduce(
        operator.or_,
        (Q(app_label=app_label, model=model)
         for app_label, model
         in getattr(settings, "CSV_ADMIN_CONTENT_FORMS", {}).keys())
    )
    csv = models.FileField(upload_to="csv_admin", help_text="CSV file to be imported")
    content_type = models.ForeignKey(
        ContentType,
        limit_choices_to=content_type_choices,
        help_text="Content types with CSV admin forms defined in Django's admin settings"
    )
    added_on = models.DateTimeField(auto_now_add=True)
    imported_on = models.DateTimeField(blank=True, null=True, editable=False)

    class Meta:
        ordering = ("-added_on",)

    def __unicode__(self):
        return self.csv.name

    @models.permalink
    def get_absolute_url(self):
        return ("admin:csv_admin_csvfile_change", [str(self.id)])
