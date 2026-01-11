import logging
from xml.dom.minidom import parseString
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
            print(success.text)
            return success.ok, success.status_code
        except HTTPError as e:
            logger.error("Error: %s", e)
            return success.ok, success.status_code

    
    LIST_NODE_MAP = {
        "scripts": "script",
        "packages": "package",
        "computers": "computer",
        "computer_groups": "computer_group",
        "buildings": "building",
        "departments": "department",
        "users": "user",
        "user_groups": "user_group",
        "network_segments": "network_segment",
        "ibeacons": "ibeacon",
        "dock_items": "dock_item",
    }


    def _jamf_bool(self, value):
        return "true" if value is True else "false" if value is False else value


    def _normalize(self, value, parent_key=None):
        if isinstance(value, bool):
            return self._jamf_bool(value)

        if isinstance(value, dict):
            out = {}
            for k, v in value.items():
                if v in ({}, [], None, ""):
                    continue
                out[k] = self._normalize(v, k)
            return out

        if isinstance(value, list):
            if not value:
                return None

            node_name = self.LIST_NODE_MAP.get(parent_key, "item")
            return {node_name: [self._normalize(v) for v in value if v not in ("", None)]}

        return value

    def _normalize_triggers(self, general: dict):
        triggers = []

        if general.pop("trigger_checkin", False):
            triggers.append("checkin")

        if general.pop("trigger_login", False):
            triggers.append("login")

        if general.pop("trigger_startup", False):
            triggers.append("startup")

        if general.pop("trigger_enrollment_complete", False):
            triggers.append("enrollment")

        # USER_INITIATED == selfservice
        if general.pop("trigger_other", None) == "USER_INITIATED":
            triggers.append("selfservice")

        # Remove invalid fields
        general.pop("trigger", None)

        # Inject correct Classic API triggers
        if triggers:
            general["trigger"] = triggers

    def _policy_json_to_jamf_xml(self, policy_json: dict) -> str:
            policy = policy_json["policy"]

            # --- GENERAL CLEANUP ---
            general = policy["general"]
            general.pop("id", None)
            general.pop("retry_attempts", None)
            general.pop("network_requirements", None)

            # 🔴 THIS IS THE IMPORTANT LINE
            self._normalize_triggers(general)

            # --- PACKAGE CONFIG ---
            if "package_configuration" in policy:
                policy["packages"] = policy["package_configuration"]["packages"]
                del policy["package_configuration"]

            # --- REMOVE INVALID KEYS ---
            policy.pop("printers", None)

            # --- NORMALIZE FOR XML ---
            normalized = self._normalize(policy)

            xml = dicttoxml(
                normalized,
                custom_root="policy",
                attr_type=False
            )
            print(xml)
            dom = parseString(xml)
            return dom.toprettyxml(indent="  ")
