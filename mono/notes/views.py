"""Notes' views"""
from collections import defaultdict
from typing import Any, Dict

from __mono.mixins import PassRequestToFormViewMixin
from __mono.views import ProtectedDeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.template import loader
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from markdownx.utils import markdownify

from .forms import NoteForm
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
    """
    Render tree of files and folders
    """

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
                for file in files[mfile]:
                    file_id = file.split(':')[0]
                    title = file[len(file_id) + 1:]
                    yield loader.render_to_string(
                        'notes/p_file.html',
                        {
                            'id': file_id,
                            'title': title,
                        }
                    )
        return _index(tree)

    return index_maker()


class NoteCreateView(LoginRequiredMixin, SuccessMessageMixin, PassRequestToFormViewMixin, CreateView):
    """
    Create note
    """
    form_class = NoteForm
    template_name = 'notes/note_form.html'
    success_url = reverse_lazy('notes:notes')
    success_message = "%(title)s note created successfully"


class NoteFormView(LoginRequiredMixin, SuccessMessageMixin, PassRequestToFormViewMixin, UpdateView):
    """
    Edit note
    """
    model = Note
    form_class = NoteForm
    template_name = 'notes/note_form.html'
    success_url = reverse_lazy('notes:notes')
    success_message = "%(title)s note created successfully"


class NoteDetailApiView(LoginRequiredMixin, View):
    """
    Detailed info about a note
    """
    def get(self, request, *args, **kwargs):
        """
        Detailed info about a note
        """
        note_id = kwargs['pk']
        note = Note.objects.get(id=note_id)
        request.session['note'] = note_id
        return JsonResponse(
            {
                'id': note_id,
                'title': note.title,
                'text': note.text,
                'html': markdownify(note.text),
                'url': note.get_absolute_url(),
                'delete_url': note.get_delete_url(),
            }
        )


class NoteListView(LoginRequiredMixin, ListView):
    """
    List all user's notes
    """
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


class NoteDeleteView(ProtectedDeleteView):
    """
    Delete note
    """
    model = Note
    success_url = reverse_lazy('notes:notes')
    success_message = _("Note was deleted successfully")
