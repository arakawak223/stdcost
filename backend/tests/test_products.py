"""Product API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_products(client: AsyncClient):
    # Create a product
    response = await client.post("/api/v1/masters/products", json={
        "code": "TEST01",
        "name": "テスト製品01",
        "product_group": "テスト",
        "unit": "kg",
        "standard_lot_size": "1000",
    })
    assert response.status_code == 201
    product = response.json()
    assert product["code"] == "TEST01"
    assert product["name"] == "テスト製品01"
    product_id = product["id"]

    # List products
    response = await client.get("/api/v1/masters/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 1

    # Get single product
    response = await client.get(f"/api/v1/masters/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["code"] == "TEST01"

    # Update product
    response = await client.put(f"/api/v1/masters/products/{product_id}", json={
        "name": "テスト製品01（更新）",
    })
    assert response.status_code == 200
    assert response.json()["name"] == "テスト製品01（更新）"

    # Delete product
    response = await client.delete(f"/api/v1/masters/products/{product_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_duplicate_product_code(client: AsyncClient):
    await client.post("/api/v1/masters/products", json={
        "code": "DUP01",
        "name": "重複テスト",
        "unit": "kg",
    })
    response = await client.post("/api/v1/masters/products", json={
        "code": "DUP01",
        "name": "重複テスト2",
        "unit": "kg",
    })
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_product_search(client: AsyncClient):
    await client.post("/api/v1/masters/products", json={
        "code": "SRCH01",
        "name": "検索テスト製品",
        "product_group": "検索グループ",
        "unit": "L",
    })
    response = await client.get("/api/v1/masters/products", params={"search": "検索テスト"})
    assert response.status_code == 200
    assert len(response.json()) >= 1
