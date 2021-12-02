import django.apps
from django.core.mail import mail_admins
from django.template.loader import get_template


class Report:

    def get_models(self):
        data = {}
        for name, app in django.apps.apps.app_configs.items():
            app_name = name
            data[app_name] = {}
            for model in app.get_models():
                model_name = model.__name__
                qs = model.objects.all()
                data[app_name][model_name] = qs
        return data

    def send(self):
        context = {'models': self.get_models()}

        text_content = get_template('email/status_report.txt').render(context)
        html_content = get_template('email/status_report.html').render(context)

        mail_admins(
            subject='STATUS REPORT',
            message=text_content,
            html_message=html_content,
            fail_silently=False,
        )
