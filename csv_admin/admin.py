from django.contrib import admin

from models import CsvFile


class CsvFileAdmin(admin.ModelAdmin):
    list_display = ("csv", "added_on")

admin.site.register(CsvFile, CsvFileAdmin)
