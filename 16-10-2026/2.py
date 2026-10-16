from pydantic import BaseModel,ValidationError,Field
import logging



class Registration(BaseModel):
    registration_id: str
    name: str
    email: str
    age: int = Field(ge=18)
    ticket_type: str = Field(pattern="^(Standard|Premium|VIP)$")
    amount: int = Field(gt=0)

import json
try:
    with open("registrations.json") as f:
        data=json.load(f)
except FileNotFoundError:
    logging.error("The file \'registrations.json\' does not exist")
    data=[]
except json.decoder.JSONDecodeError:
    logging.error("Invalid JSON Format")
    data=[]

# print(data)


valid_reg=[]

for item in data:
    try:
        reg=Registration(**item)
        print("Valid registration: ",reg)
        valid_reg.append(reg)
        print("-----------------------------------------")
    except ValidationError as e:
        reg_id=item.get("registration_id","UnknownID")
        for it in e.errors():
            field=it["loc"]
            message=it["msg"]

            print("Registration ID: ",reg_id)
            print("Field with error: ",field[0])
            print("Error Message: ",message)

            print("-----------------------------------------------------------")

print("VALID REGISTRATIONS ARE: ")
for item in valid_reg:
    print(item)
print("---------------------------------------------------------")

print("One valid registration into dictionary: ")
reg_dict=valid_reg[0].model_dump()
print(reg_dict)
print("----------------------------------------------------------")
print("One valid registration into json: ")
reg_json=valid_reg[0].model_dump_json()
print(reg_json)
print("---------------------------------------------------------")
jsonfiles=[]
for it in valid_reg:
    jsonfiles.append(it.model_dump())

with open("valid_registrations.json","w") as f:
    json.dump(jsonfiles,f)




logging.basicConfig(
    level=logging.INFO,format='%(levelname)s - %(message)s',filename="registrations.log"
)

for item in data:
    try:
        reg=Registration(**item)
        logging.info(f"Registration data {reg.registration_id} validated successfully")
        if reg.ticket_type=="VIP":
            logging.warning(f"Registration {reg.registration_id} ticket type is \'VIP\'")

    except ValidationError as e:
        reg_id=item.get("registration_id","UnknownID")
        for it in e.errors():
            field=it["loc"]
            message=it["msg"]
            logging.error(f"Registration {reg_id}: {field[0]} , {message}")

print("Total records : ",len(data))
print("Valid records : ",len(valid_reg))
print("Invalid records : ",len(data)-len(valid_reg))

print("-----------------------------------------------------------")

