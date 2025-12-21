from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Course, Lesson

@registry.register_document
class CourseDocument(Document):
    class Index:
        name = 'courses'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Course
        fields = [
            'title',
            'description',
            'category',
        ]

@registry.register_document
class LessonDocument(Document):
    course = fields.ObjectField(properties={
        'title': fields.TextField(),
    })

    class Index:
        name = 'lessons'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Lesson
        fields = [
            'title',
            'content',
        ]