

class FileSpec:

    def __init__(self, old_file_name=None, new_file_name=None, added_lines=[], deleted_lines=[], commit_sha=None):

        self.old_file_name = old_file_name
        self.new_file_name = new_file_name
        self.added_lines = added_lines
        self.deleted_lines = deleted_lines
        self.commit_SHA = commit_sha

    @property
    def number_deleted_lines(self):

        return len(self.deleted_lines)

    @property
    def number_added_lines(self):

        return len(self.added_lines)

    def number_changed_lines(self):
        """

        :return: total number of changed in the files in specific commit
        """
        return self.number_added_lines + self.number_deleted_lines

    def added_line_number(self):
        pass
