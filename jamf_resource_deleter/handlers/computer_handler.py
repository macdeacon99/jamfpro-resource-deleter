import logging
from typing import Optional, Dict
from base import ResourceHandler
from requests import HTTPError

logger = logging.getLogger(__name__)


class ComputerHandler(ResourceHandler):
    resource_name = "Computer"

    def delete(self, resource_id: int) -> bool:
        return self.client.classic.computers.delete_by_id(resource_id)

    def get(self, resource_id: int) -> Optional[Dict]:
        try:
            return self.client.classic.computers.get_by_id(resource_id).json()
        except HTTPError as e:
            logger.error(
                "Could not retrieve %s %s: %s", self.resource_name, resource_id, e
            )
            return None
