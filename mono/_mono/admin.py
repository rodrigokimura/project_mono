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
            "Transaction": 1,
            "RecurrentTransaction": 2,
            "Installment": 3,
            "Account": 4,
            "Category": 5,
            "Group": 6,
            "Invite": 7,
            "Notification": 8,
            "Icon": 9,
            "Budget": 10,
            "BudgetConfiguration": 11,
            "Goal": 12,
            "Configuration": 13,
            "Plan": 14,
            "Feature": 15,
            "Subscription": 16,
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
