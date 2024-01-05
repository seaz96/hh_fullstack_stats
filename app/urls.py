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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('demand/total/update-count', views.demand_by_count),
    path('demand/total/update-average', views.demand_by_average),
    path('demand/prof/update-count', views.demand_by_count_prof),
    path('demand/prof/update-average', views.demand_by_average_prof),
    path('demand/update-graphs', views.update_demand_graphs),
    path('geo/total/update-average', views.update_geo_total_avg),
    path('geo/prof/update-average', views.update_geo_prof_avg),
    path('geo/total/update-count', views.update_geo_total_count),
    path('geo/prof/update-count', views.update_geo_prof_count),
    path('geo/update-graphs', views.update_geo_graphs),
    path('skills/total/update-count', views.update_total_key_skills),
    path('skills/prof/update-count', views.update_prof_key_skills),
    path('skills/update-graphs', views.update_skills_graphs),
    path('vac', views.get_vacancies)
]
