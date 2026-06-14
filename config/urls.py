from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("portfolio_app.urls")),
    path("api/", include("chatbot.urls")),
]
