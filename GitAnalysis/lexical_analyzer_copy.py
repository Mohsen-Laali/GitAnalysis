from pygments.util import ClassNotFound
from pygments.lexers import guess_lexer_for_filename, guess_lexer


class CantFindContentException(Exception):
    def __init__(self, message):
        super(CantFindContentException, self).__init__(message)


class LexicalAnalyzer:
    def __init__(self, txt, file_name=None):
        self.txt = txt
        self.file_name = file_name
        self.tokens = None
        self.lines = txt.splitlines(True)
        self.lexer = None
        self.lines_len = [len(line) for line in self.lines]

        passed_character = 0
        self.lines_len_so_far = [0]
        for idx in range(0, len(self.lines_len)):
            passed_character += self.lines_len[idx]
            self.lines_len_so_far.append(passed_character)
        self.analysis(self.txt, file_name)

    def analysis(self, txt, file_name=None):
        try:
            lxr = guess_lexer_for_filename(_fn=file_name, _text=txt, stripall=True, stripnl=True)
        except ClassNotFound as e:
            print e.message
            lxr = guess_lexer(_text=txt)
        if not lxr:
            return
        self.lexer = lxr
        # filter tokens like new line and white space

        self.tokens = [token for token in lxr.get_tokens_unprocessed(txt) if token[2].strip()]
        print txt
        for t in self.tokens:
            print t

        return self.tokens

    def find_token_line(self, line_number, tokens_with_previous=True):
        assert line_number > 0, 'Line number must larger than zero'
        lower_band = self.lines_len_so_far[line_number - 1]
        upper_band = self.lines_len_so_far[line_number]
        content = self.lines[line_number - 1]
        find_tokens = filter(lambda token: (lower_band <= token[0] < upper_band), self.tokens)
        # Find content if
        if len(find_tokens) == 0 and len(content.strip()) and tokens_with_previous:
            for ln in reversed(range(1, line_number)):
                tns, _ = self.find_token_line(ln, False)
                if len(tns):
                    for t in tns:
                        if content.strip() in t[2].strip():
                            return [t], content
                        else:
                            raise CantFindContentException('Can not find the content(' + content + ')')
            raise CantFindContentException('Can not find the content(' + content + ')')
        return find_tokens, content

    def find_token_lines(self, line_number_list):
        re_tokens = []
        for line_number in line_number_list:
            # try:
                tokens, content = self.find_token_line(line_number)
                if self.file_name is not None:
                    re_tokens.append((line_number, content, tokens, self.file_name))
                else:
                    re_tokens.append((line_number, content, tokens))
                    # TODO : fix this part
            # except (CantFindContentException, IndexError)as e:
            #     print e.message

        return re_tokens
