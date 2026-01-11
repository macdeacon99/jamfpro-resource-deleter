import logging
import json
from typing import Optional, Dict
from dicttoxml import dicttoxml
from requests import RequestException, Response
from .base import ResourceHandler

logger = logging.getLogger(__name__)


class ComputerConfigProfileHandler(ResourceHandler):
    resource_name = "macOS Configuration Profile"

    def delete(self, resource_id: int) -> Response:
        return self.client.classic.configuration_profiles.delete_by_id(resource_id)

    def get(self, resource_id: int) -> Optional[Dict]:
        try:
            return self.client.classic.configuration_profiles.get_by_id(
                resource_id
            ).json()
        except RequestException as e:
            logger.error(
                "Could not retrieve %s %s: %s", self.resource_name, resource_id, e
            )
            return None

    def create(self, resource_config: Dict) -> tuple[bool, int]:
        xml = self._json_to_jamf_profile_xml_dicttoxml(resource_config)

        try:
            success = self.client.classic.configuration_profiles.create(xml)
            return success.ok, success.status_code
        except RequestException as e:
            logger.error("Error: %s", e)
            return success.ok, success.status_code

    def _json_to_jamf_profile_xml_dicttoxml(self, config_data: Dict) -> str:
        """
        Convert configuration profile data to Jamf Pro API XML format using dicttoxml.
        Expects the 'configuration' object directly.
        """

        # Parse JSON if it's a string
        if isinstance(config_data, str):
            data = json.loads(config_data)
        else:
            data = config_data

        # Extract the os_x_configuration_profile data
        profile_data = data.get("os_x_configuration_profile", {})

        # Prepare data for conversion
        clean_data: Dict = {}

        # Handle general section
        if "general" in profile_data:
            general = profile_data["general"]
            clean_data["general"] = {}

            if "name" in general:
                clean_data["general"]["name"] = general["name"]
            if "description" in general:
                clean_data["general"]["description"] = general["description"]
            if "site" in general:
                clean_data["general"]["site"] = {
                    "id": general["site"].get("id", -1),
                    "name": general["site"].get("name", "NONE"),
                }
            if "category" in general:
                clean_data["general"]["category"] = {
                    "id": general["category"].get("id", -1),
                    "name": general["category"].get("name", "No category assigned"),
                }
            if "distribution_method" in general:
                clean_data["general"]["distribution_method"] = general[
                    "distribution_method"
                ]
            if "user_removable" in general:
                clean_data["general"]["user_removable"] = str(
                    general["user_removable"]
                ).lower()
            if "level" in general:
                clean_data["general"]["level"] = general["level"]
            if "uuid" in general:
                clean_data["general"]["uuid"] = general["uuid"]
            if "redeploy_on_update" in general:
                clean_data["general"]["redeploy_on_update"] = general[
                    "redeploy_on_update"
                ]
            if "payloads" in general:
                clean_data["general"]["payloads"] = general["payloads"]

        # Handle scope section
        if "scope" in profile_data:
            scope = profile_data["scope"]
            clean_data["scope"] = {}

            if "all_computers" in scope:
                clean_data["scope"]["all_computers"] = str(
                    scope["all_computers"]
                ).lower()
            if "all_jss_users" in scope:
                clean_data["scope"]["all_jss_users"] = str(
                    scope["all_jss_users"]
                ).lower()

            # Handle arrays in scope
            for key in [
                "computers",
                "buildings",
                "departments",
                "computer_groups",
                "jss_users",
                "jss_user_groups",
            ]:
                if key in scope and scope[key]:
                    clean_data["scope"][key] = scope[key]

            # Handle limitations
            if "limitations" in scope:
                clean_data["scope"]["limitations"] = {}
                for key in ["users", "user_groups", "network_segments", "ibeacons"]:
                    if key in scope["limitations"] and scope["limitations"][key]:
                        clean_data["scope"]["limitations"][key] = scope["limitations"][
                            key
                        ]

            # Handle exclusions
            if "exclusions" in scope:
                clean_data["scope"]["exclusions"] = {}
                for key in [
                    "computers",
                    "buildings",
                    "departments",
                    "computer_groups",
                    "users",
                    "user_groups",
                    "network_segments",
                    "ibeacons",
                    "jss_users",
                    "jss_user_groups",
                ]:
                    if key in scope["exclusions"] and scope["exclusions"][key]:
                        clean_data["scope"]["exclusions"][key] = scope["exclusions"][
                            key
                        ]

        # Handle self_service section
        if "self_service" in profile_data:
            ss = profile_data["self_service"]
            clean_data["self_service"] = {}

            if "self_service_display_name" in ss:
                clean_data["self_service"]["self_service_display_name"] = ss[
                    "self_service_display_name"
                ]
            if "install_button_text" in ss:
                clean_data["self_service"]["install_button_text"] = ss[
                    "install_button_text"
                ]
            if "self_service_description" in ss:
                clean_data["self_service"]["self_service_description"] = ss[
                    "self_service_description"
                ]
            if "force_users_to_view_description" in ss:
                clean_data["self_service"]["force_users_to_view_description"] = str(
                    ss["force_users_to_view_description"]
                ).lower()

            if "security" in ss:
                clean_data["self_service"]["security"] = {}
                if "removal_disallowed" in ss["security"]:
                    clean_data["self_service"]["security"]["removal_disallowed"] = ss[
                        "security"
                    ]["removal_disallowed"]

            if "self_service_icon" in ss and ss["self_service_icon"]:
                clean_data["self_service"]["self_service_icon"] = ss[
                    "self_service_icon"
                ]

            if "feature_on_main_page" in ss:
                clean_data["self_service"]["feature_on_main_page"] = str(
                    ss["feature_on_main_page"]
                ).lower()

            if "self_service_categories" in ss and ss["self_service_categories"]:
                clean_data["self_service"]["self_service_categories"] = ss[
                    "self_service_categories"
                ]

            if "notification" in ss:
                clean_data["self_service"]["notification"] = ss["notification"]
            if "notification_subject" in ss:
                clean_data["self_service"]["notification_subject"] = ss[
                    "notification_subject"
                ]
            if "notification_message" in ss:
                clean_data["self_service"]["notification_message"] = ss[
                    "notification_message"
                ]

        # Convert to XML
        xml = dicttoxml(
            clean_data,
            custom_root="os_x_configuration_profile",
            attr_type=False,
            item_func=lambda x: self._get_item_name(x),
        )

        # Convert bytes to string and clean up
        xml_string = xml.decode("utf-8")

        # Fix boolean values
        xml_string = xml_string.replace(">True<", ">true<")
        xml_string = xml_string.replace(">False<", ">false<")

        return xml_string

    def _get_item_name(self, parent_name):
        """
        Custom function to determine the item name for lists in XML.
        """
        item_names = {
            "computers": "computer",
            "buildings": "building",
            "departments": "department",
            "computer_groups": "computer_group",
            "jss_users": "user",
            "jss_user_groups": "user_group",
            "users": "user",
            "user_groups": "user_group",
            "network_segments": "network_segment",
            "ibeacons": "ibeacon",
            "self_service_categories": "category",
        }
        return item_names.get(parent_name, "item")
