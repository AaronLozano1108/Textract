import boto3
import json
import Analizecfeimage
from trp import Document
import mysql.connector

client = boto3.client('textract')

cnx = mysql.connector.connect(user='root', password='admin',
                              host='127.0.0.1',
                              database='textract_db')
cursor = cnx.cursor()
sqlID = "INSERT INTO datos_identificacion (Nombre, Domicilio, Tipo_documento) VALUES (%s, %s, %s)"
#sqlRecibo = "INSERT INTO datos_identificacion (Nombre, Domicilio) VALUES (%s, %s)"

def analyze_id(bucket_name, file_name):

    # Analyze document
    # process using S3 object
    Cfe=int(0)
    passp=int(0)
    Ine=int(0)
    Domicilio = ''
    NumPass = ''
    fechaNac = ''
    lugarNac = ''
    curp = ''
    response = client.analyze_id(
        DocumentPages=[{'S3Object': {'Bucket': bucket_name, 'Name': file_name}}])

    for doc_fields in response['IdentityDocuments']:
        for id_field in doc_fields['IdentityDocumentFields']:
            for key, val in id_field.items():
                if "Type" in str(key):
                    print("Type: " + str(val['Text']))
            for key, val in id_field.items():
                if "ValueDetection" in str(key):
                    print("Value Detection: " + str(val['Text']))
                if "UNKNOWN" in str(val['Text']):
                    Cfe=1
                if "PASSPORT" in str(val['Text']):
                    passp=1
                if "DRIVER LICENSE FRONT" in str(val['Text']):
                    Ine=1    
            print()
    x= doc_fields['IdentityDocumentFields']
    Nombre = str("{} {} {}".format(x[0]['ValueDetection']['Text'],x[2]['ValueDetection']['Text'],x[1]['ValueDetection']['Text']))
    fechaNac = str("{} ".format(x[10]['ValueDetection']['Text']))
    print(Nombre)
    if Ine ==1:
        Domicilio = str("{}, {}, {}".format(x[17]['ValueDetection']['Text'],x[4]['ValueDetection']['Text'],x[7]['ValueDetection']['Text']))
        print (Domicilio)
        curp = (analyze(bucket_name,file_name))
        print(curp)
        val = (Nombre, Domicilio, "INE")

    if passp == 1:
        NumPass = str("{} ".format(x[8]['ValueDetection']['Text']))
        fechaNac = str("{} ".format(x[10]['ValueDetection']['Text']))
        lugarNac = str("{} ".format(x[19]['ValueDetection']['Text']))
        val = (Nombre, Domicilio, "Pasaporte")
        print (NumPass)
        print (lugarNac)

    cursor.execute(sqlID, val)
    cnx.commit()
    print(cursor.rowcount, "record inserted.")


    print (fechaNac)
    if Cfe==1:
        Analizecfeimage.s3BucketName=bucket_name
        Analizecfeimage.documentName=file_name
        Analizecfeimage.analyze(bucket_name,file_name)


def lines (doc):
    cont= int(0)
    cont2= int(0)
    varCurp=''
    for page in doc.pages:
        for line in page.lines:
            cont += 1
            if "CURP" in line.text:
                for word in line.words:
                    cont2 += 1
                    if cont2 == 2:
                        varCurp = str("{}".format(word.text))   
    return varCurp

def analyze(bucket_name, file_name):
    response = client.analyze_document(
        Document={
            'S3Object':{
                'Bucket':bucket_name,
                'Name': file_name
            }
        },
        FeatureTypes=["FORMS","TABLES"])
    
    doc=Document(response)
    curp=(lines(doc))
    return curp
    

