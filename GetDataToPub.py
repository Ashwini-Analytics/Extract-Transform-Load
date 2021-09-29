import pandas as pd
from google.cloud import pubsub_v1
from concurrent import futures
from typing import Callable
from time import sleep

class GetDataToPub:
    publish_futures = []

    def __init__(self):
        self.project_id = "capstone-327117"
        self.topic_id = "publish-data-to-gcs"
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(self.project_id, self.topic_id)
        


    def global_temperature(self):
        # Load the global temperature dataset and store it in a dataframe
        temperature_data = pd.read_csv('GlobalTemperatures.csv')
        global_temperature_df = temperature_data.copy()

        # Choose the required columns
        global_temperature_df = global_temperature_df[['dt', 'LandAndOceanAverageTemperature']]

        # Set the date column as a DateTimeIndex and sort it
        global_temperature_df['dt'] = pd.to_datetime(global_temperature_df['dt'])
        global_temperature_df.set_index('dt', inplace = True)
        global_temperature_df.sort_index(axis = 0, inplace = True)

        # Resample annually and rename index & columns
        global_temperature_df = global_temperature_df.resample('A').mean()
        global_temperature_df.rename(columns = {'LandAndOceanAverageTemperature': 'AnnualAverageTemp'}, inplace = True)
        global_temperature_df.index.rename('Year', inplace = True)
        global_temperature_df.index = global_temperature_df.index.year

        # drop null values
        global_temperature_df[global_temperature_df['AnnualAverageTemp'].isnull()].index
        global_temperature_df.dropna(inplace = True)

        # Calculate the global baseline temperature
        global_ref_temp = global_temperature_df.loc['1951':'1980'].mean()['AnnualAverageTemp']

        # Create the temperature anomaly column
        global_temperature_df['Temperature Anomaly'] = global_temperature_df['AnnualAverageTemp'] - global_ref_temp
        global_temperature_df.drop(['AnnualAverageTemp'], axis = 1, inplace = True)
        global_temperature_df['year'] = global_temperature_df.index
        data = global_temperature_df.to_json()
        return data

    def natural_disaster(self):
        # Load the natural disaster dataset and store it in a dataframe
        disaster_data = pd.read_csv('number-of-natural-disaster-events.csv')
        natural_disaster_df = disaster_data.copy()

        # Remove the 'Code' column
        natural_disaster_df.drop(['Code'], axis = 1, inplace = True)
        # Check the different types of 'Entity' values
        natural_disaster_df['Entity'].unique()


        # Pivot the dataframe
        natural_disaster_df = natural_disaster_df.pivot(index = 'Year', columns = 'Entity', values = 'Number of reported natural disasters (reported disasters)')
        natural_disaster_df.drop(['Impact'], axis = 1, inplace = True)

        # Handle missing values and rename columns
        natural_disaster_df.fillna(value = 0, inplace = True)
        natural_disaster_df['year'] = natural_disaster_df.index
        data = natural_disaster_df.to_json()
        return data

    def get_callback(self, publish_future: pubsub_v1.publisher.futures.Future, data: str) -> Callable[
        [pubsub_v1.publisher.futures.Future], None]:
        def callback(publish_future: pubsub_v1.publisher.futures.Future) -> None:
            try:
                # Wait 60 seconds for the publish call to succeed.
                print(publish_future.result(timeout=60))
            except futures.TimeoutError:
                print(f"Publishing {data} timed out.")

        return callback

    def publish_to_topic(self, i):
        data = str(i)
        # When you publish a message, the client returns a future.
        publish_future = self.publisher.publish(self.topic_path, data.encode("utf-8"))
        # Non-blocking. Publish failures are handled in the callback function.
        publish_future.add_done_callback(self.get_callback(publish_future, data))
        self.publish_futures.append(publish_future)


def getAndPublish():
#if __name__ == '__main__':

    obj = GetDataToPub()

    temperature = obj.global_temperature()
    disaster = obj.natural_disaster()

    obj.publish_to_topic(temperature)
    sleep(5)
    obj.publish_to_topic(disaster)

    # Wait for all the publish futures to resolve before exiting.
    futures.wait(obj.publish_futures, return_when=futures.ALL_COMPLETED)
    print(f"Published message successfully.")
