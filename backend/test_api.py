"""
Quick test script to verify backend setup.
Run this after starting the server to test all endpoints.
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health check endpoint."""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"✅ Health: {response.json()}")
    assert response.status_code == 200


def test_items_crud():
    """Test complete CRUD flow for items."""
    print("\n--- Testing Items CRUD ---")
    
    # 1. List items (should be empty)
    print("\n1. List items (empty)...")
    response = requests.get(f"{BASE_URL}/api/v1/items/")
    items = response.json()
    print(f"✅ Items: {items}")
    assert response.status_code == 200
    assert items == []
    
    # 2. Create item
    print("\n2. Create new item...")
    new_item = {
        "name": "Summer Campaign",
        "description": "Social media campaign for summer sale"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/items/",
        json=new_item
    )
    created = response.json()
    print(f"✅ Created: {json.dumps(created, indent=2)}")
    assert response.status_code == 201
    assert created["name"] == new_item["name"]
    item_id = created["id"]
    
    # 3. Get item by ID
    print(f"\n3. Get item {item_id}...")
    response = requests.get(f"{BASE_URL}/api/v1/items/{item_id}")
    item = response.json()
    print(f"✅ Retrieved: {json.dumps(item, indent=2)}")
    assert response.status_code == 200
    
    # 4. Update item
    print(f"\n4. Update item {item_id}...")
    update_data = {
        "name": "Updated Summer Campaign",
        "description": "Updated description"
    }
    response = requests.patch(
        f"{BASE_URL}/api/v1/items/{item_id}",
        json=update_data
    )
    updated = response.json()
    print(f"✅ Updated: {json.dumps(updated, indent=2)}")
    assert response.status_code == 200
    assert updated["name"] == update_data["name"]
    
    # 5. List items (should have 1)
    print("\n5. List items (should have 1)...")
    response = requests.get(f"{BASE_URL}/api/v1/items/")
    items = response.json()
    print(f"✅ Items: {len(items)} item(s)")
    assert len(items) == 1
    
    # 6. Delete item
    print(f"\n6. Delete item {item_id}...")
    response = requests.delete(f"{BASE_URL}/api/v1/items/{item_id}")
    print(f"✅ Deleted: {response.status_code}")
    assert response.status_code == 204
    
    # 7. Verify deletion
    print(f"\n7. Verify item {item_id} is deleted...")
    response = requests.get(f"{BASE_URL}/api/v1/items/{item_id}")
    print(f"✅ Not found (expected): {response.status_code}")
    assert response.status_code == 404
    
    print("\n✅ All CRUD operations passed!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("BossolutionAI Backend Test Suite")
    print("=" * 60)
    print(f"\nTesting backend at: {BASE_URL}")
    print("Make sure the server is running (python main.py)")
    print()
    
    try:
        test_health()
        test_items_crud()
        print("\n" + "=" * 60)
        print("🎉 All tests passed! Backend is working correctly.")
        print("=" * 60)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend.")
        print("Make sure the server is running:")
        print("  cd backend")
        print("  python main.py")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
