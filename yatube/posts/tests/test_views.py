from django.urls import reverse
from django import forms
from django.test import Client, TestCase
from ..models import Group, Post, User


class Paginator_view_test(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='NoNameAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.posts = [
            Post(
                text=f'Тестовый пост {i}',
                author=cls.author,
                group=cls.group,
            )
            for i in range(13)
        ]
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.unauthorized_client = Client()

    def test_pagination(self):
        """На первой странице 10 постов, на второй 13."""
        page_one = 10
        page_two = 3
        pages_url = [
            reverse(
                'posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={
                'username': self.author.username}),
        ]
        for reverse_ in pages_url:
            with self.subTest(reverse_=reverse_):
                self.assertEqual(len(self.unauthorized_client.get(
                    reverse_).context.get('page_obj')),
                    page_one
                )
                self.assertEqual(len(self.unauthorized_client.get(
                    reverse_ + '?page=2').context.get('page_obj')),
                    page_two
                )


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='NoNameAuthor')
        cls.auth_user = User.objects.create(username='AuthUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client.force_login(PostURLTests.auth_user)
        self.authorized_client_author.force_login(PostURLTests.author)

    def test_create_post_edit_show_correct_context(self):
        """Шаблон редактирования поста create_post сформирован
        с правильным контекстом.
        """
        url = reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        response = self.authorized_client_author.get(url)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for field, expected in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected)

    def test_create_post_show_correct_context(self):
        """Шаблон  create_post сформирован
        с правильным контекстом.
        """
        url = reverse('posts:post_create')
        response = self.authorized_client.get(url)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for field, expected in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.post.author}
            ): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={
                    'post_id': self.post.pk}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        post_text = response.context.get('page_obj')[0].text
        post_author = response.context.get('page_obj')[0].author.username
        group_post = response.context.get('page_obj')[0].group.title
        self.assertEqual(post_text, 'Тестовый пост')
        self.assertEqual(post_author, 'NoNameAuthor')
        self.assertEqual(group_post, 'Тестовая группа')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        url = reverse('posts:group_list', kwargs={
            'slug': self.group.slug}
        )
        response = self.authorized_client.get(url)
        group_title = response.context.get('group').title
        group_description = response.context.get('group').description
        group_slug = response.context.get('group').slug
        self.assertEqual(group_title, 'Тестовая группа')
        self.assertEqual(group_description, 'Тестовое описание')
        self.assertEqual(group_slug, 'test-slug')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        url = reverse('posts:profile', kwargs={
            'username': PostURLTests.author})
        response = self.authorized_client_author.get(url)
        post_text = response.context.get('page_obj')[0].text
        post_author = response.context.get('page_obj')[0].author.username
        group_post = response.context.get('page_obj')[0].group.title
        self.assertEqual(post_text, 'Тестовый пост')
        self.assertEqual(post_author, 'NoNameAuthor')
        self.assertEqual(group_post, 'Тестовая группа')

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        url = reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        response = self.authorized_client_author.get(url)
        post_text = response.context.get('post').text
        post_author = response.context.get('post').author.username
        group_post = response.context.get('post').group.title
        self.assertEqual(post_text, 'Тестовый пост')
        self.assertEqual(post_author, 'NoNameAuthor')
        self.assertEqual(group_post, 'Тестовая группа')
