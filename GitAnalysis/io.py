from git_hub_issue_commits import GitHubIssueCommits
import csv
import json
import os


class NoFileExtensionException(Exception):
    def __init__(self, file_address):
        super(NoFileExtensionException, self).__init__('Please provide extension for following file: (' +
                                                       file_address + ')')


class IO:
    def __init__(self):
        pass

    @staticmethod
    def read_issue_commits(file_address, file_extension=None, tuple_keep_filter_attribute=None, keep=True,
                           ignore_field_without_value=True):
        # type: (str, str) -> IGitHubFixCommit
        """
        :param: file_address
        :param: file_extension can be txt or csv or json
        :param: tuple_keep_filter_attribute  tuple filed value and condition for keep or filter issue
        :param: keep if it is true keep with the condition otherwise filter  the issue
        """

        def invert_condition(condition, invert):
            if invert:
                return condition
            else:
                return not condition

        if not file_extension:
            file_extension = file_address.split('.').pop().lower()
            if file_extension not in ['txt', 'csv', 'json']:
                raise NoFileExtensionException(file_address=file_address)

        def utf8_encode(to_encode):
            if type(to_encode) is list:
                return map(lambda t: t.encode('utf8'), to_encode)
            elif type(to_encode) is unicode:
                to_encode = to_encode.encode('utf8')
                return to_encode
            else:
                return to_encode

        with open(file_address) as file_handler:
            if file_extension == 'txt':
                # Ignore first line (first line is header)
                file_handler.readline()
                for line in file_handler:
                    split_line = line.split(',')
                    # skip if the filter attribute is not matched(check if the value is not inside the dictionary)
                    if tuple_keep_filter_attribute and \
                            invert_condition((tuple_keep_filter_attribute[1]
                                             not in split_line[int(tuple_keep_filter_attribute[0])]), keep):
                        continue
                    git_hub_issue_commit = GitHubIssueCommits()
                    git_hub_issue_commit.init_from_text(line)
                    yield git_hub_issue_commit
            elif file_extension == 'csv':
                cvs_reader = csv.DictReader(file_handler)
                # print cvs_reader.next()
                for row_dictionary in cvs_reader:
                    # row_dictionary = dict(map(lambda (k, v): (k, unicode(v, 'utf-8')), row_dictionary.iteritems()))
                    # row_dictionary = dict(map(lambda (k, v): (k, v.decode('utf-8')), row_dictionary.iteritems()))
                    # ignore field without value of filter attribute
                    if ignore_field_without_value and tuple_keep_filter_attribute \
                            and tuple_keep_filter_attribute[0] not in row_dictionary:
                        continue
                    # skip if the filter attribute is not matched(check if the value is not inside the dictionary)
                    if tuple_keep_filter_attribute and tuple_keep_filter_attribute[0] in row_dictionary and\
                            invert_condition(tuple_keep_filter_attribute[1]
                                             not in row_dictionary[tuple_keep_filter_attribute[0]], keep):
                        continue
                    git_hub_issue_commit = GitHubIssueCommits()
                    git_hub_issue_commit.init_from_dictionary(row_dictionary)
                    yield git_hub_issue_commit
            elif file_extension == 'json':
                file_handler.readline()
                for json_txt in file_handler:
                    json_line = json.loads(json_txt, encoding='utf8')
                    json_line = {k: utf8_encode(v) for k, v in json_line.items()}
                    # ignore field without value of filter attribute
                    if ignore_field_without_value and tuple_keep_filter_attribute \
                            and tuple_keep_filter_attribute[0] not in json_line:
                        continue
                    # skip if the filter attribute is not matched(check if the value is not inside the dictionary)
                    if tuple_keep_filter_attribute and tuple_keep_filter_attribute[0] in json_line and \
                            invert_condition(tuple_keep_filter_attribute[1]
                                             not in json_line[tuple_keep_filter_attribute[0]], keep):
                        continue
                    git_hub_issue_commit = GitHubIssueCommits()
                    git_hub_issue_commit.init_from_dictionary(json_line)
                    yield git_hub_issue_commit

