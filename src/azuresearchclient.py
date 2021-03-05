"""
This file contains methods to communicate with azure src
"""
import os
import uuid

import requests
from src.utils import Utils


class AzureSearchClient:
    """
    This class contains methods to communicate with azure src
    """

    def __init__(self):
        self.utils = Utils(os.path.join("../resources"))
        self.config = self.utils.get_config()
        self.endpoint = 'https://{}.search.windows.net/'.format(self.config["search"]["service_name"])
        self.api_version = '?api-version=2020-06-30'
        self.headers = {'Content-Type': 'application/json',
                        'api-key': '{}'.format(self.config["search"]["api_key"])}

    def insert_documents(self, index_name="test"):
        """
        Thsi method is to insert document into an index in azure src
        :param index_name:
        """
        url = self.endpoint + "indexes/" + index_name + "/docs/index" + self.api_version
        response = requests.post(url, headers=self.headers, json=self.create_documents_payload())
        return response.json()

    def create_index(self, index_name="test"):
        """
        this method is to create an index in azure src using a schema file (resources/index-schema.json)
        :param index_name:
        :return: response of the generated index schema
        """
        url = self.endpoint + "/indexes/" + index_name + self.api_version
        body = self.utils.read_json_from_resources("index-schema.json")
        body["name"] = index_name
        response = requests.put(url, headers=self.headers,
                                json=body)
        return response.json()

    def make_search(self, misspelled_name, fields, index_name="test"):
        """
        this method queries the azure src index
        :param index_name:
        :param fields:
        :param misspelled_name:
        :query  the query
        """
        url = self.endpoint + "/indexes/" + index_name + "/docs/search" + self.api_version
        body = self.utils.create_azure_search_body(misspelled_name, fields)
        body["name"] = index_name
        azure_response = requests.post(url, headers=self.headers,
                                       json=body)
        return self.utils.get_maximum_rank_from_azure_search_response(azure_response.json())

    def create_documents_payload(self):
        """
        This method is to create documents payload for the azure src from tokens.csv file
        :return: a payload to insert documents into azure src
        """
        documents = []
        tokens = self.utils.read_csv("names.csv")
        for token in tokens:
            documents.append({
                "@src.action": "upload",
                "id": str(uuid.uuid4()),
                "standard_lucene": token[0],
                "phonetic": token[0],
                "edge_n_gram": token[0],
                "keyword": token[0],
                "letter": token[0],
                "ngram": token[0],
                "camelcase": token[0],
                "email": token[0],
                "stemming": token[0],
                "url_email": token[0],
                "text_microsoft": token[0]

            })

        return {"value": documents}