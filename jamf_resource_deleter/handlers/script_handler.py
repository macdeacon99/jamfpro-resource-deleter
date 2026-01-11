import logging
from dicttoxml import dicttoxml
from typing import Optional, Dict
from requests import HTTPError
from .base import ResourceHandler

logger = logging.getLogger(__name__)


class ScriptHandler(ResourceHandler):
    resource_name = "Script"

    def delete(self, resource_id: int) -> bool:
        return self.client.classic.scripts.delete_by_id(resource_id)

    def get(self, resource_id: int) -> Optional[Dict]:
        try:
            return self.client.classic.scripts.get_by_id(resource_id).json()
        except HTTPError as e:
            logger.error(
                "Could not retrieve %s %s: %s", self.resource_name, resource_id, e
            )
            return None

    def create(self, resource_config: Dict) -> tuple[bool, int]:
        xml = self._convert_to_xml(resource_config)

        try:
            success = self.client.classic.scripts.create(xml)
            return success.ok, success.status_code
        except HTTPError as e:
            logger.error("Error: %s", e)
            return success.ok, success.status_code

    def _convert_to_xml(self, resource_config):
        ee_data = resource_config["script"]

        return dicttoxml(ee_data, custom_root="script", attr_type=False)
