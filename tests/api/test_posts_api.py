import pytest
from playwright.sync_api import APIRequestContext

from models.user import User
from utils.json_compare import assert_json_deep_equal


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.readonly
def test_get_post_by_id(api_context: APIRequestContext) -> None:
    response = api_context.get("/posts/1")

    assert response.status == 200
    post = response.json()
    assert post["id"] == 1
    assert post["userId"] == 1
    assert isinstance(post["title"], str) and post["title"]


@pytest.mark.regression
@pytest.mark.readonly
def test_filter_posts_by_user(api_context: APIRequestContext) -> None:
    response = api_context.get("/posts", params={"userId": 1})

    assert response.status == 200
    posts = response.json()
    assert posts
    assert all(post["userId"] == 1 for post in posts)


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.readonly
def test_get_users_as_models_and_find_by_name(api_context: APIRequestContext) -> None:
    response = api_context.get("/users")

    assert response.status == 200
    users = [User.from_json(user_data) for user_data in response.json()]
    target_user = next((user for user in users if user.name == "Clementine Bauch"), None)

    assert len(users) == 10
    assert target_user is not None
    assert target_user.id == 3
    assert target_user.email == "Nathan@yesenia.net"


@pytest.mark.regression
def test_create_post(api_context: APIRequestContext) -> None:
    payload = {"title": "API test post", "body": "Created by Playwright", "userId": 1}
    response = api_context.post("/posts", data=payload)

    assert response.status == 201
    created_post = response.json()
    assert created_post["id"] == 101
    assert created_post["title"] == payload["title"]
    assert created_post["body"] == payload["body"]
    assert created_post["userId"] == payload["userId"]


@pytest.mark.regression
def test_update_post_with_exact_json_comparison(api_context: APIRequestContext) -> None:
    expected = {
        "id": 1,
        "title": "Updated title",
        "body": "Updated body",
        "userId": 1,
    }
    response = api_context.put("/posts/1", data=expected)

    assert response.status == 200
    actual = response.json()
    assert actual == expected


@pytest.mark.regression
def test_delete_post(api_context: APIRequestContext) -> None:
    response = api_context.delete("/posts/1")

    assert response.status == 200
    assert response.json() == {}


@pytest.mark.regression
def test_deep_json_comparison_reports_nested_path() -> None:
    actual = {"id": 7, "address": {"city": "London"}}
    expected = {"id": 7, "address": {"city": "Paris"}}

    with pytest.raises(AssertionError, match=r"root\.address\.city"):
        assert_json_deep_equal(actual, expected)