import boto3
import ID
import Multi

s3 = boto3.resource('s3')

bucket_name = "bucketest111"
prefix = ""

objects = list(s3.Bucket(bucket_name).objects.filter(Prefix=prefix))
objects.sort(key=lambda o: o.last_modified)

lastModified = objects[-1].key
secLastModified = objects[-2].key

print(lastModified)
print(secLastModified)
if 'pdf' in lastModified:
    jobId = Multi.startJob(2,bucket_name,lastModified)
    if (Multi.isJobComplete(2,jobId)):
        response = Multi.getJobResults(2,jobId)
        doc = Multi.Document(response)
        Multi.lines(lastModified,doc)
else:
    ID.analyze_id(bucket_name,lastModified)

print("//////////////////////////////////////")

if 'pdf' in secLastModified:
    jobId = Multi.startJob(2,bucket_name,secLastModified)
    if (Multi.isJobComplete(2,jobId)):
        response = Multi.getJobResults(2,jobId)
        doc = Multi.Document(response)
        Multi.lines(secLastModified,doc)
else:
    ID.analyze_id(bucket_name,secLastModified)    