"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('demand', views.get_demand),
    path('api/demand/total/update-count', views.demand_by_count),
    path('api/demand/total/update-average', views.demand_by_average),
    path('api/demand/prof/update-count', views.demand_by_count_prof),
    path('api/demand/prof/update-average', views.demand_by_average_prof),
    path('api/demand/update-graphs', views.update_demand_graphs),
    path('geography', views.get_geography),
    path('api/geo/total/update-average', views.update_geo_total_avg),
    path('api/geo/prof/update-average', views.update_geo_prof_avg),
    path('api/geo/total/update-count', views.update_geo_total_count),
    path('api/geo/prof/update-count', views.update_geo_prof_count),
    path('api/geo/update-graphs', views.update_geo_graphs),
    path('skills', views.get_skills),
    path('api/skills/total/update-count', views.update_total_key_skills),
    path('api/skills/prof/update-count', views.update_prof_key_skills),
    path('api/skills/update-graphs', views.update_skills_graphs),
    path('last-vacancies/', views.last_vacancies),
    path('', views.index)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
