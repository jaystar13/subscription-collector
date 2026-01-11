from typing import Generic, TypeVar, List, Optional, Tuple
from pydantic import BaseModel
import base64
from datetime import datetime

T = TypeVar("T")

class CursorPage(BaseModel, Generic[T]):
    items: List[T]
    next_cursor: Optional[str] = None

def encode_cursor(published_at: datetime, item_id: int) -> str:
    """커서를 인코딩합니다."""
    cursor_str = f"{published_at.isoformat()}|{item_id}"
    return base64.b64encode(cursor_str.encode("utf-8")).decode("utf-8")

def decode_cursor(cursor: str) -> Tuple[datetime, int]:
    """인코딩된 커서를 디코딩합니다."""
    try:
        decoded_str = base64.b64decode(cursor.encode("utf-8")).decode("utf-8")
        parts = decoded_str.split("|")
        if len(parts) != 2:
            raise ValueError("Invalid cursor format")
        
        published_at_str, item_id_str = parts
        published_at = datetime.fromisoformat(published_at_str)
        item_id = int(item_id_str)
        
        return published_at, item_id
    except (base64.binascii.Error, ValueError, IndexError) as e:
        raise ValueError("Invalid cursor") from e
