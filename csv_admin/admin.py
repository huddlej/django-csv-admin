import csv

from django.conf import settings
from django.conf.urls.defaults import patterns
from django.contrib import admin
from django.core.urlresolvers import get_callable
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import CsvFile


class CsvFileAdmin(admin.ModelAdmin):
    list_display = ("csv", "added_on")

    class Meta:
        css = {"all": "csv/style.css"}

    def get_urls(self):
        urls = super(CsvFileAdmin, self).get_urls()
        csv_urls = patterns("",
            (r'^(?P<object_id>\d+)/validate/$', self.admin_site.admin_view(self.validate_view))
        )
        return csv_urls + urls

    def validate_view(self, request, object_id, extra_context=None):
        context = {}
        if extra_context is not None:
            context.update(extra_context)

        instance = self.get_object(request, object_id)
        content_type_key = instance.content_type.natural_key()
        context["instance"] = instance
        context["app_label"] = instance._meta.app_label
        context["opts"] = instance._meta

        if (hasattr(settings, "CSV_ADMIN_CONTENT_FORMS") and
            content_type_key in settings.CSV_ADMIN_CONTENT_FORMS):
            # Look up the form path for this file's content type.
            form_path = settings.CSV_ADMIN_CONTENT_FORMS.get(content_type_key)
            form_class = get_callable(form_path)
            reader = csv.DictReader(instance.csv)

            forms = []
            rows = 0
            invalid_rows = 0
            for row in reader:
                rows += 1
                form_instance = form_class(row)
                if form_instance.is_valid():
                    # Ignore valid forms for now.
                    pass
                else:
                    forms.append(form_instance)
                    invalid_rows += 1

            context["csv_forms"] = forms
            context["rows"] = rows
            context["invalid_rows"] = invalid_rows
        else:
            self.message_user(
                request,
                """Set a form for the content type "%s" in the Django
                CSV_ADMIN_CONTENT_FORMS setting.""" % instance.content_type
            )

        return render_to_response("admin/csv_admin/validate_form.html",
                                  context,
                                  context_instance=RequestContext(request))

admin.site.register(CsvFile, CsvFileAdmin)
