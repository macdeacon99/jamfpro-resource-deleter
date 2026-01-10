from abc import ABC, abstractmethod
from jamfpy import Tenant


class ResourceHandler(ABC):
    """Base Class for resource handling"""

    def __init__(self, client: Tenant):
        self.client = client

    @abstractmethod
    def delete(self, resource_id: int) -> bool:
        """Delete a resource by ID"""
        pass

    @abstractmethod
    def get(self, resource_id: int) -> bool:
        """Get a resource by ID"""
        pass

    @property
    @abstractmethod
    def resource_name(self) -> str:
        """Human readable resource name"""
        pass
