from GitAnalysis.commit import GitDiffEmptyException, NoParentsCommitException
from GitAnalysis import IO
from GitAnalysis import CommitSpec

import time
import os
import csv
import json

import git
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


class GitAnalysis:
    def __init__(self, repository_address, retrieve_other_commit_id_from_issue_tracker,
                 consider_issues_without_labels_as_other=True,
                 tuple_keep_attribute=None, write_mode='wb', log_flag=False):
        """
        :param repository_address: repository file address
        """
        self.repository = git.Repo(repository_address)
        self.retrieve_other_commit_id_from_issue_tracker = retrieve_other_commit_id_from_issue_tracker
        self.consider_issues_without_labels_as_other = consider_issues_without_labels_as_other
        self.tuple_keep_attribute = tuple_keep_attribute
        self.write_mode = write_mode
        self.log_flag = log_flag

    def log(self, log_str):
        if self.log_flag:
            print(log_str)
            print '*******************************************************'

    # Start parquet writer
    def parquet_writer(self, result_file_address, data_generator, compression='gzip'):
        index = 0

        try:
            dic_data = next(data_generator)
            df = pd.DataFrame(dic_data, [index])
            table = pa.Table.from_pandas(df)
            with pq.ParquetWriter(result_file_address, table.schema, compression=compression) as writer:
                writer.write_table(table)
                for dic_data in data_generator:
                    index += 1
                    df = pd.DataFrame(dic_data, [index])
                    table = pa.Table.from_pandas(df)
                    writer.write_table(table=table)
        except StopIteration:
            pass
        finally:
            del data_generator
            self.log("Finished writing on the parquet file")

    def csv_writer(self, result_file_address, data_generator):

        try:
            with open(result_file_address, self.write_mode) as csv_file:
                dic_data = next(data_generator)
                writer = csv.DictWriter(csv_file, dic_data.keys())
                writer.writeheader()
                writer.writerow(dic_data)
                for dic_data in data_generator:
                    writer.writerow(dic_data)
        except StopIteration:
            pass
        finally:
            del data_generator
            self.log("Finished writing on the csv file")

    def choose_writing_format(self, result_file_address, data_generator, file_format):
        if file_format == 'parquet':
            self.parquet_writer(result_file_address=result_file_address, data_generator=data_generator,
                                compression='gzip')
        elif file_format == 'csv':
            self.csv_writer(result_file_address=result_file_address, data_generator=data_generator)
        else:
            self.log('Writing format is not supported, you can only use either of parquet or csv')

    # Start Commit Iterator
    def iter_fix_commits(self, fix_commits_file_address):
        # def iterator(file_address):
        #     for git_hub_fix_commit in IO.read_fix_commit(file_address):
        #         fix_issue_commit_id = git_hub_fix_commit.issue_commit_id.strip()
        #         if fix_issue_commit_id:
        #             commit = self.repository.commit(fix_issue_commit_id)
        #             yield commit

        def iterator(file_address, tuple_keep_attribute):
            set_of_fix_commits = set()
            for git_hub_fix_commit in IO.read_issue_commits(file_address,
                                                            tuple_keep_filter_attribute=tuple_keep_attribute,
                                                            keep=True, ignore_field_without_value=True):
                issue_fix_commit_ids = git_hub_fix_commit.get_fix_commits()
                map(set_of_fix_commits.add, issue_fix_commit_ids)

            for commit_id in set_of_fix_commits:
                commit = self.repository.commit(commit_id)
                yield commit

        return iterator(fix_commits_file_address, self.tuple_keep_attribute)

    def iter_commit_except_fix(self, fix_commits_file_address):
        iter_fix_commits = self.iter_fix_commits(fix_commits_file_address=fix_commits_file_address)
        list_fix_commit_sha = []
        for fix_commit in iter_fix_commits:
            list_fix_commit_sha.append(fix_commit.hexsha)

        def iterator(retrieve_other_commit_id_from_issue_tracker, tuple_keep_attribute,
                     consider_issues_without_labels_as_other):
            if retrieve_other_commit_id_from_issue_tracker:
                set_of_other_commits = set()
                for git_hub_commit in IO.read_issue_commits(file_address=fix_commits_file_address,
                                                            tuple_keep_filter_attribute=tuple_keep_attribute,
                                                            keep=False,
                                                            ignore_field_without_value=
                                                            not consider_issues_without_labels_as_other):
                    issue_commit_ids = git_hub_commit.get_fix_commits()
                    map(set_of_other_commits.add, issue_commit_ids)

                for commit_id in set_of_other_commits:
                    commit = self.repository.commit(commit_id)
                    yield commit
            else:
                for commit in self.repository.iter_commits():
                    if commit.hexsha not in list_fix_commit_sha:
                        yield commit
                    yield commit

        return iterator(self.retrieve_other_commit_id_from_issue_tracker, self.tuple_keep_attribute,
                        self.consider_issues_without_labels_as_other)

    # End Commit Iterator

    # Start Content Analysis

    def content_analysis_all_commits(self, result_file_address, analyze_part='deleted', file_format='parquet'):
        content_generator = self.content_analysis_generator(iter_commit=self.repository.iter_commits(),
                                                            analyze_part=analyze_part)
        self.choose_writing_format(result_file_address=result_file_address, data_generator=content_generator,
                                   file_format=file_format)

    def content_analysis_fix_commits(self, result_file_address, fix_commits_file_address, analyze_part='deleted',
                                     file_format='parquet'):
        content_generator = self.content_analysis_generator(iter_commit=self.iter_fix_commits(
            fix_commits_file_address=fix_commits_file_address), analyze_part=analyze_part)
        self.choose_writing_format(result_file_address=result_file_address, data_generator=content_generator,
                                   file_format=file_format)

    def content_analysis_all_commits_except_fix_commits(self, result_file_address, fix_commits_file_address,
                                                        analyze_part='deleted', file_format='parquet'):
        content_generator = self.content_analysis_generator(iter_commit=self.iter_commit_except_fix(
            fix_commits_file_address=fix_commits_file_address), analyze_part=analyze_part)

        self.choose_writing_format(result_file_address=result_file_address, data_generator=content_generator,
                                   file_format=file_format)

    def content_analysis_generator(self, iter_commit, analyze_part='deleted'):
        field_names = ['line_number', 'hex_hash', 'lexer_name', 'code_line_number', 'file_name', 'token_content',
                       'token_type', 'line_content', 'number_of_tokens', 'number_of_changes']
        line_number, hex_hash, lexer_name, cod_line_number, file_name, token_content, token_type, \
            line_content, number_of_tokens, number_of_changes = field_names
        line_counter = 0

        for commit in iter_commit:
            commit_spec = CommitSpec(commit)
            commit_hex_sha = commit_spec.commit_hex_sha
            try:
                line_tokens_list, number_of_changes_value = commit_spec.content_analyzer(analyze_part=analyze_part)
            except GitDiffEmptyException as err:
                print err
                continue
            except NoParentsCommitException as err:
                print err
                continue

            for tokens_contents in line_tokens_list:

                cod_line_number_value, line_content_value, tokens, file_name_value, lexer_name_value = \
                    tokens_contents
                number_of_tokens_value = len(tokens)
                for token in tokens:
                    line_counter += 1
                    dictionary_data = {
                        line_number: line_counter,
                        hex_hash: commit_hex_sha,
                        lexer_name: lexer_name_value,
                        cod_line_number: str(cod_line_number_value),
                        file_name: file_name_value,
                        token_content: token[2].encode('utf-8'),
                        token_type: str(token[1]),

                        line_content: line_content_value.encode('utf-8'),
                        number_of_tokens: str(number_of_tokens_value),
                        number_of_changes: str(number_of_changes_value)
                    }
                    self.log(dictionary_data)
                    yield dictionary_data

    # End Content Analysis

    ################
    # Time analyze
    ################

    # Start Time Analysis Deleted Lines

    def iter_blame_detail_deleted_lines_fix_commits(self, iter_commits):
        def iterator():
            for fix_commit in iter_commits:
                commit_spec = CommitSpec(fix_commit)
                self.log(fix_commit)
                try:
                    blame_details_list = commit_spec.blame_content()
                except GitDiffEmptyException as err:
                    print err
                    continue
                except NoParentsCommitException as err:
                    print err
                    continue

                for blame_detail in blame_details_list:
                    yield blame_detail

        return iterator()

    def time_analysis_deleted_lines_all_commits(self, result_file_address, file_format='parquet'):
        time_analysis_generator = \
            self.time_analysis_deleted_lines_generator(iter_blame_detail=
                                                       self.iter_blame_detail_deleted_lines_fix_commits(
                                                           self.repository.iter_commits()))
        self.choose_writing_format(result_file_address=result_file_address, data_generator=time_analysis_generator,
                                   file_format=file_format)

    def time_analysis_deleted_lines_all_commit_except_fix_commits(self, result_file_address, fix_commits_file_address,
                                                                  file_format='parquet'):
        time_analysis_generator = \
            self.time_analysis_deleted_lines_generator(iter_blame_detail=
                                                       self.iter_blame_detail_deleted_lines_fix_commits(
                                                           self.iter_commit_except_fix(
                                                               fix_commits_file_address=
                                                               fix_commits_file_address)))
        self.choose_writing_format(result_file_address=result_file_address, data_generator=time_analysis_generator,
                                   file_format=file_format)

    def time_analysis_deleted_lines_fix_commits(self, result_file_address, fix_commits_file_address,
                                                file_format='parquet'):
        time_analysis_generator = \
            self.time_analysis_deleted_lines_generator(iter_blame_detail=
                                                       self.iter_blame_detail_deleted_lines_fix_commits(
                                                           self.iter_fix_commits(fix_commits_file_address=
                                                                                 fix_commits_file_address)))
        self.choose_writing_format(result_file_address=result_file_address, data_generator=time_analysis_generator,
                                   file_format=file_format)

    def time_analysis_deleted_lines_generator(self, iter_blame_detail):
        field_names = ['line_number', 'author', 'author_email', 'authored_date', 'authored_time_zone_offset',
                       'number_of_related_deleted_lines', 'total_deleted_lines', 'total_added_lines']
        line_number, author, author_email, authored_date, author_tz_offset, number_of_related_deleted_lines, \
            total_deleted_lines, total_added_lines = field_names
        line_counter = 0
        for blame_detail in iter_blame_detail:
            line_counter += 1
            commit = blame_detail.blame_commit
            dictionary_data = {
                line_number: line_counter,
                author: commit.author.name.encode('utf-8'),
                author_email: commit.author.email.encode('utf-8'),
                authored_date: time.asctime(time.gmtime(commit.authored_date)),
                author_tz_offset: str(time.gmtime(commit.author_tz_offset).tm_hour) + ':' +
                str(time.gmtime(commit.author_tz_offset).tm_min),
                number_of_related_deleted_lines: str(blame_detail.number_of_related_lines),
                total_deleted_lines: str(blame_detail.total_number_deleted),
                total_added_lines: str(blame_detail.total_number_added)}
            self.log(dictionary_data)
            yield dictionary_data

    # End Time Analysis Deleted Lines

    # Start Time Analysis Commits

    def time_analysis_all_commits_except_fix_commits(self, result_file_address, fix_commits_file_address,
                                                     file_format='parquet'):
        time_analysis_generator = \
            self.time_analysis_generator(self.iter_commit_except_fix(fix_commits_file_address))
        self.choose_writing_format(result_file_address=result_file_address, data_generator=time_analysis_generator,
                                   file_format=file_format)

    def time_analysis_all_commits(self, result_file_address, file_format='parquet'):
        time_analysis_generator = \
            self.time_analysis_generator(self.repository.iter_commits())
        self.choose_writing_format(result_file_address=result_file_address, data_generator=time_analysis_generator,
                                   file_format=file_format)

    def time_analysis_fix_commits(self, result_file_address, fix_commits_file_address, file_format='parquet'):
        time_analysis_generator = \
            self.time_analysis_generator(self.iter_fix_commits(fix_commits_file_address))
        self.choose_writing_format(result_file_address=result_file_address, data_generator=time_analysis_generator,
                                   file_format=file_format)

    def time_analysis_generator(self, iter_commits):
        field_names = ['line_number', 'author', 'author_email', 'authored_date', 'authored_time_zone_offset']
        line_number, author, author_email, authored_date, author_tz_offset = field_names
        line_counter = 0
        for commit in iter_commits:
            line_counter += 1
            dictionary_data = {
                line_number: line_counter,
                author: commit.author.name.encode('utf-8'),
                author_email: commit.author.email.encode('utf-8'),
                authored_date: time.asctime(time.gmtime(commit.authored_date)),
                author_tz_offset: str(time.gmtime(commit.author_tz_offset).tm_hour) + ':' + str(time.gmtime(
                    commit.author_tz_offset).tm_min)}
            self.log(dictionary_data)
            yield dictionary_data

    # End Time Analysis Commits

    # Start Count Change

    def count_change_all_commits_limited_files_except_fix_commit(self, result_file_address, fix_commits_file_address):
        set_fix_commits_files = set()
        iter_fix_commits = self.iter_fix_commits(fix_commits_file_address)
        for fix_commit in iter_fix_commits:
            commit_spec = CommitSpec(fix_commit)

            try:
                patch_set = commit_spec.pars_diff(commit_spec.diff_commit_pre_version())
            except GitDiffEmptyException as err:
                print err
                continue
            except NoParentsCommitException as err:
                print err
                continue

            for patch_file in patch_set:
                if patch_file.source_file != '/dev/null':
                    set_fix_commits_files.add(patch_file.source_file[2:])
                if patch_file.target_file != '/dev/null':
                    set_fix_commits_files.add(patch_file.target_file[2:])

        self.count_change_all_commits_except_fix_commits(result_file_address=result_file_address,
                                                         fix_commits_file_address=fix_commits_file_address,
                                                         set_limited_files=set_fix_commits_files)

    def count_change_all_commits_except_fix_commits(self, result_file_address, fix_commits_file_address,
                                                    set_limited_files=None, file_format='parquet'):
        change_generator = self.count_change_generator(self.iter_commit_except_fix(fix_commits_file_address),
                                                       set_limited_files)
        self.choose_writing_format(result_file_address=result_file_address, data_generator=change_generator)

    def count_change_fix_commits(self, result_file_address, fix_commits_file_address, file_format='parquet'):
        change_generator = self.count_change_generator(self.iter_fix_commits(fix_commits_file_address))
        self.choose_writing_format(result_file_address=result_file_address, data_generator=change_generator)

    def count_change_all_commits(self, result_file_address, set_limited_files=None, file_format='parquet'):
        change_generator = self.count_change_generator(self.repository.iter_commits(), set_limited_files)
        self.choose_writing_format(result_file_address=result_file_address, data_generator=change_generator)

    def count_change_generator(self, iter_commits, set_limited_files=None):
        field_names = ['line_number', 'commit_number', 'commit_SHA', 'path', 'adds', 'deletes',
                       'changes']
        line_number, commit_number, commit_sha, path, adds, deletes, changes = field_names
        line_counter = 0
        commit_counter = 0

        for commit in iter_commits:
            commit_counter += 1
            commit_spec = CommitSpec(commit)

            try:
                patch_set = commit_spec.pars_diff(commit_spec.diff_commit_pre_version())
            except GitDiffEmptyException as err:
                print err
                continue
            except NoParentsCommitException as err:
                print err
                continue

            for patch_file in patch_set:
                line_counter += 1
                if set_limited_files:
                    if patch_file.path not in set_limited_files:
                        continue
                dictionary_data = {
                    line_number: line_counter,
                    commit_number: commit_counter,
                    commit_sha: commit_spec.commit_hex_sha,
                    path: patch_file.path,
                    adds: patch_file.added,
                    deletes: patch_file.removed,
                    changes: patch_file.added + patch_file.removed}
                self.log(dictionary_data)
                yield dictionary_data

    # End Count Change

    # Stat Count Number of Commits

    def count_commit(self):
        number_commit = len([commit for commit in self.repository.iter_commits()])
        print 'Total number of commits in  the repository: ' + str(number_commit)
        return number_commit

    # End Count Number of Commits

    # start write commit_SHA and message in file

    def export_all_commit_messages(self, result_file_address):
        self.export_commit_messages(result_file_address=result_file_address,
                                    iter_commits=self.repository.iter_commits())

    def export_commit_messages(self, result_file_address, iter_commits):
        with open(result_file_address, self.write_mode) as json_file:
            for commit in iter_commits:
                dictionary_data = {'commit_hash': commit.hexsha, 'commit_message': commit.message}
                if self.log_flag:
                    self.log(json.dumps(dictionary_data, indent=2, sort_keys=True))
                json_file.write(json.dumps(dictionary_data, sort_keys=True) + os.linesep)

    # end write commit_SHA and message in file
