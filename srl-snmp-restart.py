from netmiko import ConnectHandler
import json
import re
from datetime import datetime

# SR Linux connection details
srl_device = {
    'device_type': 'terminal_server',
    'host': '10.59.132.60',
    'username': 'admin',
    'password': 'NokiaSrl1!',
    'port': 22,
    'fast_cli': False
}

def enter_bash(conn):
    conn.send_command_timing("bash", delay_factor=1)

def run_srcli_json(conn, srcli_cmd):
    full_cmd = f'sr_cli --output-format json {srcli_cmd}'
    output = conn.send_command_timing(full_cmd, delay_factor=2)
    return output

def extract_last_change_from_json(raw_output):
    match = re.search(r'\{.*\}', raw_output, re.DOTALL)
    if not match:
        raise ValueError("JSON not found in sr_cli output")

    json_text = match.group(0)
    data = json.loads(json_text)
    timestamp = data["system"]["app-management"]["application"][0]["last-change"]
    iso_time = timestamp.split(" ")[0]  # Remove "(x minutes ago)"
    return datetime.fromisoformat(iso_time.replace("Z", "+00:00"))

try:
    print("Connecting to SR Linux...")
    conn = ConnectHandler(**srl_device)
    print("✅ Login successful\n")

    enter_bash(conn)

    # Step 1: before restart
    before_raw = run_srcli_json(conn,
        "info from state /system app-management application snmp_server-mgmt last-change")
    before_dt = extract_last_change_from_json(before_raw)

    # Step 2: restart
    conn.send_command_timing(
        "sr_cli tools system app-management application snmp_server-mgmt restart", delay_factor=2)

    # Step 3: after restart
    after_raw = run_srcli_json(conn,
        "info from state /system app-management application snmp_server-mgmt last-change")
    after_dt = extract_last_change_from_json(after_raw)

    # Diff in seconds
    delta_sec = int((after_dt - before_dt).total_seconds())

    print(f"Last-change before restart : {before_dt.isoformat()}")
    print(f"Last-change after restart  : {after_dt.isoformat()}")
    print(f"⏱  Time delta: {delta_sec} seconds")

    conn.disconnect()

except Exception as e:
    print(f"❌ Error: {e}")
