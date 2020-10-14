from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from compare_app.views import FileView
from compare_app.UploadFile import Upload
from compare_app import views
import logging
urlpatterns = [
  url(r'^admin/', admin.site.urls),
  url(r'^file/', include('compare_app.urls')),
  url(r'CompareTwoPDF', FileView.as_view()),
  url(r'UploadPDF', Upload.as_view()),
  url(r'', views.homepage)
]
log = logging.getLogger(__name__)

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# python -m venv venv
# venv\Scripts\activate
#
# --- pycharm start from here---
# pip install django
# django-admin startproject hello
# cd hello
# python manage.py startapp home
# python manage.py runserver