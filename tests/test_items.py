import pytest
from fastapi import status

class TestItems:
    def test_create_item_success(self, client, auth_headers):
        item_data = {
            "title": "Test Item",
            "description": "This is a test item"
        }
        response = client.post("/items/", json=item_data, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["title"] == item_data["title"]
        assert response.json()["description"] == item_data["description"]
        assert "id" in response.json()

    def test_read_items_success(self, client, auth_headers):
        # First create an item
        item_data = {"title": "Test Item", "description": "Test Description"}
        client.post("/items/", json=item_data, headers=auth_headers)
        
        # Then try to read items
        response = client.get("/items/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
        assert len(response.json()) > 0
        assert "title" in response.json()[0]
        assert "description" in response.json()[0]

    def test_read_item_success(self, client, auth_headers):
        # First create an item
        item_data = {"title": "Test Item", "description": "Test Description"}
        create_response = client.post("/items/", json=item_data, headers=auth_headers)
        item_id = create_response.json()["id"]
        
        # Then try to read the item
        response = client.get(f"/items/{item_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == item_id
        assert response.json()["title"] == item_data["title"]

    def test_update_item_success(self, client, auth_headers):
        # First create an item
        item_data = {"title": "Old Title", "description": "Old Description"}
        create_response = client.post("/items/", json=item_data, headers=auth_headers)
        item_id = create_response.json()["id"]
        
        # Then update the item
        update_data = {"title": "Updated Title", "description": "Updated Description"}
        response = client.put(
            f"/items/{item_id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["title"] == update_data["title"]
        assert response.json()["description"] == update_data["description"]

    def test_delete_item_success(self, client, auth_headers):
        # First create an item
        item_data = {"title": "Item to Delete", "description": "Will be deleted"}
        create_response = client.post("/items/", json=item_data, headers=auth_headers)
        item_id = create_response.json()["id"]
        
        # Then delete the item
        response = client.delete(f"/items/{item_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"ok": True}
        
        # Verify the item is deleted
        get_response = client.get(f"/items/{item_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_item_unauthorized(self, client):
        item_data = {"title": "Test Item", "description": "Should fail"}
        response = client.post("/items/", json=item_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_read_items_unauthorized(self, client):
        response = client.get("/items/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_item_not_found(self, client, auth_headers):
        update_data = {"title": "Nonexistent", "description": "Should not exist"}
        response = client.put(
            "/items/999999",  # Non-existent ID
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
