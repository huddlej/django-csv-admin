import csv
import datetime

from django.conf import settings
from django.conf.urls.defaults import patterns
from django.contrib import admin
from django.core.urlresolvers import get_callable
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import CsvFile


class CsvFileAdmin(admin.ModelAdmin):
    """
    Provides a custom view for validating CsvFile contents as form data and
    importing the validated data with a user-defined form or formset.
    """
    list_display = ("csv", "added_on", "imported_on")

    class Meta:
        css = {"all": "csv/style.css"}

    def get_urls(self):
        """
        Returns standard Django admin urls plus the custom validation view url.
        """
        urls = super(CsvFileAdmin, self).get_urls()
        csv_urls = patterns("",
            (r'^(?P<object_id>\d+)/validate/$', self.admin_site.admin_view(self.validate_view))
        )
        return csv_urls + urls

    def validate_view(self, request, object_id, extra_context=None):
        """
        Validates the contents of a CsvFile instance's file based on the
        associated content type and a user-defined form. The user can correct
        invalid data before importing it all into a database.
        """
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

            valid_rows = []
            initial_data = []
            rows = 0
            invalid_rows = 0
            for row in reader:
                rows += 1
                form_instance = form_class(row)
                if form_instance.is_valid():
                    # Ignore valid forms for now.
                    valid_rows.append(form_instance)
                else:
                    initial_data.append(row)
                    invalid_rows += 1

            # One or more rows contain invalid data.
            save_rows = False
            if invalid_rows > 0:
                # Create a form class with one form for each invalid row.
                formset_class = formset_factory(form_class, extra=0)

                if request.method == "POST":
                    formset = formset_class(request.POST, request.FILES)
                else:
                    formset = formset_class(initial=initial_data)

                if formset.is_valid():
                    valid_rows.extend(list(formset.forms))

                    # If all the invalid rows save properly, it's safe to
                    # save the remaining valid rows.
                    save_rows = True

            if save_rows:
                # All rows are valid. Save all forms.
                saved_instances = []
                try:
                    for form in valid_rows:
                        form.save()
                        saved_instances.append(form.instance)

                    # Save the time when this instance was successfully
                    # imported.
                    instance.imported_on = datetime.datetime.now()
                    instance.save()

                    # Tell the user everything was successful and redirect them
                    # to the admin page for this instance.
                    self.message_user(
                        request,
                        "Successfully imported %i records." % len(valid_rows)
                    )
                    return HttpResponseRedirect(instance.get_absolute_url())
                except Exception, e:
                    # If something goes wrong during a save, delete
                    # everything that has been saved up to this point to
                    # maintain consistency in the database. In other words,
                    # either all records get saved or none of them do.
                    #
                    # TODO: this should really be handled with a database
                    # transaction instead of the application.
                    for instance in saved_instances:
                        instance.delete()

                    # Let the user know what went wrong with an error
                    # message.
                    self.message_user(
                        request,
                        """One or more of your records couldn't be saved.
                        All changes have been reverted.
                        Error message was: %s""" % e
                    )

            context["formset"] = formset
            context["rows"] = rows
            context["invalid_rows"] = invalid_rows
        else:
            self.message_user(
                request,
                """Set a form for the content type "%s" in the Django
                CSV_ADMIN_CONTENT_FORMS setting.""" % instance.content_type
            )

        # TODO: allow the user to specify their own template.
        return render_to_response("admin/csv_admin/validate_form.html",
                                  context,
                                  context_instance=RequestContext(request))

admin.site.register(CsvFile, CsvFileAdmin)
