import boto3
import time
import csv
from trp import Document

def startJob(typeOp, s3BucketName, documentName):
    response = None
    client = boto3.client('textract')

    if typeOp == 1:
        response = client.start_document_text_detection(
            DocumentLocation={
                'S3Object': {
                    'Bucket': s3BucketName,
                    'Name': documentName
                }
            }
        )
    else: 
        response = client.start_document_analysis(
            DocumentLocation={
                'S3Object': {
                    'Bucket': s3BucketName,
                    'Name': documentName
                }
            }, FeatureTypes=["FORMS", "TABLES"])
    
    return response["JobId"]

def isJobComplete(typeOp, jobId):
    time.sleep(5)
    
    client = boto3.client("textract")

    if typeOp == 1:
        response = client.get_document_text_detection(JobId=jobId)
    else: 
        response = client.get_document_analysis(JobId=jobId)

    status= response["JobStatus"]
    print ("Job Status: {}".format(status))

    while(status == "IN_PROGRESS"):
        time.sleep(5)
        
        if typeOp == 1:
            response = client.get_document_text_detection(JobId=jobId)
        else: 
            response = client.get_document_analysis(JobId=jobId)
    
        status= response["JobStatus"]
        print ("Job Status: {}".format(status))

    return status

def getJobResults(typeOp,jobId):
    pages = []
    
    time.sleep(5)
    
    client = boto3.client('textract')
    
    if typeOp == 1:
        response = client.get_document_text_detection(JobId=jobId)
    else: 
        response = client.get_document_analysis(JobId=jobId)
    pages.append(response)
    print("Result set page received: {}".format(len(pages)))
    nextToken= None
    if ('NextToken' in response):
        nextToken = response['NextToken']

    while (nextToken):
        time.sleep(5)

        if typeOp == 1:
            response = client.get_document_text_detection(JobId=jobId, NextToken=nextToken)
        else: 
            response = client.get_document_analysis(JobId=jobId, NextToken=nextToken)
    
        pages.append(response)
        print("Result set page received: {}".format(len(pages)))
        nextToken= None
        if ('NextToken' in response):
            nextToken = response['NextToken']
    
    return pages


def lines (documentName,doc):
    cont = int(0)
    Domicilio = ''
    Nombre = ''
    f = open(documentName + "-lines.txt","w+")
    print("Lines\n==============")
    for page in doc.pages:
        for line in page.lines:
            cont += 1
            if cont == 7:
                Nombre = ("{}".format(line.text))
            elif cont == 9 or cont == 11 or cont == 12 or cont == 14:
                Domicilio += ("{} ".format(line.text))
    print("Nombre: {}".format(Nombre))
    print("Domicilio: {}".format(Domicilio))
    f.write("{}--{}".format(Nombre,Domicilio)+"\n")    
    f.close
            

def forms(documentName,doc):
    f = open(documentName + "-fields.txt","w+")
    print("Forms\n==============")
    for page in doc.pages:
        for field in page.form.fields:
            kv = "Key: {}, value: {}".format(field.key,field.value)
            f.write(kv + "\n")
            print(kv)
    f.close

def tables(documentName,doc):
    print("Tables\n==============")
    for p, page in enumerate(doc.pages):
        for t, table in enumerate(page.tables):
            f = open(documentName + "-table-"+"str(p)"+"-"+str(t)+".csv","w+") 
            w= csv.writer(f,escapechar='\\',lineterminator='\n')           
            for r, row in enumerate(table.rows):
                rw=[]
                for c, cell in enumerate(row.cells):
                    print("Table[{}][{}] = {}".format(r,c,cell.text)) 
                    rw.append(cell.text)
                w.writerow(rw)
            f.close()


typeOp = 2
s3BucketName = ""
documentName = ""

#jobId = startJob(typeOp,s3BucketName,documentName)
#print("Started job with ID: {}".format(jobId))

#if (isJobComplete(typeOp,jobId)):
#    response = getJobResults(typeOp,jobId)

#    doc = Document(response)

#    lines(documentName,doc)
    #forms(documentName,doc)
    #tables(documentName,doc)

