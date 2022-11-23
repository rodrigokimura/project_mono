"""Mind maps views"""
from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DEFAULT_PANEL_SIZE, MindMap, Node
from .serializers import NodeSerializer


class IndexView(LoginRequiredMixin, TemplateView):
    """Main view for Mind Maps app"""

    template_name = "mind_maps/index.html"


class MindMapListView(LoginRequiredMixin, TemplateView):
    """List view for Mind Maps app"""

    template_name = "mind_maps/mind_map_list.html"


class MindMapDetailView(LoginRequiredMixin, DetailView):
    """Detail view for Mind Maps app"""

    template_name = "mind_maps/detail.html"
    model = MindMap

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        mind_map: MindMap = self.get_object()
        context = super().get_context_data(**kwargs)
        context["PANEL_SIZE"] = DEFAULT_PANEL_SIZE
        context["panel"] = {
            **DEFAULT_PANEL_SIZE,
            "color": mind_map.color,
            "scale": mind_map.scale,
        }
        context["node_defaults"] = {
            "font_color": Node._meta.get_field("font_color").get_default(),
            "border_color": Node._meta.get_field("border_color").get_default(),
            "background_color": Node._meta.get_field(
                "background_color"
            ).get_default(),
        }
        return context


class FullSyncView(APIView):
    """Full sync view for Mind Maps app"""

    @transaction.atomic()
    def post(self, request: Request, *args, **kwargs):
        """Full sync view"""
        serializer = NodeSerializer(
            data=request.data, many=True, context={"request": request}
        )
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        for node in request.data:
            mind_map = MindMap.objects.get(id=node.get("mind_map"))
            Node.objects.update_or_create(
                id=node["id"],
                created_by=request.user,
                defaults={
                    "name": node.get("name"),
                    "mind_map": mind_map,
                    "parent": Node.objects.get_or_create(
                        id=node.get("parent"),
                        defaults={
                            "mind_map": mind_map,
                            "created_by": request.user,
                        },
                    )[0]
                    if node.get("parent") is not None
                    else None,
                    "x": node.get("x"),
                    "y": node.get("y"),
                    "created_by": request.user,
                    "font_size": node.get("font_size"),
                    "padding": node.get("padding"),
                    "border_size": node.get("border_size"),
                    "font_color": node.get("font_color"),
                    "border_color": node.get("border_color"),
                    "background_color": node.get("background_color"),
                    "bold": node.get("bold"),
                    "italic": node.get("italic"),
                    "underline": node.get("underline"),
                    "line_through": node.get("line_through"),
                    "collapsed": node.get("collapsed"),
                },
            )
        Node.objects.filter(
            created_by=request.user,
            mind_map=request.data[0].get("mind_map"),
        ).exclude(id__in=[n["id"] for n in request.data]).delete()
        return Response(
            status=status.HTTP_200_OK,
            data=request.data,
        )
