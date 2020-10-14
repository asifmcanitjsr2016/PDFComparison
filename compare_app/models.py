from django.db import models


class File(models.Model):
    pdf_old = models.TextField(blank=False, null=False)
    pdf_new = models.TextField(blank=False, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)
