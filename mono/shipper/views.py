from django.views.generic import TemplateView

from .models import Ship

# from django.views.generic.edit import CreateView


class Slice(object):
    def __init__(self, root, leng):
        self.root = root  # The original word
        self.leng = leng  # How many morphemes should be used as the prefix for the new portmanteau
        self.morphemes = []
        self.output = ''
        self.slice()

    def slice(self):
        import re
        ex = r'([^aeiou]*[aeiou]*)|[aeiou]*[^aeiou]*[aeiou]*'
        root = self.root

        # Full list of morphemes for future use
        while root != '':
            end = re.match(ex, root).end()
            self.morphemes.append(root[0:end])
            root = root[end:]

        # Check that the number given isnt more than is available
        if len(self.morphemes) < self.leng:
            self.leng = len(self.morphemes)

        # Stitch together the output word
        g = 0
        while g < self.leng:
            self.output += self.morphemes[g]
            g += 1


class ShipView(TemplateView):
    template_name = 'shipper/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Shipper'
        context['description'] = 'A simple shipper for portmanteau words'
        context['keywords'] = 'portmanteau, shipper, mono, django'
        ship: Ship = Ship.objects.first()
        result = ship.generate_ship()
        return context

# class ShipView(CreateView):
#     model = Project
#     form_class = ProjectForm
#     success_url = reverse_lazy('project_manager:projects')
