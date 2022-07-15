from wordz import Combinator


class Passwords(Combinator):

    wordlists = (
        'data/keywords.txt',
    )
    rules = (
        'data/hashcat.rule',
    )

    def process(self):

        self.merge(
            self.output('passwords.txt'),
            (
                self.right(self.temp('hashcat-data-keywords.txt'), self.base('data/bits.txt')),
                self.left(self.temp('hashcat-data-keywords.txt'), self.base('data/bits.txt')),
                self.both(self.temp('hashcat-data-keywords.txt'), self.base('data/bits.txt')),
            )
        )


class WorkflowBase(Combinator):

    passwords_all = 'passwords-all.txt'
    wordlists = (
        'data/keywords.txt',
    )
    rules = (
        'data/hashcat.rule',
        'data/hax0r.rule',
    )

    def setup(self):
        for lst in ['patterns', 'numbers']:
            self.diff('data/extrabits', lst)

        basic = self.base('data/extrawords/keywords-basic.txt')
        extended = self.base('data/extrawords/keywords-extended.txt')
        self.sort(basic, self.temp('lowercase-keywords-basic.txt'))
        self.sort(extended, self.temp('lowercase-keywords-extended.txt'))
        self.compare(self.temp('lowercase-keywords-basic.txt'), self.temp('lowercase-keywords-extended.txt'), extended)
        self.delete(basic)
        self.copy(self.temp('lowercase-keywords-basic.txt'), basic)

        self.delete(self.base('data/extrawords/all.txt'))
        self.sort(self.base('data/extrawords/*.txt'), self.temp('lowercase-keywords-all.txt'), unique=True)
        self.copy(self.temp('lowercase-keywords-all.txt'), self.base('data/extrawords/all.txt'))

        if not self.temp(self.passwords_all).is_file():
            self.sort(self.base('data/classic.txt'), self.temp(self.passwords_all))

        self.wordlists_process()


class WorkflowA(WorkflowBase):

    def process(self):
        hashcat_keywords = self.temp('hashcat-data-keywords.txt')
        self.merge(
            self.output('workflow-a.txt'),
            (
                self.both(hashcat_keywords, self.base('data/extrabits/patterns-basic.txt')),
                self.right(hashcat_keywords, self.base('data/extrabits/patterns-extended.txt')),
                self.right(hashcat_keywords, self.base('data/extrabits/numbers-all.txt')),
                self.left(hashcat_keywords, self.base('data/extrabits/numbers-basic.txt')),
                self.right(self.temp('hax0r-data-keywords.txt'), self.base('data/extrabits/patterns-basic.txt')),
                self.base('data/classic.txt'),
                hashcat_keywords,
            ),
            compare=self.temp(self.passwords_all)
        )


class WorkflowB(WorkflowBase):

    def process(self):
        self.merge(
            self.output('workflow-b.txt'),
            (
                self.right(self.temp('hax0r-data-keywords.txt'), self.base('data/extrabits/patterns-extended.txt')),
            ),
            compare=self.temp(self.passwords_all)
        )
