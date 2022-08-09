from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post
from http import HTTPStatus

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='username')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание группы'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post(self):
        """Проверка процесса и результата создания поста."""
        count_posts = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post_1 = get_object_or_404(Post, id=self.group.id)
        self.assertEqual(PostCreateFormTests.user.username, 'username')
        self.assertEqual(PostCreateFormTests.group.title, 'Тестовая группа')
        self.assertTrue(Post.objects.filter(group=self.group.id))
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertEqual(post_1.text, 'Тестовый текст')
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'username'})
        )

    def test_authorized_edit_post(self):
        """Авторизованный пользователь может редактировать свой пост."""
        post_2 = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
        )
        form_data = {
            'text': 'Измененный тестовый текст',
            'group': self.group.id
        }
        response_edit = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': post_2.id
                    }),
            data=form_data,
            follow=True,
        )
        post_2 = get_object_or_404(Post, id=self.group.id)
        self.assertEqual(response_edit.status_code, HTTPStatus.OK)
        self.assertEqual(post_2.text, 'Измененный тестовый текст')
