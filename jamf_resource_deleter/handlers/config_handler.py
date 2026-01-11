import logging
from typing import Optional, Dict
from requests import HTTPError
from .base import ResourceHandler

logger = logging.getLogger(__name__)


class ComputerConfigProfileHandler(ResourceHandler):
    resource_name = "macOS Configuration Profile"

    def delete(self, resource_id: int) -> bool:
        return self.client.classic.configuration_profiles.delete_by_id(resource_id)

    def get(self, resource_id: int) -> Optional[Dict]:
        try:
            return self.client.classic.configuration_profiles.get_by_id(
                resource_id
            ).json()
        except HTTPError as e:
            logger.error(
                "Could not retrieve %s %s: %s", self.resource_name, resource_id, e
            )
            return None

    def create(self, resource_config: Dict) -> bool:
        # xml = self._json_to_jamf_group_xml_dicttoxml(resource_config)

        xml = ""

        try:
            success = self.client.classic.configuration_profiles.create(xml)
            print(success.text)
            return success.ok, success.status_code
        except HTTPError as e:
            logger.error("Error: %s", e)
            return success.ok, success.status_code
