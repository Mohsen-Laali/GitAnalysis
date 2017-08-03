import os
import whatthepatch
from GitAnalysis.lexical_analyzer import LexicalAnalyzer
from unidiff import PatchSet
from cStringIO import StringIO
from pygments.util import ClassNotFound
from unidiff import UnidiffParseError


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
            pre_commit = self.commit.repo.commit(self.pre_commit_hex_sha)
        else:
            raise NoParentsCommitException(self.commit_hex_sha)

        # Git ignore white space at the end of line, empty lines, renamed files, also copied files and also
        diff_index = pre_commit.diff(self.commit_hex_sha, create_patch=True, ignore_blank_lines=True,
                                     ignore_space_at_eol=True, diff_filter='crt', ignore_submodules=True, **kwargs)
        # diff_index = self.commit.diff(self.pre_commit_hex_sha, create_patch=True, **kwargs)
        return diff_index

    def pars_diff_wp(self):
        diff_index = self.diff_commit_pre_version()
        pars_diff_list = []
        for idx in diff_index:
            dif = idx.diff
            for pars_diff in whatthepatch.parse_patch(str(dif)):
                pars_diff_list.append(pars_diff)
        return pars_diff_list

    def pars_diff(self, diff_index):

        if len(diff_index) > 1:
            diff_txt = reduce(lambda x, y: str(x) + os.linesep + str(y), diff_index)
        elif len(diff_index) == 1:
            diff_txt = str(diff_index[0])
        else:
            raise GitDiffEmptyException(self.commit_hex_sha)

        patches = PatchSet(StringIO(diff_txt), encoding='utf-8')

        return patches

    def changed_files(self):
        """
        Returned list of changed files

        """
        pars_diff_list = self.pars_diff_wp()
        changed_files_list = []
        for pars_diff in pars_diff_list:
            changed_files_list.append(FileChanges(pars_diff, self.commit.hexsha))
        return changed_files_list

    def content_analyzer(self, analyze_part='deleted'):
        patch_set = self.pars_diff(diff_index=self.diff_commit_pre_version())
        tokens_list = []
        number_of_changes = 0
        for patched_file in patch_set:
            file_path = patched_file.path

            analyze_line_number_list = []
            analyze_hex_sha = ''

            if analyze_part == 'added':
                analyze_line_number_list = map(lambda l_: l_.target_line_no,
                                               [line for hunk in patched_file for line in hunk if line.is_added and
                                                line.value.strip() != ''])
                analyze_hex_sha = self.commit_hex_sha

            elif analyze_part == 'deleted':
                analyze_line_number_list = map(lambda l_: l_.source_line_no,
                                               [line for hunk in patched_file for line in hunk if line.is_removed and
                                                line.value.strip() != ''])
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
        patch_set = self.pars_diff(diff_index=self.diff_commit_pre_version())

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


class FileChanges:
    def __init__(self, pars_diff, commit_sha):
        self.commit_SHA = commit_sha
        self.index_path = pars_diff.header.index_path
        self.old_path = pars_diff.header.old_path.strip()
        self.new_path = pars_diff.header.new_path.strip()
        self.old_version = pars_diff.header.old_version
        self.new_version = pars_diff.header.new_version
        self.changes = pars_diff.changes

    @property
    def changed_file_name(self):
        dev_null = '/dev/null'
        deleted_lines = map(lambda l: l[2], self.deleted_lines)
        added_lines = map(lambda l: l[2], self.added_lines)
        print '_+_+_+_+'
        for line in deleted_lines:
            print line
        print '=-=--=-=-'
        if len(deleted_lines) == len(added_lines):
            for ind in range(0, len(deleted_lines)):
                if deleted_lines[ind] != added_lines[ind]:
                    print '********************************'
                    print deleted_lines[ind]
                    print added_lines[ind]
                    print '********************************'
        for line in added_lines:
            print line

        if self.old_path != self.new_path and self.new_path != dev_null and self.old_path != dev_null:
            if set(map(lambda l: l[2], self.deleted_lines)) == set(map(lambda l: l[2], self.added_lines)):
                return True
        return False

    @property
    def added_lines(self):
        return filter(lambda line: line[1] is None and line[2].strip() != '', self.changes)

    @property
    def deleted_lines(self):
        return filter(lambda line: line[0] is None and line[2].strip() != '', self.changes)

    @property
    def changed_lines(self):
        return filter(lambda line: (line[0] is None or line[1] is None) and line[2].strip() != '', self.changes)

    @property
    def line_number_of_added_lines(self):
        return [added_line[0] for added_line in self.added_lines]

    @property
    def line_number_of_deleted_lines(self):
        return [deleted_line[1] for deleted_line in self.deleted_lines]

    @property
    def line_number_of_changed_lines(self):
        return self.line_number_of_added_lines + self.line_number_of_deleted_lines

    @property
    def number_of_added_lines(self):
        return len(self.added_lines)

    @property
    def number_of_deleted_lines(self):
        return len(self.deleted_lines)

    @property
    def number_of_changed_lines(self):
        return len(self.changed_lines)

    def __str__(self):
        content = 'index path: ' + str(self.index_path) + os.linesep
        content += 'old path: ' + str(self.old_path) + os.linesep
        content += 'new path: ' + str(self.new_path) + os.linesep
        content += 'old version: ' + str(self.old_version) + os.linesep
        content += 'new version: ' + str(self.new_version) + os.linesep
        content += 'changes: ' + os.linesep
        for change in self.changes:
            content += str(change) + os.linesep
        return content


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
