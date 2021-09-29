
from airflow import DAG
from datetime import timedelta, datetime
from airflow.contrib.operators.gcs_to_bq import GoogleCloudStorageToBigQueryOperator
from airflow.operators import dummy_operator
from airflow.operators.python_operator import PythonOperator
from google.cloud import bigquery

YESTERDAY = datetime.now() - timedelta(days=1)
DAG_NAME = "capstone_dag"

# default parameters of the dag
default_args = {
    'owner': 'capstone',
    'depends_on_past': False,
    'start_date': YESTERDAY,
    'email': ['ragitashwiniwork@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

# This dag parameters will be applied to all the dags
dag = DAG(
    dag_id="capstone_dag",
    default_args=default_args,
    schedule_interval="*/5 * * * *",
    catchup=False,
    description="capstone_dag",
    max_active_runs=5,
)

start = dummy_operator.DummyOperator(task_id="start", dag=dag)
end = dummy_operator.DummyOperator(task_id="end", dag=dag)

#-----------------------------------------------------------------------------------------------------------------------------

def gcs_to_bigquery_disaster():
    # Construct a BigQuery client object.
    client = bigquery.Client()
    table_id = "dataset.disaster"
    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("All_natural_disasters", "Float"),
            bigquery.SchemaField("Drought", "Float"),
            bigquery.SchemaField("Earthquake", "Float"),
            bigquery.SchemaField("Extreme_temperature", "Float"),
            bigquery.SchemaField("Extreme_weather", "Float"),
            bigquery.SchemaField("Flood", "Float"),
            bigquery.SchemaField("Landslide", "Float"),
            bigquery.SchemaField("Mass_movement", "Float"),
            bigquery.SchemaField("Volcanic_activity", "Float"),
            bigquery.SchemaField("Wildfire", "Float"),
            bigquery.SchemaField("year", "INTEGER"),
        ],
        skip_leading_rows=1,
        # The source format defaults to CSV, so the line below is optional.
        source_format=bigquery.SourceFormat.CSV,
    )
    uri = "gs://capstone-project1/capstone_data1.csv"
    load_job = client.load_table_from_uri(
        uri, table_id, job_config=job_config
    )  # Make an API request.
    load_job.result()  # Waits for the job to complete.
    destination_table = client.get_table(table_id)  # Make an API request.
    print("Loaded {} rows.".format(destination_table.num_rows))

#-------------------------------------------------------------------------------------------------------------------------------

def gcs_to_bigquery_temp():
        
    client = bigquery.Client()
    table_id = "dataset.temperature"
    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("TemperatureAnomaly", "FLOAT"),
            bigquery.SchemaField("year", "INTEGER"),
        ],
        skip_leading_rows=1,
        # The source format defaults to CSV, so the line below is optional.
        source_format=bigquery.SourceFormat.CSV,
    )
    uri = "gs://capstone-project1/capstone_data.csv"
    load_job = client.load_table_from_uri(
        uri, table_id, job_config=job_config
    )  # Make an API request.
    load_job.result()  # Waits for the job to complete.
    destination_table = client.get_table(table_id)  # Make an API request.
    print("Loaded {} rows.".format(destination_table.num_rows))
 
# ---------------------------------------------------------------------------------------------------------------------------- 

gcs_to_bigquery_disaster = PythonOperator(
    task_id='gcs_to_bigquery_disaster',
    python_callable=gcs_to_bigquery_disaster,
    dag=dag,
)

gcs_to_bigquery_temp = PythonOperator(
    task_id='gcs_to_bigquery_temp',
    python_callable=gcs_to_bigquery_temp,
    dag=dag,
)


# This is how the dag will work.
start >> gcs_to_bigquery_disaster >> gcs_to_bigquery_temp >> end