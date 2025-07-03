from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException, NetMikoAuthenticationException
import json
import yaml
import sys
import re

def restart_snmp_server(host, username, password, use_yaml=False):
    device = {
        'device_type': 'nokia_srl',
        'host': host,
        'username': username,
        'password': password,
    }

    result = {
        'host': host,
        'status': 'unknown',
        'message': '',
        'output': ''
    }

    try:
        net_connect = ConnectHandler(**device)

        # Restart SNMP server application
        net_connect.send_command(
            'tools system app-management application snmp_server-mgmt restart',
            read_timeout=30
        )

        # Check post-restart status
        raw_output = net_connect.send_command(
            'info from state /system app-management application snmp_server-mgmt last-change',
            read_timeout=30
        )

        # Extract last-change timestamp using regex
        match = re.search(r'last-change\s+"([^"]+)"', raw_output)
        last_change_value = match.group(1) if match else ''

        result['output'] = last_change_value

        if "now" in last_change_value.lower():
            result['status'] = 'success'
            result['message'] = "Restart successful (detected 'now')"
        else:
            result['status'] = 'failure'
            result['message'] = "Restart may have failed (no 'now' in output)"

    except NetMikoTimeoutException:
        result['status'] = 'error'
        result['message'] = 'Connection timeout.'
    except NetMikoAuthenticationException:
        result['status'] = 'error'
        result['message'] = 'Authentication failed.'
    except Exception as e:
        result['status'] = 'error'
        result['message'] = f'Unexpected error: {str(e)}'

    # Output in desired format
    if use_yaml:
        print(yaml.safe_dump(result, sort_keys=False))
    else:
        print(json.dumps(result, indent=2))

if __name__ == '__main__':
    # Example usage
    restart_snmp_server(
        host='10.59.132.60',
        username='admin',
        password='NokiaSrl1!',
        use_yaml=False  # Set to True for YAML output
    )
