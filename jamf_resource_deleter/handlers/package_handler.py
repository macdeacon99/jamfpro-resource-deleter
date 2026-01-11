import logging
from typing import Optional, Dict
from requests import RequestException, Response
from .base import ResourceHandler

logger = logging.getLogger(__name__)


class PackageHandler(ResourceHandler):
    resource_name = "Package"

    def delete(self, resource_id: int) -> Response:
        return self.client.classic.packages.delete_by_id(resource_id)

    def get(self, resource_id: int) -> Optional[Dict]:
        try:
            return self.client.classic.packages.get_by_id(resource_id).json()
        except RequestException as e:
            logger.error(
                "Could not retrieve %s %s: %s", self.resource_name, resource_id, e
            )
            return None

    def create(self, resource_config: Dict) -> tuple[bool, int]:
        logger.warning("Cannot retrieve or re-create mac apps, so will not continue")
        return True, 200
