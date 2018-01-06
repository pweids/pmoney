"""pmoney URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.urls import include, path, re_path
from django.contrib import admin
from budget import views


urlpatterns = [
    path('', views.home_page, name="home"),

    path('budget/', views.budget_page, name="budget"),
    path('budget/<int:month>/',
        views.budget_page, name="budget"),
    path('budget/<int:month>/<int:year>/',
        views.budget_page, name="budget"),

    path('edit_item/<int:id>/', views.edit_item, name="edit_item"),
    path('add_item/', views.add_item, name="add_item"),
    path('add_item/<int:month>/<int:year>/', views.add_item, name="add_item"),
    path('delete_item/', views.delete_item, name="delete_item"),

    path('', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls)
]
