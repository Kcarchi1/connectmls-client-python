from typing import Union
from json.decoder import JSONDecodeError

from requests import Session, Response

from .auth import get_auth_cookies
from .utils import (
    extract_baseurl,
    convert_to_excel,
    convert_to_tsv,
)


class BaseClient:
    def __init__(self, username: str, password: str, connect_timeout: int = 10, read_timeout: int = 10):
        self.timeout_settings = (connect_timeout, read_timeout)
        self.base_url = None

        self.session = Session()

        self.session.cookies = get_auth_cookies(username, password)
        self.session.headers.update({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/119.0.0.0 Safari/537.36",
        })

    def get(self, path: str, json: dict = None, raw_response: bool = True) -> Union[Response, dict]:
        response = self.session.get(
            url=self.base_url + path, json=json, timeout=self.timeout_settings
        )

        if raw_response:
            return response

        return self.to_json(response)

    def post(self, path: str, json: dict = None, data: str = None, raw_response: bool = True) -> Union[Response, dict]:
        response = self.session.post(
            url=self.base_url + path, json=json, data=data, timeout=self.timeout_settings
         )

        if raw_response:
            return response

        return self.to_json(response)

    def to_json(self, response) -> dict:
        if isinstance(response, dict):
            return response
        else:
            try:
                return response.json()
            except JSONDecodeError as e:
                return vars(e)


class Client(BaseClient):
    def __init__(self, username: str, password: str, connect_timeout: int = 10, read_timeout: int = 10):
        super().__init__(username, password, connect_timeout, read_timeout)

        self.base_url = "https://" + extract_baseurl(self.session.cookies.list_domains())

    def get_listings_ids(self, property_payload: dict, raw_response: bool = False) -> Union[Response, dict]:
        """
        Retrieve available listing IDs that correspond to parameters specified in the payload.

        :param property_payload: Contains the property type and parameters that listings should match.
        :param raw_response: Indicates whether a 'Response' object should be returned. Can be utilized to check
                             the status code or headers of the response. Defaults to False which returns the decoded
                             JSON dictionary.
        :return: A decoded JSON dictionary by default, containing listing IDs. To get the underlying 'Response' object,
                 set "raw_response = True".
        """

        endpoint = "/api/search/listing/download"
        response = self.post(path=endpoint, json=property_payload)

        if raw_response:
            return response

        return self.to_json(response)

    def download(self, export_payload: dict, receive_bytes: bool = False) -> Union[bytes, None]:
        """
        Download listings to the system based on the file format specified in the payload.

        :param export_payload: Contains listings IDs and criteria dictating how the server
                               should generate the export file.
        :param receive_bytes: Indicates whether a 'Bytes' object should be returned. Can be used to convert the bytes
                              to a data structure of choice, such as a Pandas DataFrame (refer to the documentation for
                              examples). Defaults to False which downloads the listings to the system based on the
                              file format specified in "export_payload".
        :return: None by default. Saves listings to the system. To get the underlying 'Bytes' object, set
                 "receive_bytes = True".
        """

        response = self.get_file_info(export_payload)
        download_bytes = self.get(path=response["url"]).content

        if receive_bytes:
            return download_bytes

        export_type = export_payload["type"].upper()

        if export_type == "XLS":
            convert_to_excel(response["filename"], download_bytes)
        elif export_type == "TSV":
            convert_to_tsv(response["filename"], download_bytes)

        return None

    def get_file_info(self, export_payload: dict, raw_response: bool = False) -> Union[Response, dict]:
        """
        Get the name and location of the recently created export file.

        :param export_payload: Contains listings IDs and criteria dictating how the server
                               should generate the export file.
        :param raw_response: Indicates whether a 'Response' object should be returned. Can be utilized to check
                             the status code or headers of the response. Defaults to False which returns the decoded
                             JSON dictionary.
        :return: A decoded JSON dictionary by default, containing file info. To get the underlying 'Response' object,
                 set "raw_response = True".
        """

        endpoint = "/api/listing/mylistings/export"
        response = self.post(path=endpoint, json=export_payload)

        if raw_response:
            return response

        return self.to_json(response)

    def get_export_options(self, property_type: str, raw_response: bool = False) -> Union[Response, dict]:
        """
        Get available export options for a given property type.

        :param property_type: Property type to check export options for (example: Attached Single is "AT").
        :param raw_response: Indicates whether a 'Response' object should be returned. Can be utilized to check
                             the status code or headers of the response. Defaults to False which returns the decoded
                             JSON dictionary.
        :return: A decoded JSON dictionary by default, containing export options. To get the underlying 'Response'
                 object, set "raw_response = True".
        """

        endpoint = "/api/listing/mylistings/exportoptions"
        response = self.post(path=endpoint, data=property_type.upper())

        if response.status_code == 500:
            raise TypeError("invalid property type")

        if raw_response:
            return response

        return self.to_json(response)

    def get_table_info(self, property_type: str, table_name: str) -> Union[dict, None]:
        """
        Get the unique table ID of a default or custom table.

        :param property_type: Property type to check a table for (example: Attached Single is "AT").
        :param table_name: Name of the table to search for.
        :return: A decoded JSON dictionary containing the table ID. If no table matching the name is found, None
                 is returned.
        """

        response = self.get_export_options(property_type)
        table_list = response['reports']['options']
        return next((table for table in table_list if table['label'] == table_name), None)

    def create_custom_table(self, table_payload: dict, raw_response: bool = False) -> Union[Response, dict]:
        """
        Create and save a custom table to your profile.

        :param table_payload: Contains information on what columns your custom table should be
                              made up of.
        :param raw_response: Indicates whether a 'Response' object should be returned. Can be utilized to check
                             the status code or headers of the response. Defaults to False which returns the decoded
                             JSON dictionary.
        :return: A decoded JSON dictionary containing information on the new table. To get the underlying 'Response'
                 object, set "raw_response = True".
        """

        endpoint = "/api/reports/custom/save"
        response = self.post(path=endpoint, json=table_payload)

        if raw_response:
            return response

        return self.to_json(response)

    def clippy_test(self, raw_response: bool = False) -> Union[Response, dict]:
        """
        A quick and easy way to check for authorization. If your credentials have been successfully authenticated,
        a current API version number will be returned.

        :param raw_response: Indicates whether a 'Response' object should be returned. Can be utilized to check
                             the status code or headers of the response. Defaults to False which returns the decoded
                             JSON dictionary.
        :return: A decoded JSON dictionary by default, containing an API version number. To get the underlying
                 'Response' object, set "raw_response = True".
        """

        endpoint = "/api/clippy/version"
        response = self.get(path=endpoint)

        if raw_response:
            return response

        return self.to_json(response)

    def get_listing_details(
            self,
            property_type: str,
            listing_id: str,
            raw_response: bool = False
    ) -> Union[Response, dict]:

        endpoint = f"/api/search/listing/details/data/LISTING/{property_type}/{listing_id}"
        response = self.get(path=endpoint)

        if raw_response:
            return response

        return self.to_json(response)

    def get_listing_count(
            self,
            property_payload: dict,
            focus_count: bool = False,
            raw_response: bool = False
    ) -> Union[Response, dict]:

        endpoint = "/api/search/listing/count"
        response = self.get(path=endpoint, json=property_payload)

        if raw_response:
            return response

        if focus_count:
            d = self.to_json(response)
            return {"count": d["count"]}

        return self.to_json(response)