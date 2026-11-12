import pymupdf

##1
doc = pymupdf.open("EY_Digital_PDF_Practice.pdf")

##2
print("Pages:", len(doc))

##3
print("Content of Page-1: ")
print(doc[0].get_text())

##4
print("Content of whole document: ")
wholedoc=""

for page in doc:
    wholedoc=wholedoc+page.get_text()
print(wholedoc)

##5
if "maintenance" in wholedoc.lower():
    print("Maintenance appears in the document")
else:
    print("Maintenance doesnt appear in the document")

##6
print("Count of word \'V303\' is: ",wholedoc.count("V303"))

##7
print("Content of page-2: ")
print(doc[1].get_text())

##8
with open("digital_pdf_text.txt","w") as f:
    f.write(wholedoc)