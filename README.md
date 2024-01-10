# connectMLS Client Python

Welcome to the unofficial Python client module for the [MRED connectMLS](https://store.mredllc.com/products/1000) API. The end goal is to ultimately turn this module into a python package, but for now, feel free to fork this repository and use it or build upon it as it undergoes development.

## Creating Client
Import the Client.
```python
from connectmlsconnector.client import Client
```
Create a new client with your credentials
```python
client = Client(username="your_username, password="your_password")
```
### Example Usage
Request listing IDs
```python
# Fill payload with search parameters
payload = {
  "searchtype": "LISTING",
  "searchclass": "RN",
  "boundaries": None,
  "fields": [
    {
      "ordinal": None,
      "id": "ST",
      "value": "ACTV,AUCT,BOMK,NEW",
      "option": "",
      "min": "",
      "max": "",
      "none": None,
      "all": None
    },
    {
      "ordinal": None,
      "id": "MONTHS_BACK",
      "value": "9",
      "option": None,
      "min": None,
      "max": None,
      "none": None,
      "all": None
    },
    {
      "ordinal": None,
      "id": "ZP",
      "value": "60611",
      "option": "",
      "min": "",
      "max": "",
      "none": None,
      "all": None
    },
  ],
  "layers": [],
  "sort": [
    {
      "field": "RENTAL_PRICE",
      "direction": 1,
      "mark": False
    }
  ],
  "record": True
}

listing_ids = client.search(property_payload=payload)
print(listing_ids)
```
