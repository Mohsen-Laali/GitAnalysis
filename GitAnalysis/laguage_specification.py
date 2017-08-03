

class LanguageSpecification:

    def __init__(self):
        pass

    @staticmethod
    def java_keywords():
        keywords = ['abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const']
        keywords += ['continue', 'default', 'do', 'double', 'else', 'enum', 'extends', 'final', 'finally', 'float']
        keywords += ['for', 'goto', 'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'native']
        keywords += ['new', 'package', 'private', 'protected', 'public', 'return', 'short', 'static', 'strictfp',
                     'super']
        keywords += ['switch', 'synchronized', 'this', 'throw', 'throws', 'transient', 'try', 'void', 'volatile',
                     'while']
        return keywords

