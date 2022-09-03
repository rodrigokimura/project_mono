"""Mind maps views"""
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MindMap, Node
from .serializers import NodeSerializer


class IndexView(UserPassesTestMixin, TemplateView):

    template_name = "mind_maps/index.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        mind_maps = MindMap.objects.filter(created_by=self.request.user)
        context = super().get_context_data(**kwargs)
        context["mind_maps"] = mind_maps
        return context


class MindMapDetailView(UserPassesTestMixin, DetailView):

    template_name = "mind_maps/detail.html"
    model = MindMap

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PlaygroundView(UserPassesTestMixin, TemplateView):

    template_name = "mind_maps/playground.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class FullSyncView(APIView):
    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        serializer = NodeSerializer(
            data=request.data, many=True, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        for n in request.data:
            Node.objects.update_or_create(
                id=n["id"],
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
        return Response(
            status=status.HTTP_200_OK,
            data=request.data,
        )
