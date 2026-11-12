from pypdf import PdfReader

##1
reader = PdfReader("EY_Digital_PDF_Practice.pdf")

##2
print("Pages:", len(reader.pages))
# for page in reader.pages:
#     print(page.extract_text())

##3
print("Page-1 content:")
print(reader.pages[0].extract_text())

##4
print("Page-2 content:")
print(reader.pages[1].extract_text())

##5
page12combined=""
page12combined=reader.pages[0].extract_text()+reader.pages[1].extract_text()
print("Content of page-1 & page-2: ")
print(page12combined)

##6
totalcontent=""
for page in reader.pages:
    totalcontent=totalcontent+page.extract_text()
if "NorthStar Maintenance" in totalcontent:
    print("\'NorthStar Maintenance\' exists in the document")
else:
    print("\'NorthStar Maintenance\' does not exist in the document")

##7
print("Count of the word \'vendor\' in the document: ",totalcontent.count('vendor'))

##8
with open("pypdf_output.txt","w") as f:
    f.write(totalcontent)