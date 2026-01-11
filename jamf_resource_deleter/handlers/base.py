from abc import ABC, abstractmethod
from typing import Dict, Optional
from requests import Response
from jamfpy import Tenant


class ResourceHandler(ABC):
    """Base Class for resource handling"""

    def __init__(self, client: Tenant):
        self.client = client

    @abstractmethod
    def delete(self, resource_id: int) -> Response:
        """Delete a resource by ID"""
        pass

    @abstractmethod
    def get(self, resource_id: int) -> Optional[Dict]:
        """Get a resource by ID"""
        pass

    @abstractmethod
    def create(self, resource_config: Dict) -> tuple[bool, int]:
        """Create a resource based on backup data"""
        pass

    @property
    @abstractmethod
    def resource_name(self) -> str:
        """Human readable resource name"""
        pass
