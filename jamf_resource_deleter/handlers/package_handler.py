import logging
from typing import Optional, Dict
from requests import HTTPError
from .base import ResourceHandler

logger = logging.getLogger(__name__)

# TODO This needs tested to see what the API returns? Does it return the package or does it return metadata


class PackageHandler(ResourceHandler):
    resource_name = "Package"

    def delete(self, resource_id: int) -> bool:
        return self.client.classic.packages.delete_by_id(resource_id)

    def get(self, resource_id: int) -> Optional[Dict]:
        try:
            return self.client.classic.packages.get_by_id(resource_id)
        except HTTPError as e:
            logger.error(
                "Could not retrieve %s %s: %s", self.resource_name, resource_id, e
            )
            return None
        
    def create(self, resource_config: Dict):
        pass
