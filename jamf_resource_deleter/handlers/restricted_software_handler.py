import logging
from typing import Optional, Dict
from requests import HTTPError
from .base import ResourceHandler

logger = logging.getLogger(__name__)


class RestrictedSoftwareHandler(ResourceHandler):
    resource_name = "Restricted Software"

    def delete(self, resource_id: int) -> bool:
        return self.client.classic.restricted_software.delete_by_id(resource_id)

    def get(self, resource_id: int) -> Optional[Dict]:
        try:
            return self.client.classic.restricted_software.get_by_id(resource_id).json()
        except HTTPError as e:
            logger.error(
                "Could not retrieve %s %s: %s", self.resource_name, resource_id, e
            )
            return None
