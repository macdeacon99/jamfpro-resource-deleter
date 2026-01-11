import logging
import json
from dicttoxml import dicttoxml
from typing import Optional, Dict
from requests import HTTPError
from .base import ResourceHandler

logger = logging.getLogger(__name__)


class ComputerHandler(ResourceHandler):
    resource_name = "Computer"

    def delete(self, resource_id: int) -> bool:
        return self.client.classic.computers.delete_by_id(resource_id)

    def get(self, resource_id: int) -> Optional[Dict]:
        try:
            return self.client.classic.computers.get_by_id(resource_id).json()
        except HTTPError as e:
            logger.error(
                "Could not retrieve %s %s: %s", self.resource_name, resource_id, e
            )
            return None

    def create(self, resource_config: Dict) -> bool:
        xml = self._json_to_jamf_computer_xml_dicttoxml(resource_config)

        try:
            success = self.client.classic.computer_extension_attributes.create(xml)

            return success.ok, success.status_code
        except HTTPError as e:
            logger.error("Error: %s", e)
            return success.ok, success.status_code

    def _json_to_jamf_computer_xml_dicttoxml(self, config_data):
        """
        Convert computer configuration data to Jamf Pro API XML format using dicttoxml.
        Expects the 'configuration' object directly.
        """
        
        # Parse JSON if it's a string
        if isinstance(config_data, str):
            data = json.loads(config_data)
        else:
            data = config_data
        
        # Extract the computer data
        computer_data = data.get('computer', {})
        
        # Prepare data for conversion
        clean_data = {}
        
        # Handle general section
        if 'general' in computer_data:
            general = computer_data['general']
            clean_data['general'] = {}
            
            # Basic fields
            for field in ['name', 'network_adapter_type', 'mac_address', 
                        'alt_network_adapter_type', 'alt_mac_address', 'ip_address',
                        'serial_number', 'udid', 'jamf_version', 'platform',
                        'barcode_1', 'barcode_2', 'asset_tag']:
                if field in general:
                    clean_data['general'][field] = general[field]
            
            # Remote management
            if 'remote_management' in general:
                rm = general['remote_management']
                clean_data['general']['remote_management'] = {}
                if 'managed' in rm:
                    clean_data['general']['remote_management']['managed'] = str(rm['managed']).lower()
                if 'management_username' in rm:
                    clean_data['general']['remote_management']['management_username'] = rm['management_username']
            
            # Boolean fields
            if 'supervised' in general:
                clean_data['general']['supervised'] = str(general['supervised']).lower()
            if 'mdm_capable' in general:
                clean_data['general']['mdm_capable'] = str(general['mdm_capable']).lower()
            
            # Site
            if 'site' in general:
                clean_data['general']['site'] = {
                    'id': general['site'].get('id', -1),
                    'name': general['site'].get('name', 'NONE')
                }
        
        # Handle location section
        if 'location' in computer_data:
            location = computer_data['location']
            clean_data['location'] = {}
            
            for field in ['username', 'realname', 'real_name', 'email_address',
                        'position', 'phone', 'phone_number', 'department', 
                        'building', 'room']:
                if field in location:
                    clean_data['location'][field] = location[field]
        
        # Handle purchasing section
        if 'purchasing' in computer_data:
            purchasing = computer_data['purchasing']
            clean_data['purchasing'] = {}
            
            if 'is_purchased' in purchasing:
                clean_data['purchasing']['is_purchased'] = str(purchasing['is_purchased']).lower()
            if 'is_leased' in purchasing:
                clean_data['purchasing']['is_leased'] = str(purchasing['is_leased']).lower()
            
            for field in ['po_number', 'vendor', 'applecare_id', 'purchase_price',
                        'purchasing_account', 'po_date', 'warranty_expires',
                        'lease_expires', 'life_expectancy', 'purchasing_contact',
                        'os_applecare_id', 'os_maintenance_expires']:
                if field in purchasing:
                    clean_data['purchasing'][field] = purchasing[field]
            
            if 'attachments' in purchasing and purchasing['attachments']:
                clean_data['purchasing']['attachments'] = purchasing['attachments']
        
        # Handle peripherals (if any)
        if 'peripherals' in computer_data and computer_data['peripherals']:
            clean_data['peripherals'] = computer_data['peripherals']
        
        # Handle hardware section
        if 'hardware' in computer_data:
            hardware = computer_data['hardware']
            clean_data['hardware'] = {}
            
            for field in ['make', 'model', 'model_identifier', 'os_name', 'os_version',
                        'os_build', 'processor_type', 'processor_architecture',
                        'processor_speed', 'processor_speed_mhz', 'number_processors',
                        'number_cores', 'total_ram', 'total_ram_mb', 'boot_rom',
                        'bus_speed', 'bus_speed_mhz', 'battery_capacity', 'cache_size',
                        'cache_size_kb', 'available_ram_slots', 'optical_drive',
                        'nic_speed', 'smc_version', 'xprotect_version',
                        'institutional_recovery_key', 'disk_encryption_configuration']:
                if field in hardware:
                    clean_data['hardware'][field] = hardware[field]
            
            # Boolean fields
            for field in ['is_apple_silicon', 'ble_capable', 'supports_ios_app_installs']:
                if field in hardware:
                    clean_data['hardware'][field] = str(hardware[field]).lower()
            
            # Arrays
            for field in ['storage', 'mapped_printers', 'filevault2_users']:
                if field in hardware and hardware[field]:
                    clean_data['hardware'][field] = hardware[field]
        
        # Handle certificates (if any)
        if 'certificates' in computer_data and computer_data['certificates']:
            clean_data['certificates'] = computer_data['certificates']
        
        # Handle security section
        if 'security' in computer_data:
            security = computer_data['security']
            clean_data['security'] = {}
            
            if 'activation_lock' in security:
                clean_data['security']['activation_lock'] = str(security['activation_lock']).lower()
            if 'recovery_lock_enabled' in security:
                clean_data['security']['recovery_lock_enabled'] = str(security['recovery_lock_enabled']).lower()
            if 'firewall_enabled' in security:
                clean_data['security']['firewall_enabled'] = str(security['firewall_enabled']).lower()
            
            for field in ['secure_boot_level', 'external_boot_level']:
                if field in security:
                    clean_data['security'][field] = security[field]
        
        # Handle software section
        if 'software' in computer_data:
            software = computer_data['software']
            clean_data['software'] = {}
            
            for field in ['unix_executables', 'licensed_software', 'installed_by_casper',
                        'installed_by_jamf_pro', 'installed_by_installer_swu',
                        'cached_by_casper', 'cached_by_jamf_pro', 
                        'available_software_updates', 'available_updates',
                        'running_services', 'applications', 'fonts', 'plugins']:
                if field in software and software[field]:
                    clean_data['software'][field] = software[field]
        
        # Handle extension attributes
        if 'extension_attributes' in computer_data and computer_data['extension_attributes']:
            clean_data['extension_attributes'] = []
            for ea in computer_data['extension_attributes']:
                ea_clean = {}
                if 'id' in ea:
                    ea_clean['id'] = ea['id']
                if 'name' in ea:
                    ea_clean['name'] = ea['name']
                if 'type' in ea:
                    ea_clean['type'] = ea['type']
                if 'value' in ea:
                    ea_clean['value'] = ea['value']
                clean_data['extension_attributes'].append(ea_clean)
        
        # Handle groups_accounts section
        if 'groups_accounts' in computer_data:
            ga = computer_data['groups_accounts']
            clean_data['groups_accounts'] = {}
            
            if 'computer_group_memberships' in ga and ga['computer_group_memberships']:
                clean_data['groups_accounts']['computer_group_memberships'] = ga['computer_group_memberships']
            
            if 'local_accounts' in ga and ga['local_accounts']:
                clean_data['groups_accounts']['local_accounts'] = ga['local_accounts']
            
            if 'user_inventories' in ga:
                clean_data['groups_accounts']['user_inventories'] = {}
                if 'disable_automatic_login' in ga['user_inventories']:
                    clean_data['groups_accounts']['user_inventories']['disable_automatic_login'] = \
                        str(ga['user_inventories']['disable_automatic_login']).lower()
        
        # Convert to XML
        xml = dicttoxml(
            clean_data,
            custom_root='computer',
            attr_type=False,
            item_func=lambda x: self._get_computer_item_name(x)
        )
        
        # Convert bytes to string and clean up
        xml_string = xml.decode('utf-8')
        
        # Fix boolean values
        xml_string = xml_string.replace('>True<', '>true<')
        xml_string = xml_string.replace('>False<', '>false<')
        
        return xml_string


    def _get_computer_item_name(self, parent_name):
        """
        Custom function to determine the item name for lists in computer XML.
        """
        item_names = {
            'peripherals': 'peripheral',
            'storage': 'device',
            'mapped_printers': 'printer',
            'filevault2_users': 'user',
            'certificates': 'certificate',
            'unix_executables': 'unix_executable',
            'licensed_software': 'licensed_software',
            'installed_by_casper': 'package',
            'installed_by_jamf_pro': 'package',
            'installed_by_installer_swu': 'package',
            'cached_by_casper': 'package',
            'cached_by_jamf_pro': 'package',
            'available_software_updates': 'update',
            'available_updates': 'update',
            'running_services': 'service',
            'applications': 'application',
            'fonts': 'font',
            'plugins': 'plugin',
            'extension_attributes': 'extension_attribute',
            'computer_group_memberships': 'group',
            'local_accounts': 'user',
            'attachments': 'attachment'
        }
        return item_names.get(parent_name, 'item')
