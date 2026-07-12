from typing import Any, Optional


def success_response(data: Any, message: str = "Success") -> dict:
    return {"success": True, "message": message, "data": data}


def error_response(message: str, code: Optional[str] = None) -> dict:
    return {"success": False, "message": message, "code": code}


def paginated_response(items: list, total: int, page: int, page_size: int) -> dict:
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }
