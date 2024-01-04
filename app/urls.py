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
    path('hello/', views.hello),
    path('demand/update-count/total', views.demand_by_count),
    path('demand/update-average/total', views.demand_by_average),
    path('demand/update-count/prof', views.demand_by_count_prof),
    path('demand/update-average/prof', views.demand_by_average_prof),
    path('geo/update-average/total', views.update_geo_total_avg),
    path('geo/update-average/prof', views.update_geo_prof_avg),
    path('geo/update-count/total', views.update_geo_total_count),
    path('geo/update-count/prof', views.update_geo_prof_count)
]
