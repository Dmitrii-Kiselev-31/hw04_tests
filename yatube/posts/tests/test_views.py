from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..forms import PostForm


from ..models import Group, Post


User = get_user_model()


class PostsPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Auth1')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            id='1',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание группы',
        )

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_namespaces_urls_matching(self):

        templtates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': PostsPagesTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostsPagesTests.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsPagesTests.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': PostsPagesTests.post.id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for reverse_name, template in templtates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):

        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.context['page_obj'][0].text,
                         PostsPagesTests.post.text)

    def test_group_list_correct_context(self):

        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': PostsPagesTests.group.slug}
        ))
        self.assertEqual(response.context['group'].title,
                         PostsPagesTests.group.title)

    def test_profile_correct_context(self):

        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': PostsPagesTests.user.username}
        ))
        self.assertEqual(response.context['page_obj'][0].author,
                         PostsPagesTests.user)

    def test_post_detail_correct_context(self):

        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': PostsPagesTests.post.id}
        ))
        self.assertEqual(response.context['post'].id,
                         int(PostsPagesTests.post.id))

    def test_post_edit_correct_context(self):

        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': PostsPagesTests.post.id}
        ))
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertEqual(response.context['post'].id,
                         int(PostsPagesTests.post.id))

    def test_create_correct_context(self):

        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': PostsPagesTests.post.id}
        ))
        assert isinstance(response.context['form'], PostForm)


class PaginatorViewsTest(TestCase):
    '''Тестирование работы паджинатора.'''

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='Auth1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание группы',
        )
        cls.posts = []
        for i in range(13):
            cls.posts.append(Post(
                text=f'Тестовый пост №{i}',
                author=cls.author,
                group=cls.group
            )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='username')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_posts(self):
        urls = {
            reverse('posts:index'): 'index',
            reverse('posts:group_list',
                    kwargs={'slug': PaginatorViewsTest.group.slug}): 'group',
            reverse('posts:profile',
                    kwargs={
                        'username': PaginatorViewsTest.author.username
                    }): 'profile',
        }
        for url in urls.keys():
            response = self.client.get(url)
            self.assertEqual(len(response.context.get('page_obj').object_list),
                             10)

    def test_second_page_contains_three_posts(self):
        urls = {
            reverse('posts:index') + '?page=2': 'index',
            reverse('posts:group_list', kwargs={
                'slug': PaginatorViewsTest.group.slug
            }) + '?page=2':
            'group',
            reverse('posts:profile',
                    kwargs={
                        'username': PaginatorViewsTest.author.username
                    }) + '?page=2':
            'profile',
        }
        for url in urls.keys():
            response = self.client.get(url)
            self.assertEqual(
                len(response.context.get('page_obj').object_list), 3
            )
