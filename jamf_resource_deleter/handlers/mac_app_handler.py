from typing import Dict, Optional
from requests import Response
import logging
from .base import ResourceHandler

logger = logging.getLogger(__name__)


class MacAppsHandler(ResourceHandler):
    resource_name = "Mac App"

    def delete(self, resource_id: int) -> Response:
        return self.client.pro.app_installers.delete(resource_id)

    def get(self, resource_id: int) -> Optional[Dict]:
        logger.warning("Cannot retrieve or re-create mac apps, so will not continue")
        return None

    def create(self, resource_config: Dict) -> tuple[bool, int]:
        logger.warning("Cannot retrieve or re-create mac apps, so will not continue")
        return True, 200
