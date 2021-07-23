from typing import Any, Dict
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Note
from .forms import NoteForm
from .mixins import PassRequestToFormViewMixin
import os
from django.template import loader
from django.conf import settings


class NoteCreateView(SuccessMessageMixin, PassRequestToFormViewMixin, CreateView):
    form_class = NoteForm
    template_name = 'notes/note_form.html'
    success_url = reverse_lazy('notes:note_list')
    success_message = "%(title)s note created successfully"


class NoteListView(ListView):
    model = Note

    def get_queryset(self):
        qs = Note.objects.filter(
            created_by=self.request.user
        ).order_by('location')
        return qs

    def _generate_tree(self, user):
        user_folder = f'{settings.MEDIA_ROOT}/user_{user.id}/'

        def index_maker():
            def _index(root):
                files = os.listdir(root)
                for mfile in files:
                    t = os.path.join(root, mfile)
                    if os.path.isdir(t):
                        yield loader.render_to_string('notes/p_folder.html',
                                                      {'file': mfile,
                                                       'subfiles': _index(os.path.join(root, t))})
                        continue
                    yield loader.render_to_string('notes/p_file.html',
                                                  {'file': mfile})
            return _index(user_folder)

        return index_maker()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        # def _obj_to_tuple(obj):
        #     return obj.
        context = super().get_context_data(**kwargs)
        tree = []

        tree = [
            {'t': 1, 'n': 'teste', 'c': 1},
            {'t': 0, 'n': 'asasd', 'c': [
                {'t': 0, 'n': 'aa', 'c': [
                    {'t': 1, 'n': 'sdassdasd', 'c': 2},
                ]}
            ]},
            {'t': 0, 'n': 'teste', 'c': [
                {'t': 1, 'n': 'Test2', 'c': 3},
                {'t': 0, 'n': 'teste', 'c': [
                    {'t': 1, 'n': 'Teste2', 'c': 4},
                    {'t': 1, 'n': 'Teste', 'c': 5},
                ]},
            ]},
        ]

        # qs = self.get_queryset()
        # self._path_to_nested(qs)

        print(tree)
        context['subfiles'] = self._generate_tree(self.request.user)
        return context
