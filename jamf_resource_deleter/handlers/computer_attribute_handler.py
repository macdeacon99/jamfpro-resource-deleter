import logging
from typing import Optional, Dict
from dicttoxml import dicttoxml
from requests import HTTPError
from .base import ResourceHandler

logger = logging.getLogger(__name__)
dicttoxml_logger = logging.getLogger("dicttoxml")
dicttoxml_logger.setLevel(logging.ERROR)


class ComputerAttributeHandler(ResourceHandler):
    resource_name = "Computer Extension Attribute"

    def delete(self, resource_id: int) -> bool:
        # TODO - Add in error handling for resources that are already deleted
        return self.client.classic.computer_extension_attributes.delete_by_id(
            resource_id
        )

    def get(self, resource_id: int) -> Optional[Dict]:
        try:
            return self.client.classic.computer_extension_attributes.get_by_id(
                resource_id
            ).json()
        except HTTPError as e:
            logger.error(
                "Could not retrieve %s %s: %s", self.resource_name, resource_id, e
            )
            return None

    def create(self, resource_config: Dict) -> tuple[bool, str]:
        xml = self._convert_to_xml(resource_config)

        try:
            success = self.client.classic.computer_extension_attributes.create(xml)

            return success.ok, success.status_code
        except HTTPError as e:
            logger.error("Error: %s", e)
            return success.ok, success.status_code

    def _convert_to_xml(self, resource_config) -> str:
        ee_data = resource_config["computer_extension_attribute"]

        return dicttoxml(
            ee_data, custom_root="computer_extension_attribute", attr_type=False
        )
