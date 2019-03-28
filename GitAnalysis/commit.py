import os
from GitAnalysis.lexical_analyzer import LexicalAnalyzer
from unidiff import PatchSet
from cStringIO import StringIO
from pygments.util import ClassNotFound
# from unidiff import UnidiffParseError


class GitDiffEmptyException(Exception):
    def __init__(self, commit_hex_sha):
        super(GitDiffEmptyException, self).__init__('There is no different this version and previous version: (' +
                                                    commit_hex_sha + ')')


class NoParentsCommitException(Exception):
    def __init__(self, commit_hex_sha):
        super(NoParentsCommitException, self).__init__('Commit does not have parent : (' + commit_hex_sha + ')')


class CommitSpec:
    def __init__(self, commit=None):
        self.commit = commit
        self.commit_hex_sha = self.commit.hexsha
        self.pre_commit_hex_sha = self.commit_hex_sha + '~1'

    def diff_commit_pre_version(self, **kwargs):
        if self.commit.parents:
            # Git ignore white space at the end of line, empty lines
            diff_txt = self.commit.repo.git.diff(self.pre_commit_hex_sha, self.commit_hex_sha,
                                                 ignore_blank_lines=True, ignore_space_at_eol=True, **kwargs)
        else:
            raise NoParentsCommitException(self.commit_hex_sha)

        return diff_txt

    def pars_diff(self, diff_txt):

        # check the if diff is empty
        if not diff_txt:
            raise GitDiffEmptyException(self.commit_hex_sha)

        patches = PatchSet(StringIO(diff_txt), encoding='utf-8')

        return patches

    def content_analyzer(self, analyze_part='deleted'):
        patch_sets = self.pars_diff(diff_txt=self.diff_commit_pre_version())
        tokens_list = []
        number_of_changes = 0
        for patched_file in patch_sets:
            file_path = patched_file.path

            analyze_line_number_list = []
            analyze_hex_sha = ''

            if analyze_part == 'added':
                analyze_line_number_list = [line.target_line_no for hunk in patched_file
                                            for line in hunk if line.is_added and line.value.strip() != '']
                analyze_hex_sha = self.commit_hex_sha

            elif analyze_part == 'deleted':
                analyze_line_number_list = [line.source_source_line_no for hunk in patched_file
                                            for line in hunk if line.is_removed and line.value.strip() != '']
                analyze_hex_sha = self.pre_commit_hex_sha

            if len(analyze_line_number_list) > 0:
                analyze_txt = self.commit.repo.git.show("%s:%s" % (analyze_hex_sha, file_path))
                try:
                    lexical_analyzer = LexicalAnalyzer(analyze_txt, file_name=file_path)
                    tokens = lexical_analyzer.find_token_lines(analyze_line_number_list)
                    tokens_list += tokens
                    number_of_changes += len(analyze_line_number_list)
                except ClassNotFound as e:
                    print e.message

        return tokens_list, number_of_changes

    def blame_content(self):
        blame_details_dictionary = {}
        total_added = 0
        total_deleted = 0
        patch_set = self.pars_diff(diff_txt=self.diff_commit_pre_version())

        # Calculate total add and delete in the comment
        for patched_file in patch_set:
            total_added += patched_file.added
            total_deleted += patched_file.removed

        # Blame deleted content for each content
        for patched_file in patch_set:
            blame_hash = {}
            line_number = 0
            file_path = patched_file.path
            deleted_line_number_list = map(lambda l: l.source_line_no,
                                           [line for hunk in patched_file for line in hunk if line.is_removed])
            deleted_line_number_list.sort()
            if len(deleted_line_number_list) != 0:
                blames = self.commit.repo.blame(self.pre_commit_hex_sha, file_path)

                # put blames in a hash for a fast access
                for blame_commit, blame_lines in blames:
                    for blame_line in blame_lines:
                        line_number += 1
                        blame_hash[line_number] = (blame_commit, blame_line)
                        # put hash up to last deleted line
                        if line_number > deleted_line_number_list[-1]:
                            break
                    if line_number > deleted_line_number_list[-1]:
                        break

                # retrieve blame from the hash
                for deleted_line_number in deleted_line_number_list:
                    blame_commit_line = blame_hash[deleted_line_number]
                    blame_commit = blame_commit_line[0]
                    content = blame_commit_line[1]
                    blame_detail = blame_details_dictionary.get(blame_commit.hexsha, BlameDetail(
                        blame_commit=blame_commit, fix_commit_hex_sha=self.commit_hex_sha,
                        total_added=total_added, total_deleted=total_deleted, file_path=file_path))
                    blame_detail.line_number_content_list.append((deleted_line_number, content))
                    blame_details_dictionary[blame_commit.hexsha] = blame_detail

        return blame_details_dictionary.values()


class BlameDetail:
    def __init__(self, blame_commit, fix_commit_hex_sha,
                 total_added, total_deleted, file_path):
        self.blame_commit = blame_commit
        self.fix_commit_hex_sha = fix_commit_hex_sha
        self.total_number_added = total_added
        self.total_number_deleted = total_deleted
        self.file_path = file_path
        self.line_number_content_list = []

    @property
    def number_of_related_lines(self):
        return len(self.line_number_content_list)

    def __str__(self):
        str_rep = '------------' + os.linesep
        str_rep += 'Blame commit hex sha: ' + self.blame_commit.hexsha + os.linesep
        str_rep += 'Fix commit hex sha: ' + self.fix_commit_hex_sha + os.linesep
        str_rep += 'File path: ' + self.file_path + os.linesep
        str_rep += 'Total number of added: ' + str(self.total_number_added) + os.linesep
        str_rep += 'Total number of deleted: ' + str(self.total_number_deleted) + os.linesep
        str_rep += 'Content:' + os.linesep
        for line_number_content in self.line_number_content_list:
            str_rep += str(line_number_content[0]) + ': ' + line_number_content[1] + os.linesep
        str_rep += '------------'
        return str_rep


if __name__ == '__main__':
    pass
