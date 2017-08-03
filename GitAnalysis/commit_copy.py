import os
import whatthepatch
from git.exc import  GitCommandError
from GitAnalysis.lexical_analyzer import LexicalAnalyzer
from unidiff import PatchSet


class CommitSpec:

    def __init__(self, commit=None):
        """

        :type changed_files_list: list of FileSpec
        """
        self.commit = commit
        self.commit_hex_sha = self.commit.hexsha
        self.pre_commit_hex_sha = self.commit.repo.commit(self.commit_hex_sha + '~1').hexsha

        # self.pre_commit_hex_sha = repo.commit(self.commit_hex_sha + '~1').hexsha
        # self.pre_commit_hex_sha = self.commit_hex_sha + '~1'

    def diff_commit_pre_version(self, **kwargs):
        diff_index = self.commit.diff(self.pre_commit_hex_sha, create_patch=True, **kwargs)
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
        diff_txt = reduce(lambda x, y: str(x)+os.linesep+str(y), diff_index)
        return PatchSet(diff_txt)

    def changed_files(self):
        """
        Returned list of changed files

        """
        pars_diff_list = self.pars_diff_wp()
        changed_files_list = []
        for pars_diff in pars_diff_list:
            changed_files_list.append(FileChanges(pars_diff, self.commit.hexsha))
        return changed_files_list

    # def added_content_analyzer(self):
    #     def analyses_part_fun(changed_file):
    #         return changed_file.line_number_of_added_lines
    #     self.content_analyzer(analyses_part_fun, self.commit_hex_sha)
    #
    # def deleted_content_analyzer(self):
    #     def analyses_part_fun(changed_file):
    #         return changed_file.line_number_of_deleted_lines
    #     self.content_analyzer(analyses_part_fun, self.pre_commit_hex_sha)

    def content_analyzer(self, analyze_part='deleted'):
        changed_files_list = self.changed_files()
        tokens_list = []
        number_of_changes = 0
        pre_commit_hex_sha = self.pre_commit_hex_sha
        for changed_file in changed_files_list:
            file_path = changed_file.new_path
            print '###############################'
            print '###############################'
            print 'Current has'
            print self.commit_hex_sha
            print 'Pre hash'
            print self.pre_commit_hex_sha

            if file_path == '/dev/null':
                print changed_file.deleted_lines
                print changed_file.added_lines
                file_path = changed_file.old_path
                pre_commit_hex_sha = self.commit_hex_sha
                print 'path /dev/null'
                raw_input('press any key')

            print 'Changed file'
            print changed_file
            deleted_lines = changed_file.deleted_lines
            print 'deleted lines'
            for deleted_line in deleted_lines:
                print deleted_line
            added_lines = changed_file.added_lines
            print 'added lines'
            for added_line in added_lines:
                print added_line

            analyze_line_number_list = []
            analyze_txt = ''
            print '--------------'
            if changed_file.changed_file_name:
                print 'changed file name'
            print '--------------'

            if analyze_part == 'added' and changed_file.number_of_added_lines > 0:
                analyze_line_number_list = changed_file.line_number_of_added_lines
                analyze_txt = self.commit.repo.git.show("%s:%s" % (self.commit_hex_sha, file_path))
            elif analyze_part == 'deleted' and changed_file.number_of_deleted_lines > 0:
                print changed_file.number_of_deleted_lines
                analyze_line_number_list = changed_file.line_number_of_deleted_lines
                #TODO fix this part
                # try:
                #     analyze_txt = self.commit.repo.git.show("%s:%s" % (pre_commit_hex_sha, file_path))
                # except GitCommandError:
                #     try:
                #         analyze_txt = self.commit.repo.git.show("%s:%s" % (pre_commit_hex_sha, changed_file.old_path))
                #     except GitCommandError:
                #         print 'exception !!'
                #         continue
                # try:
                if changed_file.old_path != '/dev/null':
                    print 'ooooooooooooooooooooooooooooooooo'
                    print self.commit.repo.git.show("%s:%s" % (self.commit_hex_sha, changed_file.old_path))

                analyze_txt = self.commit.repo.git.show("%s:%s" % (pre_commit_hex_sha, file_path))
                # except GitCommandError:
                #     raw_input('gitCommand Error ')
                #     continue
                # TODO end fix part

            number_of_changes += len(analyze_line_number_list)
            lexical_analyzer = LexicalAnalyzer(analyze_txt, file_name=file_path)
            tokens = lexical_analyzer.find_token_lines(analyze_line_number_list)
            tokens_list += tokens
        return tokens_list, number_of_changes

    def blame_content(self):
        blame_details_dictionary = {}
        total_added = 0
        total_deleted = 0
        changed_files_list = self.changed_files()

        # Calculate total add and delete in the comment
        for changed_file in changed_files_list:
            total_added += changed_file.number_of_added_lines
            total_deleted += changed_file.number_of_deleted_lines

        # Blame deleted content for each content
        for changed_file in changed_files_list:
            blame_hash = {}
            line_number = 0
            file_path = changed_file.new_path
            deleted_line_number_list = changed_file.line_number_of_deleted_lines
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
        deleted_lines = map(lambda line: line[2], self.deleted_lines)
        added_lines = map(lambda line: line[2], self.added_lines)
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
            if set(map(lambda line: line[2], self.deleted_lines)) == set(map(lambda line: line[2], self.added_lines)):
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
            str_rep += str(line_number_content[0])+': '+line_number_content[1]+os.linesep
        str_rep += '------------'
        return str_rep


if __name__ == '__main__':
    pass


