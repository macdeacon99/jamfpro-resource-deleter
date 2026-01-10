from dataclasses import dataclass
from typing import Optional, Dict
from enum import Enum


class OperationStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DeletionResult:
    """Result of a deletion operation"""

    resource_type: str
    resource_id: int
    resource_name: str
    status: OperationStatus
    backup_data: Optional[Dict] = None
    error_message: Optional[str] = None

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
    results: list[DeletionResult]
    backup_path: Optional[str] = None
