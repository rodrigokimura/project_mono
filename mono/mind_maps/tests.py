import pytest

from .models import MindMap, Node


@pytest.fixture
def sample_mind_map(user):
    mind_map = MindMap.objects.create(name="Test Mind Map", created_by=user)
    root = Node.objects.create(
        name="Root",
        mind_map=mind_map,
        created_by=user,
    )
    child1 = Node.objects.create(
        name="Child 1",
        mind_map=mind_map,
        created_by=user,
        parent=root,
    )
    Node.objects.create(
        name="Child 2",
        mind_map=mind_map,
        created_by=user,
        parent=child1,
    )
    return mind_map


@pytest.mark.django_db
def test_copy_mind_map(sample_mind_map: MindMap):
    sample_mind_map.copy()
    assert MindMap.objects.filter(name__startswith="Test Mind Map").count() == 2
    assert Node.objects.all().count() == 6


@pytest.mark.django_db
def test_instance_methods(sample_mind_map: MindMap):
    assert str(sample_mind_map) == "Test Mind Map"
    assert str(sample_mind_map.nodes[0]) == "Root"
    assert sample_mind_map.nodes[0].position == [120, 120]
