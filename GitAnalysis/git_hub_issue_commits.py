import os
from exceptions import NotImplementedError


class GitHubIssueCommits:

    def __init__(self, text=None):
        self.similar_commits_limit_number = 10
        self.number = None
        self.issue_number = None
        self.repository_name = None
        self.issue_title = None
        self.issue_labels = None
        self.issue_commit_id = []
        self.issue_closed_commit_id = []
        self.commit_id_similar_to_issue_title = []
        self.diff_url = None
        self.html_url = None
        self.patch_url = None
        if text:
            self.init_from_text(text)

    def init_from_text(self, text):
        # need to adjust for new format
        split_text = text.strip().split(',')
        self.number = split_text[0]
        self.repository_name = split_text[1]
        self.issue_title = split_text[2]
        self.issue_commit_id = split_text[3]
        self.diff_url = split_text[4]
        self.html_url = split_text[5]
        self.patch_url = split_text[6]
        raise NotImplementedError()

    def init_from_dictionary(self, row_dictionary):
        self.number = row_dictionary['number']
        self.issue_number = row_dictionary['issue_number']
        self.repository_name = row_dictionary['repository_name']
        self.issue_title = row_dictionary['issue_title']
        if 'issue_labels' in row_dictionary:
            self.issue_labels = row_dictionary['issue_labels']
        if 'issue_commit_id' in row_dictionary:
            self.issue_commit_id = row_dictionary['issue_commit_id']
        if 'issue_closed_commit_id' in row_dictionary:
            self.issue_closed_commit_id = row_dictionary['issue_closed_commit_id']
        if 'commit_id_similar_to_issue_title' in row_dictionary:
            self.commit_id_similar_to_issue_title = row_dictionary['commit_id_similar_to_issue_title']
        if 'diff_url' in row_dictionary:
            self.diff_url = row_dictionary['diff_url']
        if 'html_url' in row_dictionary:
            self.html_url = row_dictionary['html_url']
        if 'patch_url' in row_dictionary:
            self.patch_url = row_dictionary['patch_url']

    def get_fix_commits(self):
        if len(self.commit_id_similar_to_issue_title) > self.similar_commits_limit_number:
            return self.issue_closed_commit_id + self.issue_commit_id
        else:
            return self.issue_closed_commit_id + self.issue_commit_id + self.commit_id_similar_to_issue_title

    def __str__(self):
        txt = 'number: ' + str(self.number) + os.linesep
        txt += 'issue number: ' + str(self.issue_number) + os.linesep
        txt += 'repository name: ' + self.repository_name + os.linesep
        txt += 'issue title: ' + self.issue_title + os.linesep
        txt += 'issue labels: ' + str(self.issue_labels) + os.linesep
        txt += 'issue commit id: ' + str(self.issue_commit_id) + os.linesep
        txt += 'issue closed commit id: ' + str(self.issue_closed_commit_id) + os.linesep
        txt += 'diff url: ' + str(self.diff_url) + os.linesep
        txt += 'html url: ' + str(self.diff_url) + os.linesep
        txt += 'patch url: ' + str(self.patch_url) + os.linesep
        return txt
