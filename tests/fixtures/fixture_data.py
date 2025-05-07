import tempfile

import pytest


@pytest.fixture
def post(user):
    from posts.models import Post
    temp_img = tempfile.NamedTemporaryFile(suffix=".jpg").name
    return Post.objects.create(
        text='Содержимое тестового поста 1',
        author=user,
        image=temp_img
    )


@pytest.fixture
def post_2(user, group_1):
    from posts.models import Post
    return Post.objects.create(
        text='Содержимое тестового поста 2',
        author=user,
        group=group_1
    )


@pytest.fixture
def comment_1_post(post, user):
    from posts.models import Comment
    return Comment.objects.create(
        author=user,
        post=post,
        text='Текст первого комментария'
    )


@pytest.fixture
def comment_2_post(post, another_user):
    from posts.models import Comment
    return Comment.objects.create(
        author=another_user,
        post=post,
        text='Текст второго комментария'
    )


@pytest.fixture
def another_post(another_user):
    from posts.models import Post
    return Post.objects.create(
        text='Содержимое альтернативного поста',
        author=another_user
    )


@pytest.fixture
def comment_1_another_post(another_post, user):
    from posts.models import Comment
    return Comment.objects.create(
        author=user,
        post=another_post,
        text='Комментарий к альтернативному посту'
    )


@pytest.fixture
def group_1():
    from posts.models import Group
    return Group.objects.create(
        title='Название первой группы',
        slug='first_group'
    )


@pytest.fixture
def group_2():
    from posts.models import Group
    return Group.objects.create(
        title='Название второй группы',
        slug='second_group'
    )
