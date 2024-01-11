from django.contrib import admin

from app import views
from app.models import Vacancy

admin.site.register(Vacancy)