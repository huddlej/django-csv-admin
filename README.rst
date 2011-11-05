Django CSV admin
================

The simplest possible tool for uploading, validating, editing, and importing CSV
data into Django models.

Configuring forms for CSV data
---------------------------

CSV data are treated as form data. As such, they need to be validated before
they can be imported into Django models. Define forms to validate your data for
specific content types using the following setting in your Django settings.

::

    CSV_ADMIN_CONTENT_FORMS = {
        ("app_label", "model"): "myapp.forms.MyModelForm"
    }

The key for the ``CSV_ADMIN_CONTENT_FORMS`` dictionary is the natural key
returned by the content type you've associated with your CSV data file. The
value for each key is a Python path string for the form by which your data will
be validated.

Defining forms
--------------

Forms for CSV data validation must be instances of the Django ``Form`` class and
implement a ``save()`` method that stores the resulting database object in the
``instance`` attribute.