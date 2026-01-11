import logging
from typing import Optional, Dict
from dicttoxml import dicttoxml
from requests import HTTPError
from .base import ResourceHandler

logger = logging.getLogger(__name__)


class ComputerGroupHandler(ResourceHandler):
    resource_name = "Computer Group"

    def delete(self, resource_id: int) -> bool:
        return self.client.classic.computer_groups.delete_by_id(resource_id)

    def get(self, resource_id: int) -> Optional[Dict]:
        try:
            return self.client.classic.computer_groups.get_by_id(resource_id).json()
        except HTTPError as e:
            logger.error(
                "Could not retrieve %s %s: %s", self.resource_name, resource_id, e
            )
            return None

    def create(self, resource_config: Dict) -> bool:
        xml = self._convert_to_xml(resource_config)

        try:
            success = self.client.classic.computer_groups.create(xml)

            return success.ok, success.status_code
        except HTTPError as e:
            logger.error("Error: %s", e)
            return success.ok, success.status_code

    def _convert_to_xml(self, resource_config):
        ee_data = resource_config["unusedComputerGroups"]

        return dicttoxml(
            ee_data, custom_root="computer_extension_attribute", attr_type=False
        )
