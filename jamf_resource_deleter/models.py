from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class OperationStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class OperationResult:
    """Result of an operation"""

    resource_type: str
    resource_id: int
    resource_name: str
    status: OperationStatus
    backup_data: Optional[Dict] = None
    error_message: Optional[Any] = None

    @property
    def success(self) -> bool:
        return self.status == OperationStatus.SUCCESS


@dataclass
class BatchResult:
    """Result of a batch deletion operation"""

    total_processed: int
    successful: int
    failed: int
    skipped: int
    results: list[OperationResult]
    backup_path: Optional[Any] = None
