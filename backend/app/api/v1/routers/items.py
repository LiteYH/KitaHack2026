"""
Items API router.

Handles HTTP endpoints for item management using ItemsService.
"""
from typing import List

from fastapi import APIRouter, HTTPException, status

from app.schemas.item import Item, ItemCreate, ItemUpdate
from app.services.items import ItemsService

router = APIRouter(prefix="/items", tags=["items"])

# Initialize service (in-memory for now)
_items_service = ItemsService()


@router.get("/", response_model=List[Item], summary="List all items")
async def list_items():
    """
    Retrieve all items.
    
    Returns:
        List of all items in the system.
    """
    return await _items_service.list_items()


@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED, summary="Create a new item")
async def create_item(payload: ItemCreate):
    """
    Create a new item.
    
    Args:
        payload: Item creation data containing name and optional description.
        
    Returns:
        The newly created item with assigned ID and timestamp.
    """
    return await _items_service.create_item(payload)


@router.get("/{item_id}", response_model=Item, summary="Get item by ID")
async def get_item(item_id: int):
    """
    Retrieve a specific item by ID.
    
    Args:
        item_id: The unique identifier of the item.
        
    Returns:
        The requested item.
        
    Raises:
        HTTPException: 404 if item not found.
    """
    item = await _items_service.get_item(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return item


@router.patch("/{item_id}", response_model=Item, summary="Update item")
async def update_item(item_id: int, payload: ItemUpdate):
    """
    Update an existing item.
    
    Args:
        item_id: The unique identifier of the item to update.
        payload: Updated item data (name and/or description).
        
    Returns:
        The updated item.
        
    Raises:
        HTTPException: 404 if item not found.
    """
    updated = await _items_service.update_item(item_id, payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return updated


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete item")
async def delete_item(item_id: int):
    """
    Delete an item by ID.
    
    Args:
        item_id: The unique identifier of the item to delete.
        
    Raises:
        HTTPException: 404 if item not found.
    """
    deleted = await _items_service.delete_item(item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return None
