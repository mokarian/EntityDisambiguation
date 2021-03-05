"""
This file contains methods that may frequently being used in this project
"""
import json
import os
import csv
from itertools import chain, combinations

import yaml
import pandas as pd


class Utils:
    """
    This class contains methods that may frequently being used in this project
    """

    def __init__(self, resources_path):
        self.resources_path = resources_path

    def get_shortest_fields_with_highest_f1_score(self, a_list):
        """
        This method finds a field with highest f1 score having the shortest length.
        Example:
        :param a_list:
        [{"f1":91, "fields":"foo.bar"},
        {"f1":91, "fields":"foo"}
        {"f1":90, "fields":"f"}]
        :return: foo -> which has the shortest length with f1 score 91
        """
        sorted_on_f1 = self.sort_on_f1_score(a_list)
        if not sorted_on_f1:
            return ""
        sublist = self.get_sublist_of_fields_having_same_value(sorted_on_f1,
                                                               'f1',
                                                               sorted_on_f1[0]['f1'])
        sorted_on_fields = self.sort_on_fields_length(sublist)
        return sorted_on_fields[0]['fields']

    def generate_reports(self, data, file_name):
        """
        This method stores data as CSV file in generated directory
        :param data:
        :param file_name:
        :return:
        """
        generated = "generated"
        self.make_directory_if_not_exists(generated)
        data_frame = pd.DataFrame(data)
        filename = os.path.join(generated, file_name + '.csv')
        data_frame.to_csv(filename)

    def write_json_to_directory(self, json_object, file_name, directory="resources"):
        """
        This method writes a python object to a json file
        """
        self.make_directory_if_not_exists(directory)
        filename = os.path.join(directory, file_name + '.json')
        with open(filename, 'w') as outfile:
            json.dump(json_object, outfile)

    def read_json_from_resources(self, filename):
        """
        This method loads a json from a file
        :param filename:
        :return: a json file
        """
        full_path = os.path.join(self.resources_path, filename)
        resources = {}
        if full_path:
            with open(full_path, 'r') as file:
                resources = json.load(file)
        return resources

    def read_csv(self, filename="names.csv"):
        """
        This method reads a CSV file to a list
        :param filename:
        :return: a list containing elements per line of CSV
        """
        filename = os.path.join(self.resources_path, filename)
        with open(filename, 'r') as a_file:
            return list(csv.reader(a_file))

    def get_config(self):
        """
        this method loads a YAML config file in a dictionary
        :return: dictionary of configuration file
        """
        yaml_path = os.path.join(self.resources_path, "config.yml")
        with open(yaml_path, 'r') as configuration:
            return yaml.load(configuration, Loader=yaml.FullLoader)

    @staticmethod
    def create_elastic_search_body(query, fields):
        """
        this method receives  a query and an array of fields,
        then it generates a request body to be sent to the Elastic Search
        :param query:
        :param fields:
        :return: src body
        """
        return {
            "query": {
                "multi_match": {
                    "query": "" + query + "",
                    "fields": fields,
                    "type": "most_fields"
                }
            }
        }

    @staticmethod
    def create_azure_search_body(query, fields):
        """
        this method receives  a query and an array of fields,
        then it generates a request body to be sent to the Elastic Search
        :param query:
        :param fields:
        :return: src body
        """
        searchFields = ",".join(fields)
        return {
            "queryType": "full",
            "search": query,
            "searchFields": searchFields
        }

    @staticmethod
    def get_maximum_rank_from_elastic_search_response(response):
        """
        this method receives a response and returns the maximum ranked hits.
        it will return NOT_FOUND if response has not hits
        :param response:
        :return: a username with the maximum rank or NOT_FOUND otherwise
        """
        score = 0
        found_name = "NOT_FOUND"
        for hit in response:
            if hit.meta.score > score:
                score = hit.meta.score
                found_name = hit.name[0]
        return found_name

    @staticmethod
    def get_maximum_rank_from_azure_search_response(response):
        """
        this method receives a response and returns the maximum ranked hits.
        it will return NOT_FOUND if response has not hits
        :param response:
        :return: a username with the maximum rank or NOT_FOUND otherwise
        """
        score = 0
        found_name = "NOT_FOUND"
        for hit in response['value']:
            if hit['@search.score'] > score:
                score = hit['@search.score']
                found_name = hit['standard_lucene']
        return found_name

    @staticmethod
    def get_subsets(iterable):
        """
        This method is to create a full subset of the elements of an iterable parameter
        :param iterable:
        :return:
        """
        list_of_set = list(iterable)
        return list(chain.from_iterable(combinations(list_of_set, r)
                                        for r in range(1, len(list_of_set) + 1)))

    @staticmethod
    def sort_on_f1_score(a_list, descending=True):
        """
        this method will sort a list on f1 score fields in Descending order
        :param a_list:
        :return: a sorted list
        """
        return sorted(a_list, key=lambda i: (i['f1']), reverse=descending)

    @staticmethod
    def sort_on_fields_length(a_list):
        """
        This method will sort the list on fields in ascending order
        Example:
        :param a_list:
        [{"fields":"this_is_longest_field", "baz="bar"},
        {"fields":"longer_field", "baz="bar"},
        {"fields":"short", "baz="bar"}]
        :return:
         [{"fields":"short", "baz="bar"},
        {"fields":"longer_field", "baz="bar"},
        {"fields":"this_is_longest_field", "baz="bar"}]
        """
        return sorted(a_list, key=lambda i: (len(i['fields'])))

    @staticmethod
    def get_sublist_of_fields_having_same_value(a_list, field, value):
        """
        this method returns a sublist from a list having equal values
        Example:
        :param a_list:  [{"foo":11, "baz="bar"},{"foo":11, "baz="bar"}, {"foo":12, "baz="bar"}]
        :param field: foo
        :param value:  11
        :return: [{"foo":11, "baz="bar"},{"foo":11, "baz="bar"}]
        """
        return [item for item in a_list if item[field] == value]

    @staticmethod
    def make_directory_if_not_exists(directory):
        """
        this method creates a directory if it does not exists
        :param directory:
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
