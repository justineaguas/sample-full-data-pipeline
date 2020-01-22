import os
import sys
import subprocess
import pytz
import dateparser
import pandas as pd
import shutil
from pathlib import Path
from datetime import datetime

# Set file directories
homeDir = "<cloud-shell-home>"								# "/home/justineaguas26"
targetPath = "{}/<target-path>".format(homeDir)				# "/home/justineaguas26/"
outputPath = "{}/<output-path>".format(homeDir)				# "/home/justineaguas26/output"
outputFile = "<output-file-name>"							# "dailycheckins.csv"					
outputFileClean = "<clean-output-file-name>"				# "dailycheckins_clean.csv"
gsBucket = "gs://<source-bucket-name>/"						# "gs://<>/data"
gsBucketOut = "gs://<output-bucket-name>/"					# "gs://<>/output"		
passphraseFile = "{}/gpg_keys/text.txt".format(homeDir)		# "/home/justineaguas26/gpg_keys/text.txt"

def cleanTimestamp(dirtyTs):
	"""
	Cleans timestamp from different languages/timezones and standardizes it to Asia/Singapore timezone
	"""
	localTz = pytz.timezone("Asia/Singapore")
	cleanTs = dateparser.parse(dirtyTs)
	if cleanTs.tzinfo is None:
		return cleanTs
	if cleanTs.tzinfo is not None:
		convertedTs = cleanTs.astimezone(localTz)
		return convertedTs

def copyToLocal(gsBucket, targetPath):
	"""
	Copies files from the Google Cloud Storage bucket to local directory
	"""
	print("{} -- Collecting data from GCS...".format(datetime.now().isoformat()))
	subprocess.call("gsutil cp -r {gsBucket} {targetPath}".format(gsBucket=gsBucket, targetPath=targetPath), shell=True)
	print("{} -- GCS copy successful...".format(datetime.now().isoformat()))

def createCleanDirectory(path):
	if os.path.exists(path):
		shutil.rmtree(path)

	os.mkdir(path)

createCleanDirectory(targetPath)
createCleanDirectory(outputPath)

# Import data from Google Cloud Storage
copyToLocal(gsBucket, targetPath)

# Decrypt GPG file
subprocess.call("gpg --batch --passphrase-file {passphraseFile} --output {outputPath}/{outputFile} --decrypt {targetPath}/data/dailycheckins.csv.gpg".format(passphraseFile=passphraseFile,
																																							 outputPath=outputPath, 
																																							 outputFile=outputFile, 
																																							 targetPath=targetPath), 
shell=True)

# Cleaning the data
checkinsDF = pd.read_csv("{outputPath}/{outputFile}".format(outputPath=outputPath, outputFile=outputFile))

# Standardize timestamp to Asia/Singapore
# Assumption is timestamp without timezone information is Asia/Singapore
print("Cleaning timestamp data...")
checkinsDF['new_timestamp'] = checkinsDF['timestamp'].apply(lambda x: cleanTimestamp(x).strftime("%Y-%m-%d %H:%M:%S"))

# Check if there are null values
# Column user has 5 NaN values
print(checkinsDF.isnull().sum())

# Drop nulls
checkinsDF = checkinsDF.dropna()

# Drop old timestamp column
checkinsDF = checkinsDF.drop("timestamp",axis=1)

print(checkinsDF.shape)
print(checkinsDF.isnull().sum())
print(checkinsDF.head())
print(checkinsDF.columns)

checkinsDF.to_csv(path_or_buf="{outputPath}/{outputFileClean}".format(outputPath=outputPath, outputFileClean=outputFileClean), index=False)

subprocess.call("gsutil cp {outputPath}/{outputFileClean} {gsBucketOut}".format(outputPath=outputPath, outputFileClean=outputFileClean, gsBucketOut=gsBucketOut), shell=True)
