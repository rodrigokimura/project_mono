"""Notes' views"""
from collections import defaultdict
from typing import Any, Dict

from __mono.mixins import PassRequestToFormViewMixin
from __mono.permissions import IsCreator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template import loader
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from markdownx.utils import markdownify
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import NoteForm
from .models import Note
from .serializers import NoteSerializer

FILE_MARKER = "<files>"


def attach(branch, trunk):
    """
    Insert a branch of directories on its trunk.
    """
    parts = branch.split("/", 1)
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

    def _index(files, level):
        for mfile in files:
            if mfile != FILE_MARKER:
                yield loader.render_to_string(
                    "notes/p_folder.html",
                    {
                        "file": mfile,
                        "subfiles": _index(files[mfile], level),
                        "level": level - 1,
                    },
                )
                continue
            for file in files[mfile]:
                file_id = file.split(":")[0]
                title = file[len(file_id) + 1 :]
                yield loader.render_to_string(
                    "notes/p_file.html",
                    {
                        "id": file_id,
                        "title": title,
                        "level": level,
                    },
                )
            level = level + 1

    return _index(tree, 0)


class NoteCreateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    PassRequestToFormViewMixin,
    CreateView,
):
    """
    Create note
    """

    form_class = NoteForm
    template_name = "notes/note_form.html"
    success_url = reverse_lazy("notes:index")
    success_message = _("%(title)s note created successfully")


class NoteFormView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    PassRequestToFormViewMixin,
    UpdateView,
):
    """
    Edit note
    """

    model = Note
    form_class = NoteForm
    template_name = "notes/note_form.html"
    success_url = reverse_lazy("notes:index")
    success_message = _("%(title)s note updated successfully")


class NoteDetailApiView(LoginRequiredMixin, APIView):
    """
    Partially edit a note
    """

    permission_classes = [IsCreator]

    def get(self, request, pk):
        """
        Detailed info about a note
        """
        note = get_object_or_404(Note, pk=pk)
        request.session["note"] = pk
        return JsonResponse(
            {
                "id": pk,
                "title": note.title,
                "text": note.text,
                "html": markdownify(note.text),
                "url": note.get_absolute_url(),
            }
        )

    def patch(self, request, pk):
        """Edit note"""
        note = get_object_or_404(Note, pk=pk)
        serializer = NoteSerializer(note, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(
            {
                "success": True,
                "data": serializer.data,
            }
        )

    def delete(self, request, pk):
        """Delete note"""
        note = get_object_or_404(Note, pk=pk)
        note.delete()
        if request.session.get("note") == pk:
            del request.session["note"]
        return Response(status=status.HTTP_204_NO_CONTENT)


class NoteListView(LoginRequiredMixin, ListView):
    """
    List all user's notes
    """

    model = Note

    def get_queryset(self):
        qs = Note.objects.filter(created_by=self.request.user).order_by(
            "location"
        )
        return qs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        main_dict = defaultdict(dict, ((FILE_MARKER, []),))
        for obj in self.get_queryset():
            attach(obj.full_path, main_dict)
        context["subfiles"] = generate_tree(main_dict)
        return context
