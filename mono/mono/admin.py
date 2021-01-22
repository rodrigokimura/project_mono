from django.contrib import admin

class MyAdminSite(admin.AdminSite):
    site_title = "MONO"
    site_header = "Project Mono"
    index_title = "Mono models administration"
