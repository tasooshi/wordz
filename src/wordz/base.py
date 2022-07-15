import datetime
import functools
import pathlib
import shutil
import subprocess
import sys

from wordz import logs


class Combinator:

    wordlists = None
    rules = None

    LEFT = 1
    BOTH = 2
    RIGHT = 3

    def __init__(self, base_dir, temp_dir, output_dir, min_length, cores, memory, bin_hashcat, bin_combinator, bin_rli2):
        self.checks_ok = True
        if not pathlib.Path.exists(pathlib.Path(temp_dir)):
            logs.logger.error(f'Temporary directory `{temp_dir}` does not exist!')
            self.checks_ok = False
        self.base_dir = base_dir
        self.temp_dir = temp_dir
        self.output_dir = output_dir
        self.min_length = min_length
        self.cores = cores
        self.memory = memory
        self.sort_snippet = f'sort -f -T {self.temp_dir} --parallel={cores} -S {memory}'
        self.bin_hashcat = bin_hashcat
        self.bin_combinator = bin_combinator
        self.bin_rli2 = bin_rli2
        self.check_which(self.bin_hashcat)
        self.check_which(self.bin_combinator)
        self.check_which(self.bin_rli2)
        if not self.checks_ok:
            raise Exception('Failed on startup')
            sys.exit(1)

    def check_which(self, name):
        if not shutil.which(pathlib.Path(name)):
            logs.logger.error(f'Binary `{name}` not found - consider adding it to $PATH environment variable')
            self.checks_ok = False

    def exist(self, *paths):
        for path in paths:
            if not pathlib.Path(path).is_file():
                logs.logger.debug(f'Resource `{path}` not found, skipping')
                return False
        return True

    def run_shell(self, cmd):
        logs.logger.debug(cmd)
        return subprocess.run(f'(export LC_ALL=C; {cmd})', shell=True, stdout=subprocess.PIPE).stdout

    def wordlists_process(self):
        if self.wordlists and self.rules:
            for rule in self.rules:
                logs.logger.info(f'Processing wordlists with rules `{rule}`')
                for wordlist in self.wordlists:
                    self.rule(pathlib.Path(self.base_dir, wordlist), pathlib.Path(self.base_dir, rule))

    def rule(self, wordlist, rule, dest_dir=None):
        if dest_dir is None:
            dest_dir = self.temp_dir
        filename = f'{rule.stem}-{wordlist.parts[-2]}-{wordlist.stem}.txt'
        if not pathlib.Path(dest_dir, filename).is_file():
            logs.logger.info(f'Processing `{wordlist}` with rule `{rule}`')
            self.run_shell(f'{self.bin_hashcat} --stdout -r {rule} {wordlist} | {self.sort_snippet} | uniq > {dest_dir}/{filename}')
        return pathlib.Path(f'{dest_dir}/{filename}')

    def sort(self, source, output=None, unique=False):
        if output is None:
            output = source
        cmd = f'{self.sort_snippet} {source} -o {output}'
        if unique:
            cmd += ' -u'
        self.run_shell(cmd)

    def copy(self, source, destination):
        logs.logger.debug(f'Copying `{source}` to {destination}')
        shutil.copyfile(source, destination)

    def append(self, source, destination):
        if source.is_file():
            self.run_shell(f'cat {source} >> {destination}')
        else:
            logs.logger.warning(f'`{source}` not found!')

    def move(self, source, destination):
        logs.logger.debug(f'Moving `{source}` to {destination}')
        shutil.move(source, destination)

    def delete(self, destination):
        logs.logger.debug(f'Deleting `{destination}`')
        pathlib.Path.unlink(destination, missing_ok=True)

    def compare(self, left, right, output, append=False):
        redir = '>>' if append else '>'
        self.run_shell(f'comm -13 {left} {right} {redir} {output}')

    @functools.cache
    def temp(self, name):
        return pathlib.Path(self.temp_dir, name)

    @functools.cache
    def base(self, name):
        return pathlib.Path(self.base_dir, name)

    @functools.cache
    def output(self, name):
        return pathlib.Path(self.output_dir, name)

    @functools.cache
    def right(self, left, right):
        return self.combine(self.RIGHT, left, right)

    @functools.cache
    def left(self, left, right):
        return self.combine(self.LEFT, left, right)

    @functools.cache
    def both(self, left, right):
        return self.combine(self.BOTH, left, right)

    def combine(self, method, left, right, dest_dir=None):
        if dest_dir is None:
            dest_dir = self.temp_dir
        if self.exist(left, right):
            name = None
            if method is self.RIGHT:
                name = f'{left.stem}+{right.stem}'
                if not pathlib.Path(dest_dir, name + '.txt').is_file():
                    logs.logger.info(f'Combining `{left.stem}` with `{right.stem}`')
                    self.run_shell(f'{self.bin_combinator} {left} {right} > {dest_dir}/{name}.txt')
            elif method is self.LEFT:
                name = f'{right.stem}+{left.stem}'
                if not pathlib.Path(dest_dir, name + '.txt').is_file():
                    logs.logger.info(f'Combining `{right.stem}` with `{left.stem}`')
                    self.run_shell(f'{self.bin_combinator} {right} {left} > {dest_dir}/{right.stem}+{left.stem}.txt')
            elif method is self.BOTH:
                name = f'{right.stem}+{left.stem}+{right.stem}'
                if not pathlib.Path(dest_dir, f'{right.stem}+{left.stem}' + '.txt').is_file():
                    self.run_shell(f'{self.bin_combinator} {right} {left} > {dest_dir}/{right.stem}+{left.stem}.txt')
                if not pathlib.Path(dest_dir, name + '.txt').is_file():
                    logs.logger.info(f'Combining `{left.stem}` with `{right.stem}`')
                    self.run_shell(f'{self.bin_combinator} {dest_dir}/{right.stem}+{left.stem}.txt {right} > {dest_dir}/{name}.txt')
            else:
                raise NotImplementedError
            logs.logger.info(f'Combined `{name}`')
            return pathlib.Path(dest_dir, name + '.txt')

    def merge(self, destination, wordlists, compare=None):
        logs.logger.info(f'Merging: {destination}')
        output_temp = self.temp(destination.stem)
        wordlists_arg = list()
        for wordlist in wordlists:
            if wordlist is None:
                continue
            if wordlist.stat().st_size == 0:
                raise Exception(f'Wordlist {wordlist} is empty, something is not right. Aborting')
            wordlists_arg.append(str(wordlist))
        wordlists_arg = ' '.join(wordlists_arg)
        # NOTE: Passing too many big files to sort directly leads to random segfaults.
        self.delete(destination)
        sort_cmd = f'awk "length >= {self.min_length}" {wordlists_arg} | {self.sort_snippet} | uniq > '
        if compare:
            self.run_shell(f'{sort_cmd} {output_temp}')
            self.run_shell(f'{self.bin_rli2} {output_temp} {compare} >> {destination}')
            self.append(destination, compare)
            self.sort(compare)
        else:
            self.run_shell(f'{sort_cmd} {destination}')

    def concat(self, destination, wordlists):
        logs.logger.debug(f'Concatenating: {destination}')
        self.delete(destination)
        for wordlist in wordlists:
            self.append(wordlist, destination)

    def diff(self, path, list_prefix, left='basic', right='extended', output='all'):
        left_fil = pathlib.Path(self.base_dir, path, f'{list_prefix}-{left}.txt')
        right_fil = pathlib.Path(self.base_dir, path, f'{list_prefix}-{right}.txt')
        output_fil = pathlib.Path(self.base_dir, path, f'{list_prefix}-{output}.txt')
        left_temp = self.temp(f'{list_prefix}-diff-{left}.txt')
        right_temp = self.temp(f'{list_prefix}-diff-{right}.txt')
        self.sort(left_fil, left_temp)
        self.sort(right_fil, right_temp)
        self.compare(left_temp, right_temp, right_fil)
        self.delete(left_fil)
        self.move(left_temp, left_fil)
        self.concat(output_fil, [left_fil, right_fil])
        self.sort(output_fil)

    def run(self):
        time_start = datetime.datetime.now()
        logs.logger.info(f'Processing with class: {type(self).__name__}')
        logs.logger.info(f'Base directory: {self.base_dir}')
        logs.logger.info(f'Temporary directory: {self.temp_dir}')
        logs.logger.info(f'Output directory: {self.output_dir}')
        logs.logger.info(f'Using {self.cores} cores')
        logs.logger.info(f'Using {self.memory} of memory')
        self.setup()
        self.process()
        time_total = datetime.datetime.now() - time_start
        logs.logger.info(f'Total time: {time_total}')
        logs.logger.info(f'Done! You may want to clean up the temporary directory yourself: {self.temp_dir}')

    def setup(self):
        self.wordlists_process()

    def process(self):
        raise NotImplementedError()
