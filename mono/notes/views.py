from typing import Any, Dict
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Note
from .forms import NoteForm
from .mixins import PassRequestToFormViewMixin
from collections import defaultdict
from django.template import loader
from django.http import JsonResponse
from markdownx.utils import markdownify


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


class NoteCreateView(SuccessMessageMixin, PassRequestToFormViewMixin, CreateView):
    form_class = NoteForm
    template_name = 'notes/note_form.html'
    success_url = reverse_lazy('notes:note_list')
    success_message = "%(title)s note created successfully"


class NoteDetailApiView(View):
    def get(self, request, *args, **kwargs):
        id = kwargs['id']
        note = Note.objects.get(id=id)
        return JsonResponse(
          {
            'id': id,
            'text': note.text,
            'html': markdownify(note.text),
          }
        )


class NoteListView(ListView):
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
