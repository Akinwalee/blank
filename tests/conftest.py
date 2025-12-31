import pytest

from blank.core.routing import get_routes, post_routes
from blank.testing import Client


@pytest.fixture(autouse=True)
def clear_routes():
    """Clear all registered routes before each test.
    
    This fixture runs automatically before every test to ensure
    route isolation - routes registered in one test don't leak
    into other tests.
    """
    get_routes.clear()
    post_routes.clear()
    
    yield
    
    get_routes.clear()
    post_routes.clear()


@pytest.fixture
def client():
    """Provide a Client instance for making test requests.
    
    Example:
        def test_get_user(client):
            response = client.get('/users/42')
            assert response.status_code == 200
    """
    return Client()
