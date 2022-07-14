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
