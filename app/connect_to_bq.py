from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

credentials = service_account.Credentials.from_service_account_file("jcaguas_service_account_key.json")

project_id = "<gcp-project-id>"					# "integral-zephyr-237909"

client = bigquery.Client(credentials=credentials,project=project_id)

bqDataset = "<bq-dataset>" 									# "tm_exam"
bqTable = "<bq-table>"										# "daily_checkins"

def filterByUser(user):
	sql = """
		SELECT *
		FROM {bqDataset}.{bqTable}
		WHERE user = '{user}'
	""".format(bqDataset=bqDataset, bqTable=bqTable, user=user)

	return client.query(sql).to_dataframe()

def getDistinctUsers():
	sql = """
		SELECT DISTINCT user
		FROM {bqDataset}.{bqTable}
	""".format(bqDataset=bqDataset, bqTable=bqTable)

	users = client.query(sql).to_dataframe()["user"].values

	return users
