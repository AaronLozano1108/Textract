import boto3
from trp import Document

#Document
s3BucketName = ''
documentName = ''

textract = boto3.client('textract')

def lines (doc):
    cont= int(0)
    cont2= int(0)
    varNombre=''
    varDireccion=''
    for page in doc.pages:
        for line in page.lines:
            cont += 1
            if cont == 7:
                varNombre += str("{} ".format(line.text))
            elif cont == 9 or cont == 10 or cont == 12 or cont == 14:
                varDireccion += str("{} ".format(line.text))       
        print("Nombre: {}".format(varNombre))
        print("Domicilio: {}".format(varDireccion))
            #for word in line.words:
                #print("WORD: {}--{}".format(word.text,word.confidence))

def forms(doc):
    for page in doc.pages:
        print("Fields: ")
        for field in page.form.fields:
            print("Key: {}, value: {}".format(field.key,field.value))

def tables(doc):
    for page in doc.pages:
        for table in page.tables:
            for r, row in enumerate(table.rows):
                for c, cell in enumerate(row.cells):
                    print("Table[{}][{}] = {}".format(r,c,cell.text)) 

def analyze(s3BucketName,documentName):
    response = textract.analyze_document(
        Document={
            'S3Object':{
                'Bucket':s3BucketName,
                'Name': documentName
            }
        },
        FeatureTypes=["FORMS","TABLES"])
    
    doc=Document(response)
    lines(doc)
    #forms(doc)
    #tables(doc)       

def detect():
    response = textract.detect_document_text (
        Document={
            'S3Object':{
                'Bucket':s3BucketName,
                'Name': documentName
            }
        }
    )

    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            print(item["Text"])

#detect()
#analyze()