import logging
from typing import Optional, Dict
from xml.dom.minidom import parseString
import json
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
        xml = self._convert_all_unused_groups(resource_config)

        print(xml)

        try:
            success = self.client.classic.computer_groups.create(xml)
            print(success.text)
            return success.ok, success.status_code
        except HTTPError as e:
            logger.error("Error: %s", e)
            return success.ok, success.status_code

    def _json_to_jamf_group_xml_dicttoxml(self, json_data):
        """
        Convert JSON computer group data to Jamf Pro API XML format using dicttoxml.
        """
        
        # Parse JSON if it's a string
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        # Extract the computer_group data
        group_data = data.get('configuration', {}).get('computer_group', {})
        
        # Prepare data for conversion
        # Remove fields that shouldn't be in the XML for creation (like id)
        clean_data = {}
        
        if 'name' in group_data:
            clean_data['name'] = group_data['name']
        
        if 'is_smart' in group_data:
            clean_data['is_smart'] = str(group_data['is_smart']).lower()
        
        if 'site' in group_data:
            clean_data['site'] = {
                'id': group_data['site'].get('id', -1),
                'name': group_data['site'].get('name', 'NONE')
            }
        
        # Handle criteria for smart groups
        if 'criteria' in group_data and group_data['criteria']:
            clean_data['criteria'] = []
            for criterion in group_data['criteria']:
                crit = {}
                if 'name' in criterion:
                    crit['name'] = criterion['name']
                if 'priority' in criterion:
                    crit['priority'] = criterion['priority']
                if 'and_or' in criterion:
                    crit['and_or'] = criterion['and_or']
                if 'search_type' in criterion:
                    crit['search_type'] = criterion['search_type']
                if 'value' in criterion:
                    crit['value'] = criterion['value']
                if 'opening_paren' in criterion:
                    crit['opening_paren'] = str(criterion['opening_paren']).lower()
                if 'closing_paren' in criterion:
                    crit['closing_paren'] = str(criterion['closing_paren']).lower()
                
                clean_data['criteria'].append(crit)
        
        # Handle computers for static groups
        if 'computers' in group_data and group_data['computers']:
            clean_data['computers'] = []
            for computer in group_data['computers']:
                # Only include computer ID for API calls
                if 'id' in computer:
                    clean_data['computers'].append({'id': computer['id']})
        
        # Convert to XML
        xml = dicttoxml(
            clean_data,
            custom_root='computer_group',
            attr_type=False,
            item_func=lambda x: 'criterion' if x == 'criteria' else 'computer' if x == 'computers' else x
        )
        
        # Convert bytes to string and clean up
        xml_string = xml.decode('utf-8')
        
        # Fix boolean values (True -> true, False -> false)
        xml_string = xml_string.replace('<is_smart>True</is_smart>', '<is_smart>true</is_smart>')
        xml_string = xml_string.replace('<is_smart>False</is_smart>', '<is_smart>false</is_smart>')
        
        # Pretty print
        dom = parseString(xml_string)
        return dom.toprettyxml(indent="  ")


    def _convert_all_unused_groups(self, json_data):
        """
        Process the entire unusedComputerGroups structure.
        """
        
        # Load data
        if isinstance(json_data, str):
            try:
                with open(json_data, 'r') as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = json.loads(json_data)
        else:
            data = json_data
        
        results = {}
        
        for group in data.get('unusedComputerGroups', []):
            group_name = group.get('name', f"group_{group.get('id')}")
            xml_output = self._json_to_jamf_group_xml_dicttoxml(group)
            results[group_name] = xml_output
        
        return results
