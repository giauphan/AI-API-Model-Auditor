import httpx
import pytest
import respx

from ai_api_model_auditor.http_client import (AdapterError, AuthError,
                                              HTTPClient, NetworkError)


@pytest.fixture
def client():
    return HTTPClient(timeout=1.0, max_retries=2, retry_delay=0.1)


@respx.mock
def test_http_client_get_success(client):
    respx.get("https://test.com/api").mock(
        return_value=httpx.Response(200, json={"status": "ok"})
    )
    response = client.get("https://test.com/api")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@respx.mock
def test_http_client_auth_error(client):
    respx.get("https://test.com/api").mock(
        return_value=httpx.Response(401, text="Unauthorized")
    )
    with pytest.raises(AuthError, match="Authentication failed"):
        client.get("https://test.com/api")


@respx.mock
def test_http_client_auth_error_403(client):
    respx.get("https://test.com/api").mock(
        return_value=httpx.Response(403, text="Forbidden")
    )
    with pytest.raises(AuthError, match="Authentication failed"):
        client.get("https://test.com/api")


@respx.mock
def test_http_client_http_status_error(client):
    respx.get("https://test.com/api").mock(
        return_value=httpx.Response(500, text="Internal Server Error")
    )
    with pytest.raises(AdapterError, match="HTTP error occurred"):
        client.get("https://test.com/api")


@respx.mock
def test_http_client_network_error_retries(client):
    route = respx.get("https://test.com/api").mock(
        side_effect=httpx.NetworkError("Connection failed")
    )
    with pytest.raises(NetworkError, match="Network error after 2 attempts"):
        client.get("https://test.com/api")
    assert route.call_count == 2


@respx.mock
def test_http_client_timeout_error_retries(client):
    route = respx.get("https://test.com/api").mock(
        side_effect=httpx.TimeoutException("Timeout")
    )
    with pytest.raises(NetworkError, match="Network error after 2 attempts"):
        client.get("https://test.com/api")
    assert route.call_count == 2


@respx.mock
def test_http_client_post_success(client):
    respx.post("https://test.com/api").mock(
        return_value=httpx.Response(201, json={"id": 1})
    )
    response = client.post("https://test.com/api", json={"name": "test"})
    assert response.status_code == 201
    assert response.json() == {"id": 1}
