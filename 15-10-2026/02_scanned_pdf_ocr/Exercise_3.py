import pymupdf
import pytesseract
from PIL import Image

##1
doc=pymupdf.open("EY_Scanned_PDF_OCR_Practice.pdf")

print("Number of pages: ",len(doc))

##2
# page=doc[0]
# img=page.get_pixmap()
# img.save("scanned_page.png")

##3
image=Image.open("scanned_page.png")
text=pytesseract.image_to_string(image)

##4
print(text)

##5
if "Forklift FL-17" in text:
    print("\'Forklift FL-17\' appears")
else:
    print("\'Forklift FL-17\' does not appear")

##6
if "injuries" in text:
    print("\'injuries\' appears")
else:
    print("\'injuries\' does not appear")

##7
print("Sentences where \'inspection\' appears are:")
for l in text.splitlines():
    if 'inspection' in l:
        print(l)

##8
with open("ocr_result.txt","w") as f:
    f.write(text)

##9
print("Count of the word \'inspection\' : ",text.count('inspection'))

##10
print("Lines containing \'Loading Bay\':")
for l in text.splitlines():
    if 'Loading Bay' in l:
        print(l)