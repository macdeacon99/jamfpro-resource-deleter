import logging
from typing import Optional, Dict
from dicttoxml import dicttoxml
from requests import HTTPError
from .base import ResourceHandler

logger = logging.getLogger(__name__)


class ComputerAttributeHandler(ResourceHandler):
    resource_name = "Computer Extension Attribute"

    def delete(self, resource_id: int) -> bool:
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

    def create(self, resource_config: Dict) -> bool:
        # TODO - find a way of returning overall result

        xml = self._convert_to_xml(resource_config)

        try:
            success = self.client.classic.computer_extension_attributes.create(
                xml
            )

            print(success.ok)
        except HTTPError as e:
            print(f"Error: {e}")


    def _convert_to_xml(self, resource_config):

        ee_data = resource_config["computer_extension_attribute"]

        return dicttoxml(ee_data, custom_root='computer_extension_attribute', attr_type=False)
