"""Mind maps views"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MindMap, Node
from .serializers import NodeSerializer


class IndexView(LoginRequiredMixin, TemplateView):

    template_name = "mind_maps/index.html"

    def get_context_data(self, **kwargs):
        mind_maps = MindMap.objects.filter(created_by=self.request.user)
        context = super().get_context_data(**kwargs)
        context["mind_maps"] = mind_maps
        return context


class MindMapListView(LoginRequiredMixin, TemplateView):

    template_name = "mind_maps/mind_map_list.html"


class MindMapDetailView(LoginRequiredMixin, DetailView):

    template_name = "mind_maps/detail.html"
    model = MindMap


class FullSyncView(APIView):
    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        serializer = NodeSerializer(
            data=request.data, many=True, context={"request": request}
        )
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        for n in request.data:
            Node.objects.update_or_create(
                id=n["id"],
                created_by=request.user,
                defaults={
                    "name": n.get("name"),
                    "mind_map": MindMap.objects.get(id=n.get("mind_map")),
                    "parent": Node.objects.get_or_create(
                        id=n.get("parent"),
                        defaults={"created_by": request.user},
                    )[0]
                    if n.get("parent") is not None
                    else None,
                    "x": n.get("x"),
                    "y": n.get("y"),
                    "created_by": request.user,
                },
            )
        Node.objects.filter(
            created_by=request.user,
        ).exclude(id__in=[n["id"] for n in request.data]).delete()
        return Response(
            status=status.HTTP_200_OK,
            data=request.data,
        )
