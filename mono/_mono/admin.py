from django.contrib import admin

class MyAdminSite(admin.AdminSite):
    site_title = "MONO"
    site_header = "Project Mono"
    index_title = "Mono models administration"
    site_url = "/fn/"

    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        ordering = {
            "Transaction":          1, 
            "Account":              2, 
            "Category":             3, 
            "Group":                4, 
            "Invite":               5, 
            "Notification":         6, 
            "Icon":                 7, 
            "Budget":               8, 
            "BudgetConfiguration":  9, 
            "Goal":                 10, 
            "Configuration":        11, 
            "Plan":                 12, 
            "Feature":              13, 
            "Subscription":         14, 
        }
        app_dict = self._build_app_dict(request)
        # a.sort(key=lambda x: b.index(x[0]))
        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            if app['app_label'] == 'finance':
                app['models'].sort(key=lambda x: ordering[x['object_name']])

        return app_list