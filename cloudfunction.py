# cloud function file
import pandas as pd
from json import loads
from json import dumps
import base64
import logging
import ast
from google.cloud.storage import Client

class loadStorage:

    def __init__(self,event,context):
        self.event = event
        self.context = context
        self.bucket_name = "capstone-project1"
    
    def get_message(self):
        logging.info(
                f"This function was triggred by messageId (self.context.event_id)) published at {self.context.timestamp}"
                f"to {self.context.resource['name']}"
                )
        if "data" in self.event:
            message = base64.b64decode(self.event["data"]).decode('utf-8')
            logging.info(message)
            return message
        else:
            logging.error("Incorrect format")
            return ""                
                
    def transform_to_dataframe(self, message):
        
        try:
            df = pd.DataFrame(loads(message))
            if not df.empty:
                logging.info(f'Created Dataframe with {df.shape[0]} rows and {df.shape[1]} columns')
            else:
                logging.warning(f'Created empty dataframe')
            return df
        except Exception as e:
            logging.error(f'Error - {str(e)}')
            raise
    
    def upload_to_bucket(self, df, filename: str = "payload"):
        storage_client = Client()
        bucket = storage_client.bucket(self.bucket_name)
        blob = bucket.blob(f'{filename}.csv')
        
        blob.upload_from_string(data = df.to_csv(index=False), content_type='text/csv')
        logging.info(f'file uploaded')
        
def currency(event, context):
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    string1 = "Temperature Anomaly"
    string2 = "All natural disasters"

    obj = loadStorage(event, context)

    message = obj.get_message()
    processed_message = ast.literal_eval(message)

    upload_df = obj.transform_to_dataframe(dumps(processed_message))

    if string1 in processed_message:
        obj.upload_to_bucket(upload_df, "capstone_data")
    else:
        obj.upload_to_bucket(upload_df, "capstone_data1")
