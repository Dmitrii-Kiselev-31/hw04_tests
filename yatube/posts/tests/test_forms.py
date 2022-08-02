from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание группы'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='username')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post(self):
        '''Проверка процесса и результата создания поста.'''
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
        post_1 = Post.objects.get(id=self.group.id)
        author_1 = User.objects.get(username='username')
        group_1 = Group.objects.get(title='Тестовая группа')
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'username'})
        )
        self.assertEqual(post_1.text, 'Тестовый текст')
        self.assertEqual(author_1.username, 'username')
        self.assertEqual(group_1.title, 'Тестовая группа')

    def test_guest_new_post(self):
        '''Неавторизованный пользователь не может опубликовать пост.'''
        form_data = {
            'text': 'Тестовый пост от неавторизованного пользователя',
            'group': self.group.id
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Post.objects.filter(
            text='Тестовый пост от неавторизованного пользователя').exists())

    def test_authorized_edit_post(self):
        '''Авторизованный пользователь может редактировать свой пост.'''
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post_2 = Post.objects.get(id=self.group.id)
        self.client.get(f'/username/{post_2.id}/edit/')
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
        post_2 = Post.objects.get(id=self.group.id)
        self.assertEqual(response_edit.status_code, 200)
        self.assertEqual(post_2.text, 'Измененный тестовый текст')
