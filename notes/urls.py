from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search_notes, name="search_notes"),
    path("download/pdf/", views.download_pdf, name="download_pdf"),
    path("download/word/", views.download_word, name="download_word"),
    path("download/ppt/", views.download_ppt, name="download_ppt"),
]
