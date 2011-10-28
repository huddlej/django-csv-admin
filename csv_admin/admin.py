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
        context["instance"] = instance
        context["app_label"] = instance._meta.app_label
        context["opts"] = instance._meta

        if hasattr(settings, "CSV_ADMIN_CONTENT_FORMS"):
            content_type = instance.content_type
            form_path = settings.CSV_ADMIN_CONTENT_FORMS.get(content_type.natural_key())
            if form_path:
                form_class = get_callable(form_path)
                reader = csv.DictReader(instance.csv)

                forms = []
                max_rows = 100
                count = 0
                all_forms_valid = True
                for row in reader:
                    if count == max_rows:
                        break

                    form_instance = form_class(row)
                    if "validate" in request.POST and form_instance.is_valid():
                        pass
                    else:
                        all_forms_valid = False

                    forms.append(form_instance)
                    count += 1

                context["csv_forms"] = forms

        return render_to_response("admin/csv_admin/validate_form.html",
                                  context,
                                  context_instance=RequestContext(request))

admin.site.register(CsvFile, CsvFileAdmin)
