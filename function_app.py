import logging
from typing import Optional
import yaml
import os
import azure.functions as func
from dotenv import load_dotenv
from tuya_connector import TuyaOpenAPI

app = func.FunctionApp()


load_dotenv(".env")
API_ENDPOINT = os.getenv("API_ENDPOINT")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
IR_REMOTE_ID = os.getenv("IR_REMOTE_ID")
AIRCON_ID = os.getenv("AIRCON_ID")
SMART_PLUG_ID = os.getenv("SMART_PLUG_ID")
THS_SENSOR_ID = os.getenv("THS_SENSOR_ID")
DEVICES_ENDPOINT = "/v1.0/iot-03/devices"

# Init settings - client, config, etc
openapi = TuyaOpenAPI(
    endpoint=API_ENDPOINT, access_id=CLIENT_ID, access_secret=CLIENT_SECRET
)
config = {}
with open('func-config.yml', 'r') as f:
    config = yaml.safe_load(f)
schedule  = config['base-configs']['schedule']
plug_status_endpoint = f"{DEVICES_ENDPOINT}/{SMART_PLUG_ID}/status"
ths_status_endpoint = f"{DEVICES_ENDPOINT}/{THS_SENSOR_ID}/status"

#TODO : Add real sensor values
@app.schedule(
    schedule=schedule, arg_name="myTimer", run_on_startup=True, use_monitor=False
)
def control_humidifier(myTimer: func.TimerRequest) -> None:
    """Controls air humidity via smart plug and sensor

    Args:
        myTimer (func.TimerRequest): _description_
    """
    logging.info("Python timer trigger function executed.")
    openapi.connect()

    plug_status = openapi.get(path=plug_status_endpoint).get("result")[0]
    ths_result_list = openapi.get(path=ths_status_endpoint).get("result")
    
    humidity = [r for r in ths_result_list if r["code"]=="va_humidity"][0]
    plug_on = plug_status["value"]
    switch_on = False

    if not plug_on and humidity["value"] < 45:
        switch_on = True
   
    payload = {"commands": [{"code": "switch_1", "value": switch_on}]}
    plug_command_endpoint = f"{DEVICES_ENDPOINT}/{SMART_PLUG_ID}/commands"
    response = openapi.post(path=plug_command_endpoint, body=payload)
    logging.info(f"SUCCESS. Device status: {response}")

    
