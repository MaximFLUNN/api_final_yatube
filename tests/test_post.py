from http import HTTPStatus

import pytest

from posts.models import Post


class TestPostAPI:
    UPDATED_POST_TEXT = {'text': 'Обновленное содержание публикации'}

    def test_post_not_found(self, client, post):
        posts_endpoint = '/api/v1/posts/'
        response = client.get(posts_endpoint)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт "{posts_endpoint}" не обнаружен. Проверьте '
            'настройки маршрутизации в файле *urls.py*.'
        )

    def test_post_not_auth(self, client, post):
        posts_endpoint = '/api/v1/posts/'
        response = client.get(posts_endpoint)

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            f'GET-запрос неавторизованного пользователя к "{posts_endpoint}" '
            'должен возвращать статус 401.'
        )

    def verify_post_data(self, post_data, request_description, db_post=None):
        required_fields = ('id', 'text', 'author', 'pub_date')
        
        for field in required_fields:
            assert field in post_data, (
                f'Ответ на {request_description} должен содержать '
                f'поле "{field}".'
            )
            
        if db_post:
            assert post_data['author'] == db_post.author.username, (
                f'Ответ на {request_description} должен содержать '
                'корректное имя автора публикации.'
            )
            assert post_data['id'] == db_post.id, (
                f'Ответ на {request_description} должен содержать '
                'корректный идентификатор публикации.'
            )

    @pytest.mark.django_db(transaction=True)
    def test_posts_auth_get(self, user_client, post, another_post):
        posts_endpoint = '/api/v1/posts/'
        response = user_client.get(posts_endpoint)
        
        assert response.status_code == HTTPStatus.OK, (
            f'GET-запрос авторизованного пользователя к "{posts_endpoint}" '
            'должен возвращать статус 200.'
        )

        response_data = response.json()
        assert isinstance(response_data, list), (
            f'GET-запрос авторизованного пользователя к "{posts_endpoint}" '
            'должен возвращать список публикаций.'
        )

        assert len(response_data) == Post.objects.count(), (
            f'GET-запрос авторизованного пользователя к "{posts_endpoint}" '
            'должен возвращать все существующие публикации.'
        )

        first_post = Post.objects.first()
        test_post_data = response_data[0]
        self.verify_post_data(
            test_post_data,
            f'GET-запрос к "{posts_endpoint}"',
            first_post
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_create_auth_with_invalid_data(self, user_client):
        posts_endpoint = '/api/v1/posts/'
        initial_posts_count = Post.objects.count()
        
        response = user_client.post(posts_endpoint, data={})
        
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'POST-запрос с некорректными данными к "{posts_endpoint}" '
            'должен возвращать статус 400.'
        )
        assert initial_posts_count == Post.objects.count(), (
            f'POST-запрос с некорректными данными к "{posts_endpoint}" '
            'не должен создавать новую публикацию.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_create_auth_with_valid_data(self, user_client, user):
        posts_endpoint = '/api/v1/posts/'
        initial_posts_count = Post.objects.count()
        new_post_data = {'text': 'Содержание новой публикации'}
        
        response = user_client.post(posts_endpoint, data=new_post_data)
        
        assert response.status_code == HTTPStatus.CREATED, (
            f'POST-запрос с корректными данными к "{posts_endpoint}" '
            'должен возвращать статус 201.'
        )

        response_data = response.json()
        assert isinstance(response_data, dict), (
            f'POST-запрос к "{posts_endpoint}" должен возвращать '
            'данные новой публикации в виде словаря.'
        )
        
        self.verify_post_data(response_data, f'POST-запрос к "{posts_endpoint}"')
        
        assert response_data.get('text') == new_post_data['text'], (
            f'POST-запрос к "{posts_endpoint}" должен возвращать '
            'текст публикации в неизменном виде.'
        )
        assert response_data.get('author') == user.username, (
            f'POST-запрос к "{posts_endpoint}" должен возвращать '
            'имя пользователя, создавшего публикацию.'
        )
        assert initial_posts_count + 1 == Post.objects.count(), (
            f'POST-запрос с корректными данными к "{posts_endpoint}" '
            'должен создавать новую публикацию.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_unauth_create(self, client, user, another_user):
        posts_endpoint = '/api/v1/posts/'
        initial_posts_count = Post.objects.count()
        new_post_data = {'author': another_user.id, 'text': 'Тестовая публикация'}
        
        response = client.post(posts_endpoint, data=new_post_data)
        
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            f'POST-запрос неавторизованного пользователя к "{posts_endpoint}" '
            'должен возвращать статус 401.'
        )
        assert initial_posts_count == Post.objects.count(), (
            f'POST-запрос неавторизованного пользователя к "{posts_endpoint}" '
            'не должен создавать новую публикацию.'
        )

    def test_post_get_current(self, user_client, post):
        post_detail_endpoint = f'/api/v1/posts/{post.id}/'
        response = user_client.get(post_detail_endpoint)

        assert response.status_code == HTTPStatus.OK, (
            f'Эндпоинт "{post_detail_endpoint}" не найден. Проверьте '
            'настройки маршрутизации в файле *urls.py*.'
        )

        response_data = response.json()
        self.verify_post_data(
            response_data,
            f'GET-запрос к "{post_detail_endpoint}"',
            post
        )

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('http_method', ('put', 'patch'))
    def test_post_change_auth_with_valid_data(self, user_client, post, http_method):
        post_detail_endpoint = f'/api/v1/posts/{post.id}/'
        request_func = getattr(user_client, http_method)
        
        response = request_func(post_detail_endpoint, data=self.UPDATED_POST_TEXT)
        
        http_method_upper = http_method.upper()
        assert response.status_code == HTTPStatus.OK, (
            f'{http_method_upper}-запрос авторизованного пользователя к '
            f'"{post_detail_endpoint}" должен возвращать статус 200.'
        )

        updated_post = Post.objects.filter(id=post.id).first()
        assert updated_post, (
            f'{http_method_upper}-запрос авторизованного пользователя к '
            f'"{post_detail_endpoint}" не должен удалять публикацию.'
        )
        assert updated_post.text == self.UPDATED_POST_TEXT['text'], (
            f'{http_method_upper}-запрос авторизованного пользователя к '
            f'"{post_detail_endpoint}" должен обновлять содержание публикации.'
        )

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('http_method', ('put', 'patch'))
    def test_post_change_not_auth_with_valid_data(self, client, post, http_method):
        post_detail_endpoint = f'/api/v1/posts/{post.id}/'
        request_func = getattr(client, http_method)
        
        response = request_func(post_detail_endpoint, data=self.UPDATED_POST_TEXT)
        
        http_method_upper = http_method.upper()
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            f'{http_method_upper}-запрос неавторизованного пользователя к '
            f'"{post_detail_endpoint}" должен возвращать статус 401.'
        )
        
        db_post = Post.objects.filter(id=post.id).first()
        assert db_post.text != self.UPDATED_POST_TEXT['text'], (
            f'{http_method_upper}-запрос неавторизованного пользователя к '
            f'"{post_detail_endpoint}" не должен изменять содержание публикации.'
        )

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('http_method', ('put', 'patch'))
    def test_post_change_not_author_with_valid_data(self, user_client, another_post, http_method):
        post_detail_endpoint = f'/api/v1/posts/{another_post.id}/'
        request_func = getattr(user_client, http_method)
        
        response = request_func(post_detail_endpoint, data=self.UPDATED_POST_TEXT)
        
        http_method_upper = http_method.upper()
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            f'{http_method_upper}-запрос авторизованного пользователя к '
            f'"{post_detail_endpoint}" для чужой публикации должен '
            'возвращать статус 403.'
        )

        db_post = Post.objects.filter(id=another_post.id).first()
        assert db_post.text != self.UPDATED_POST_TEXT['text'], (
            f'{http_method_upper}-запрос авторизованного пользователя к '
            f'"{post_detail_endpoint}" для чужой публикации не должен '
            'изменять ее содержание.'
        )

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('http_method', ('put', 'patch'))
    def test_post_patch_auth_with_invalid_data(self, user_client, post, http_method):
        post_detail_endpoint = f'/api/v1/posts/{post.id}/'
        request_func = getattr(user_client, http_method)
        
        response = request_func(
            post_detail_endpoint,
            data={'text': {}},
            format='json'
        )
        
        http_method_upper = http_method.upper()
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'{http_method_upper}-запрос с некорректными данными к '
            f'"{post_detail_endpoint}" должен возвращать статус 400.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_delete_by_author(self, user_client, post):
        post_detail_endpoint = f'/api/v1/posts/{post.id}/'
        response = user_client.delete(post_detail_endpoint)
        
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            f'DELETE-запрос автора публикации к "{post_detail_endpoint}" '
            'должен возвращать статус 204.'
        )

        deleted_post = Post.objects.filter(id=post.id).first()
        assert not deleted_post, (
            f'DELETE-запрос автора публикации к "{post_detail_endpoint}" '
            'должен удалять публикацию.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_delete_not_author(self, user_client, another_post):
        post_detail_endpoint = f'/api/v1/posts/{another_post.id}/'
        response = user_client.delete(post_detail_endpoint)
        
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            f'DELETE-запрос авторизованного пользователя к "{post_detail_endpoint}" '
            'для чужой публикации должен возвращать статус 403.'
        )

        post_exists = Post.objects.filter(id=another_post.id).first()
        assert post_exists, (
            'Авторизованный пользователь не должен иметь возможности '
            'удалять чужие публикации.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_unauth_delete_current(self, client, post):
        post_detail_endpoint = f'/api/v1/posts/{post.id}/'
        response = client.delete(post_detail_endpoint)
        
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            f'DELETE-запрос неавторизованного пользователя к "{post_detail_endpoint}" '
            'должен возвращать статус 401.'
        )
        
        post_exists = Post.objects.filter(id=post.id).first()
        assert post_exists, (
            f'DELETE-запрос неавторизованного пользователя к "{post_detail_endpoint}" '
            'не должен удалять публикацию.'
        )
