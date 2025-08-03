from flask import Flask, request, abort
import subprocess
import json
import os
from dotenv import load_dotenv
import logging

app = Flask(__name__)

# Load environment variables from .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default-secret")

config_path = os.path.join(os.path.dirname(__file__), 'HomeAssistantLauncher.json')

# Set up logging to application's root folder
root_folder = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(root_folder, "HomeAssistantLauncher.log")
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

def load_config():
    # Regenerate HA-Rest-Commands.txt if config changes
    config_mtime = os.path.getmtime(config_path)
    ha_config_path = os.path.join(root_folder, "HA-Rest-Commands.txt")
    regenerate = True
    if os.path.exists(ha_config_path):
        ha_mtime = os.path.getmtime(ha_config_path)
        if ha_mtime > config_mtime:
            regenerate = False
    with open(config_path) as f:
        config = json.load(f)
    if regenerate:
        generate_ha_rest_commands(config_path, SECRET_KEY)
        logging.info("Regenerated HA-Rest-Commands.txt due to config change.")
    return config

# This generates a file that can be copied into Home Assitants Configuration
def generate_ha_rest_commands(config_path, secret_key):
    with open(config_path) as f:
        config = json.load(f)
    port = config.get("port", 1204)
    server_ip = config.get("host_ip", "127.0.0.1")  # Use host_ip from config
    lines = ["rest_command:"]
    for url in config:
        if url.startswith("/"):
            name = url.strip("/").replace("-", "_").replace("/", "_")
            lines.append(f"  launch_{name}:")
            lines.append(f'    url: "http://{server_ip}:{port}{url}"')
            lines.append("    method: POST")
            lines.append("    headers:")
            lines.append(f'      Authorization: "Bearer {secret_key}"\n')
    ha_config_path = os.path.join(root_folder, "HA-Rest-Commands.txt")
    with open(ha_config_path, "w") as out:
        out.write("\n".join(lines))
    logging.info("HA-Rest-Commands.txt generated.")

# This deals with the routing of commands against URLs
@app.route('/<path:url>', methods=['POST'])
def dynamic_route(url):
    config = load_config()
    # Allowed hosts check
    allowed_hosts = config.get("allowed_hosts", [])
    remote_addr = request.remote_addr
    if allowed_hosts and remote_addr not in allowed_hosts:
        logging.warning(f"Blocked request from {remote_addr} to /{url}")
        abort(403)
    script = config.get(f"/{url}")
    token = request.headers.get("Authorization")
    if token != f"Bearer {SECRET_KEY}":
        logging.warning(f"Unauthorized access attempt to /{url} from {remote_addr}")
        abort(401)
    if not script:
        logging.warning(f"Script for /{url} not found in config.")
        abort(404)
    try:
        subprocess.run(script, shell=True)
        logging.info(f"Executed script for /{url}: {script}")
        return 'Script executed'
    except Exception as e:
        logging.error(f"Error executing script for /{url}: {e}")
        abort(500, description=str(e))

if __name__ == '__main__':
    config = load_config()
    port = config.get("port", 1204)
    generate_ha_rest_commands(config_path, SECRET_KEY)
    logging.info(f"Home Assistant Launcher started on port {port}.")
    app.run(host='0.0.0.0', port=port)