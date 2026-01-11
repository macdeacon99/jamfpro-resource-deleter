import logging
from dicttoxml import dicttoxml
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

    def create(self, resource_config: Dict) -> bool:
        xml = self._convert_to_xml(resource_config)

        try:
            success = self.client.classic.policies.create(xml)
            print(success.text)
            return success.ok, success.status_code
        except HTTPError as e:
            logger.error("Error: %s", e)
            return success.ok, success.status_code
        
    def _convert_to_xml(self, resource_config):
        ee_data = resource_config["restricted_software"]

        return dicttoxml(ee_data, custom_root="restricted_software", attr_type=False)