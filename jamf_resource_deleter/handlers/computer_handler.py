import logging
from typing import Optional, Dict
from requests import HTTPError, Response
from .base import ResourceHandler

logger = logging.getLogger(__name__)


class ComputerHandler(ResourceHandler):
    resource_name = "Computer"

    def delete(self, resource_id: int) -> Response:
        return self.client.classic.computers.delete_by_id(resource_id)

    def get(self, resource_id: int) -> Optional[Dict]:
        try:
            return self.client.classic.computers.get_by_id(resource_id).json()
        except HTTPError as e:
            logger.error(
                "Could not retrieve %s %s: %s", self.resource_name, resource_id, e
            )
            return None

    def create(self, resource_config: Dict) -> tuple[bool, int]:
        logger.warning("Computers will not be re-created - please re-enrol the device")
        return True, 200
