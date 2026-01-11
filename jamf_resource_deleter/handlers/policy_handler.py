import logging
from dicttoxml import dicttoxml
from typing import Optional, Dict
from requests import RequestException, Response
from .base import ResourceHandler

logger = logging.getLogger(__name__)


class PolicyHandler(ResourceHandler):
    resource_name = "Policy"

    def delete(self, resource_id: int) -> Response:
        return self.client.classic.policies.delete_by_id(resource_id)

    def get(self, resource_id: int) -> Optional[Dict]:
        try:
            return self.client.classic.policies.get_by_id(resource_id).json()
        except RequestException as e:
            logger.error(
                "Could not retrieve %s %s: %s", self.resource_name, resource_id, e
            )
            return None

    def create(self, resource_config: Dict) -> tuple[bool, int]:
        xml = self._convert_to_xml(resource_config)

        try:
            success = self.client.classic.policies.create(xml)
            return success.ok, success.status_code
        except RequestException as e:
            logger.error("Error: %s", e)
            return success.ok, success.status_code

    def _convert_to_xml(self, resource_config: Dict) -> str:
        ee_data = resource_config["policy"]

        return dicttoxml(ee_data, custom_root="policy", attr_type=False)
