from collections import defaultdict
from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.template import loader
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from markdownx.utils import markdownify

from .forms import NoteForm
from .mixins import PassRequestToFormViewMixin
from .models import Note

FILE_MARKER = '<files>'


def attach(branch, trunk):
    '''
    Insert a branch of directories on its trunk.
    '''
    parts = branch.split('/', 1)
    if len(parts) == 1:  # branch is a file
        trunk[FILE_MARKER].append(parts[0])
    else:
        node, others = parts
        if node not in trunk:
            trunk[node] = defaultdict(dict, ((FILE_MARKER, []),))
        attach(others, trunk[node])


def generate_tree(tree):

    def index_maker():
        def _index(files):
            for mfile in files:
                if mfile != FILE_MARKER:
                    yield loader.render_to_string(
                        'notes/p_folder.html',
                        {
                            'file': mfile,
                            'subfiles': _index(files[mfile])
                        }
                    )
                    continue
                else:
                    for f in files[mfile]:
                        id = f.split(':')[0]
                        title = f[len(id) + 1:]
                        yield loader.render_to_string(
                            'notes/p_file.html',
                            {
                                'id': id,
                                'title': title,
                            }
                        )
        return _index(tree)

    return index_maker()


class NoteCreateView(LoginRequiredMixin, SuccessMessageMixin, PassRequestToFormViewMixin, CreateView):
    form_class = NoteForm
    template_name = 'notes/note_form.html'
    success_url = reverse_lazy('notes:notes')
    success_message = "%(title)s note created successfully"


class NoteFormView(LoginRequiredMixin, SuccessMessageMixin, PassRequestToFormViewMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'notes/note_form.html'
    success_url = reverse_lazy('notes:notes')
    success_message = "%(title)s note created successfully"


class NoteDetailApiView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        id = kwargs['pk']
        note = Note.objects.get(id=id)
        request.session['note'] = id
        return JsonResponse(
            {
                'id': id,
                'title': note.title,
                'text': note.text,
                'html': markdownify(note.text),
                'url': note.get_absolute_url(),
                'delete_url': note.get_delete_url(),
            }
        )


class NoteListView(LoginRequiredMixin, ListView):
    model = Note

    def get_queryset(self):
        qs = Note.objects.filter(
            created_by=self.request.user
        ).order_by('location')
        return qs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        main_dict = defaultdict(dict, ((FILE_MARKER, []),))
        for obj in self.get_queryset():
            attach(obj.full_path, main_dict)

        context['subfiles'] = generate_tree(main_dict)

        return context


class NoteDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Note
    success_url = reverse_lazy('notes:notes')
    success_message = _("Note was deleted successfully")

    def test_func(self):
        return self.get_object().created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
