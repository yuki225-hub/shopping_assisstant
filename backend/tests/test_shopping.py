import pytest

pytestmark = pytest.mark.asyncio

TEST_USER = {"username": "shopuser", "email": "shop@example.com", "password": "shoppass123"}


async def get_auth_token(client) -> str:
    await client.post("/api/v1/auth/register", json=TEST_USER)
    login = await client.post("/api/v1/auth/login", json={
        "email": TEST_USER["email"], "password": TEST_USER["password"]
    })
    return login.json()["access_token"]


async def test_search_products(client):
    response = await client.get("/api/v1/search?q=laptop")
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert "price_comparison" in data
    assert "review_analysis" in data
    assert "recommendation" in data
    assert data["query"] == "laptop"
    assert len(data["products"]) > 0


async def test_search_with_filters(client):
    response = await client.get("/api/v1/search?q=phone&min_price=1000&max_price=50000&sort_by=price_asc")
    assert response.status_code == 200
    data = response.json()
    prices = [p["price"] for p in data["products"] if p["price"]]
    if len(prices) > 1:
        assert prices == sorted(prices)


async def test_search_with_platform_filter(client):
    response = await client.get("/api/v1/search?q=shoes&platforms=amazon,flipkart")
    assert response.status_code == 200
    data = response.json()
    platforms = {p["platform"].lower() for p in data["products"]}
    assert platforms.issubset({"amazon", "flipkart"})


async def test_price_comparison_structure(client):
    response = await client.get("/api/v1/search?q=headphones")
    data = response.json()
    pc = data["price_comparison"]
    assert "lowest_price" in pc
    assert "highest_price" in pc
    assert "average_price" in pc
    assert "comparison_table" in pc
    assert pc["lowest_price"] <= pc["highest_price"]


async def test_recommendation_structure(client):
    response = await client.get("/api/v1/search?q=tv")
    data = response.json()
    rec = data["recommendation"]
    assert "best_overall" in rec
    assert "score" in rec
    assert 0 <= rec["score"] <= 100


async def test_analyze_reviews(client):
    response = await client.post("/api/v1/analyze-reviews", json={
        "reviews": [
            "This product is excellent and amazing quality!",
            "Terrible product, very disappointed, waste of money",
            "Average product, nothing special",
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert "overall_sentiment" in data
    assert "positive_percent" in data
    assert "negative_percent" in data


async def test_wishlist_requires_auth(client):
    response = await client.get("/api/v1/wishlist")
    assert response.status_code == 403


async def test_wishlist_flow(client):
    token = await get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Search to get a product
    search = await client.get("/api/v1/search?q=watch", headers=headers)
    products = search.json()["products"]
    assert len(products) > 0
    product_id = products[0]["id"]

    # Add to wishlist
    add = await client.post("/api/v1/wishlist", json={"product_id": product_id}, headers=headers)
    assert add.status_code == 201

    # Get wishlist
    get = await client.get("/api/v1/wishlist", headers=headers)
    assert get.status_code == 200
    assert len(get.json()) >= 1

    # Remove from wishlist
    wishlist_id = add.json()["id"]
    delete = await client.delete(f"/api/v1/wishlist/{wishlist_id}", headers=headers)
    assert delete.status_code == 204


async def test_search_history(client):
    token = await get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    await client.get("/api/v1/search?q=camera", headers=headers)

    history = await client.get("/api/v1/history", headers=headers)
    assert history.status_code == 200
    queries = [h["query"] for h in history.json()]
    assert "camera" in queries


async def test_dashboard(client):
    token = await get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/dashboard", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_searches" in data
    assert "wishlist_count" in data
