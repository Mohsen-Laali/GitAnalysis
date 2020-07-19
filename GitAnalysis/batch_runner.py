import os
import shutil
from datetime import datetime
import json
import traceback

from GitAnalysis import GitAnalysis


class BaseConfig:

    def __init__(self, json_config):
        self.language_label = str(json_config['language_label'])
        self.repo_base_address = str(json_config['repo_base_address'])
        self.issue_base_address = str(json_config['issue_base_address'])
        self.output_folder = str(json_config['output_folder'])
        self.retrieve_other_commit_id_from_issue_tracker = json_config[
                                                                   'retrieve_other_commit_id_from_issue_tracker']
        self.consider_issues_without_labels_as_other = json_config['consider_issues_without_labels_as_other']
        self.log_flag = json_config['log_flag']


class RepoIssueDetails:

    def __init__(self, json_config):
        self.repo_name = str(json_config['repo_name'])
        self.issue_file_name = str(json_config['issue_file_name'])
        self.bug_issue_label = str(json_config['bug_label'])


class BatchRunner:

    def __init__(self, batch_file, log_flag=True, error_log_file_name='error_log.txt'):
        self.batch_file = batch_file
        self.log_flag = log_flag
        self.error_log_file_name = error_log_file_name
        self.fix_label = 'Fix'
        self.non_fix_label = 'NonFix'
        self.all_commits_label = 'AllCommits'

    def log(self, log_str):
        if self.log_flag:
            print(log_str)

    def log_error(self, exception, starter=None, extra=None):

        with open(self.error_log_file_name, 'a') as f_handler:
            if starter:
                f_handler.write(starter + os.linesep)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            f_handler.write(current_time + os.linesep)
            if hasattr(exception, 'message') and exception:
                f_handler.write(str(exception.message) + os.linesep)
            elif exception:
                f_handler.write(str(exception) + os.linesep)
            if extra:
                f_handler.write(extra + os.linesep)
            f_handler.write('***********************' + os.linesep)

    def creat_folder(self, folder_path):
        try:
            os.makedirs(folder_path)
        except OSError as e:
            extra = traceback.format_exc()
            error_message = "Creation of the directory " + folder_path + " failed"
            self.log(log_str=error_message)
            self.log(log_str=extra)
            self.log(log_str='***********************' + os.linesep)
            self.log_error(exception=e, starter=error_message, extra=extra)
            raise e
        else:
            message = "Successfully created the directory " + folder_path
            self.log(log_str=message)

    def delete_folder(self, folder_path):
        try:
            shutil.rmtree(folder_path)
        except OSError as e:
            extra = traceback.format_exc()
            error_message = "Deletion of the directory " + folder_path + "  failed"
            self.log(log_str=error_message)
            self.log(log_str=extra)
            self.log(log_str='***********************' + os.linesep)
            self.log_error(exception=e, starter=error_message)
            raise e
        else:
            message = "Successfully deleted the directory " + folder_path
            self.log(log_str=message)

    def read_batch_file(self):
        list_json_repo = []
        with open(self.batch_file, 'r+') as file_handler:
            for line in file_handler:
                # skip empty line
                if not line.strip():
                    continue
                json_repo = json.loads(line)
                list_json_repo.append(json_repo)

        return list_json_repo

    def run_batch(self):
        list_json_config = self.read_batch_file()
        base_config = BaseConfig(list_json_config[0])
        list_repo_issue_details = map(lambda json_config: RepoIssueDetails(json_config=json_config),
                                      list_json_config[1:])
        for repo_issue_details in list_repo_issue_details:
            self.run(base_config=base_config, repo_issue_details=repo_issue_details)

    def run(self, base_config, repo_issue_details):
        self.log('#####################')
        self.log('Start ' + repo_issue_details.repo_name)
        self.log('#####################')
        fix_commits_file_address = os.path.join(base_config.issue_base_address, repo_issue_details.issue_file_name)
        repository_address = os.path.join(base_config.repo_base_address, repo_issue_details.repo_name)
        retrieve_other_commit_id_from_issue_tracker = base_config.retrieve_other_commit_id_from_issue_tracker
        consider_issues_without_labels_as_other = base_config.consider_issues_without_labels_as_other
        tuple_keep_attribute = ('issue_labels', repo_issue_details.bug_issue_label)
        write_mode = 'wb'
        log_flag = True
        output_folder = base_config.output_folder
        git_analysis = GitAnalysis(repository_address=repository_address,
                                   retrieve_other_commit_id_from_issue_tracker=
                                   retrieve_other_commit_id_from_issue_tracker,
                                   consider_issues_without_labels_as_other=
                                   consider_issues_without_labels_as_other,
                                   tuple_keep_attribute=tuple_keep_attribute,
                                   write_mode=write_mode,
                                   log_flag=log_flag)

        # End initial setup
        file_name = str.join("_", [str.capitalize(base_config.language_label),
                                   str.capitalize(repo_issue_details.repo_name)])
        fix_file_name = os.path.join(output_folder, str.join("_", [file_name, self.fix_label + '.csv']))
        non_fix_file_name = os.path.join(output_folder, str.join("_", [file_name, self.non_fix_label + '.csv']))
        all_commits_file_name = os.path.join(output_folder, str.join("_", [file_name, self.all_commits_label + '.csv']))

        self.log('+++++++++++++++++++++')
        self.log('User behaviour - fix commits ' + repo_issue_details.repo_name)
        self.log('+++++++++++++++++++++')

        git_analysis.user_behaviour_deleted_lines_fix_commits(result_file_address=fix_file_name,
                                                              fix_commits_file_address=fix_commits_file_address,
                                                              output_format='csv')

        self.log('+++++++++++++++++++++')
        self.log('User behaviour - non-fix commits ' + repo_issue_details.repo_name)
        self.log('+++++++++++++++++++++')

        git_analysis.user_behavior_all_commits_except_fix_commits(result_file_address=non_fix_file_name,
                                                                  fix_commits_file_address=fix_commits_file_address,
                                                                  output_format='csv')
        self.log('+++++++++++++++++++++')
        self.log('User behaviour - all commits ' + repo_issue_details.repo_name)
        self.log('+++++++++++++++++++++')

        git_analysis.user_behavior_all_commits(result_file_address=all_commits_file_name,
                                               output_format='csv')

        self.log('#####################')
        self.log('End ' + repo_issue_details.repo_name)
        self.log('#####################')

