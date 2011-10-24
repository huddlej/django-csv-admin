from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import get_callable

from models import CsvFile


class CsvFileAdmin(admin.ModelAdmin):
    list_display = ("csv", "added_on")

    def change_view(self, request, object_id, extra_context=None):
        if extra_context is None:
            extra_context = {}

        instance = self.get_object(request, object_id)
        content_type = instance.content_type

        if hasattr(settings, "CSV_ADMIN_CONTENT_FORMS"):
            form_path = settings.CSV_ADMIN_CONTENT_FORMS.get(content_type.natural_key())
            if form_path:
                form_class = get_callable(form_path)
                form_instance = form_class(request.POST or None)
                extra_context["csv_form"] = form_instance

        return super(CsvFileAdmin, self).change_view(request, object_id, extra_context)

admin.site.register(CsvFile, CsvFileAdmin)
