import logging
from dicttoxml import dicttoxml
from typing import Optional, Dict
from requests import HTTPError
from .base import ResourceHandler

logger = logging.getLogger(__name__)


class PolicyHandler(ResourceHandler):
    resource_name = "Policy"

    def delete(self, resource_id: int) -> bool:
        return self.client.classic.policies.delete_by_id(resource_id)

    def get(self, resource_id: int) -> Optional[Dict]:
        try:
            return self.client.classic.policies.get_by_id(resource_id).json()
        except HTTPError as e:
            logger.error(
                "Could not retrieve %s %s: %s", self.resource_name, resource_id, e
            )
            return None

    def create(self, resource_config: Dict) -> bool:
        xml = self._policy_json_to_jamf_xml(resource_config)

        try:
            success = self.client.classic.computer_extension_attributes.create(xml)

            return success.ok, success.status_code
        except HTTPError as e:
            logger.error("Error: %s", e)
            return success.ok, success.status_code

    JAMF_ALLOWED_TOP_LEVEL_KEYS = {
        "general",
        "scope",
        "self_service",
        "packages",
        "scripts",
        "printers",
        "dock_items",
        "account_maintenance",
        "reboot",
        "maintenance",
        "files_processes",
        "user_interaction",
        "disk_encryption"
    }


    def _normalize_for_jamf(self, value):
        """
        Recursively normalize JSON so Jamf accepts the XML:
        - Booleans -> 'true' / 'false'
        - Empty lists -> empty dict (Jamf hates <item/>)
        - Remove None values
        """
        if isinstance(value, bool):
            return "true" if value else "false"

        if isinstance(value, dict):
            return {
                k: self._normalize_for_jamf(v)
                for k, v in value.items()
                if v is not None
            }

        if isinstance(value, list):
            if not value:
                return {}  # Jamf expects empty parent nodes
            return [self._normalize_for_jamf(v) for v in value]

        return value


    def _policy_json_to_jamf_xml(self, policy_json: dict) -> str:
        """
        Convert Jamf policy JSON to Jamf Classic API XML
        """

        policy = policy_json["configuration"]["policy"]

        # Remove UI / read-only fields Jamf rejects
        policy.get("general", {}).pop("id", None)

        # Convert package_configuration → packages
        if "package_configuration" in policy:
            policy["packages"] = policy["package_configuration"].get("packages", [])
            policy.pop("package_configuration")

        # Remove unsupported top-level keys
        policy = {
            k: v for k, v in policy.items()
            if k in self.JAMF_ALLOWED_TOP_LEVEL_KEYS
        }

        normalized_policy = self._normalize_for_jamf(policy)

        xml_bytes = dicttoxml(
            normalized_policy,
            custom_root="policy",
            attr_type=False
        )

        return xml_bytes
