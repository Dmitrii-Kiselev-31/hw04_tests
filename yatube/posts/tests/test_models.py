from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Auth1')
        cls.user2 = User.objects.create(username='Auth2')
        cls.group = Group.objects.create(
            title='Тестовая група',
            slug='test-slug',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='рандомный текст для проверки',
        )

    def test_object_name(self):
        post = self.post
        group = self.group
        str_objects_names = {
            post.text[:15]: str(post),
            group.title: str(group),
        }
        for value, expected in str_objects_names.items():
            self.assertEqual(value, expected)
