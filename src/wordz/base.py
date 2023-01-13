import concurrent.futures
import datetime
import functools
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys
import uuid

from wordz import logs


os.environ['LC_ALL'] = 'C'


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
        self.temp_dir = pathlib.Path(temp_dir).absolute()
        self.output_dir = pathlib.Path(output_dir).absolute()
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
        output = subprocess.run('comm --nocheck-order', shell=True, capture_output=True).stderr
        if b'illegal option' in output:
            self.comm_ver = 'comm'
        else:
            self.comm_ver = 'comm --nocheck-order'
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

    def ensure_path(self, destination):
        dest_path = pathlib.Path(destination).parent
        if not pathlib.Path.exists(dest_path):
            logs.logger.debug(f'Creating directory `{destination}`')
            dest_path.mkdir(parents=True)

    def run_shell(self, cmd):
        logs.logger.debug(f' $ {cmd}')
        subprocess.run(cmd, shell=True)

    def wordlists_process(self):
        if self.wordlists and self.rules:
            for rule in self.rules:
                logs.logger.info(f'Processing wordlists with rules `{rule}`')
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    for wordlist in self.wordlists:
                        executor.submit(self.rule, pathlib.Path(self.base_dir, wordlist), pathlib.Path(self.base_dir, rule))

    def rule(self, wordlist, rule, dest_dir=None):
        if dest_dir is None:
            dest_dir = self.temp_dir
        filename = f'{rule.stem}-{wordlist.parts[-2]}-{wordlist.stem}.txt'
        if not pathlib.Path(dest_dir, filename).is_file():
            logs.logger.info(f'Processing `{wordlist}` with rule `{rule}`')
            self.run_shell(f'{self.bin_hashcat} --stdout --session={uuid.uuid4()} -r {rule} {wordlist} | {self.sort_snippet} | uniq > {dest_dir}/{filename}')
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
        self.ensure_path(destination)
        shutil.copyfile(source, destination)

    def append(self, source, destination):
        self.ensure_path(destination)
        if source.is_file():
            self.run_shell(f'cat {source} >> {destination}')
        else:
            logs.logger.warning(f'`{source}` not found!')

    def move(self, source, destination):
        self.ensure_path(destination)
        logs.logger.debug(f'Moving `{source}` to {destination}')
        shutil.move(source, destination)

    def delete(self, destination):
        logs.logger.debug(f'Deleting `{destination}`')
        pathlib.Path.unlink(destination, missing_ok=True)

    def delete_all(self, starts_with, destination):
        logs.logger.debug(f'Deleting all files starting with `{starts_with}` from `{destination}`')
        to_delete = destination.glob(starts_with + '*')
        for fil in to_delete:
            pathlib.Path.unlink(fil)

    def compare(self, left, right, output, append=False):
        redir = '>>' if append else '>'
        self.run_shell(f'{self.comm_ver} -13 {left} {right} {redir} {output}')

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

    def combine(self, method, left, right, destination=None):
        if destination is None:
            destination = self.temp_dir
        self.ensure_path(destination)
        if self.exist(left, right):
            name = None
            if method is self.RIGHT:
                name = f'{left.stem}+{right.stem}'
                if not pathlib.Path(destination, name + '.txt').is_file():
                    logs.logger.info(f'Combining `{left.stem}` with `{right.stem}`')
                    self.run_shell(f'{self.bin_combinator} {left} {right} > {destination}/{name}.txt')
            elif method is self.LEFT:
                name = f'{right.stem}+{left.stem}'
                if not pathlib.Path(destination, name + '.txt').is_file():
                    logs.logger.info(f'Combining `{right.stem}` with `{left.stem}`')
                    self.run_shell(f'{self.bin_combinator} {right} {left} > {destination}/{name}.txt')
            elif method is self.BOTH:
                name = f'{right.stem}+{left.stem}+{right.stem}'
                if not pathlib.Path(destination, f'{right.stem}+{left.stem}' + '.txt').is_file():
                    self.run_shell(f'{self.bin_combinator} {right} {left} > {destination}/{right.stem}+{left.stem}.txt')
                if not pathlib.Path(destination, name + '.txt').is_file():
                    logs.logger.info(f'Combining `{left.stem}` with `{right.stem}`')
                    self.run_shell(f'{self.bin_combinator} {destination}/{right.stem}+{left.stem}.txt {right} > {destination}/{name}.txt')
            else:
                raise NotImplementedError
            logs.logger.info(f'Combined `{name}`')
            return pathlib.Path(destination, name + '.txt')

    def split(self, wordlists, job_id):
        half_no = len(wordlists) / 2
        split_idx = int(half_no)
        output_name = hashlib.md5('+'.join([pathlib.Path(itm).stem for itm in wordlists]).encode('ASCII')).hexdigest()
        output = self.temp(f'{job_id}-split-' + output_name + '.txt')
        if half_no >= 2:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = [
                    executor.submit(self.split, wordlists[:split_idx], job_id).result(),
                    executor.submit(self.split, wordlists[split_idx:], job_id).result(),
                ]
            joined = ' '.join([str(pth) for pth in results])
        else:
            joined = ' '.join([str(pth) for pth in wordlists])
        self.run_shell(f'cat {joined} | {self.sort_snippet} | uniq > {output}')
        return output

    def merge(self, destination, wordlists, compare=None):
        logs.logger.info(f'Merging: {destination}')
        self.ensure_path(destination)
        wordlists = [words for words in wordlists if words is not None]
        for wordlist in wordlists:
            if wordlist.stat().st_size == 0:
                raise Exception(f'Wordlist {wordlist} is empty, something is not right. Aborting')
        self.delete(destination)
        job_id = str(uuid.uuid4())[:8]
        trimmed = list()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for wordlist in wordlists:
                trimmed_temp = self.temp(pathlib.Path(self.temp_dir, job_id + '-trimmed-' + wordlist.name))
                trimmed.append(trimmed_temp)
                executor.submit(self.run_shell, f'awk "length >= {self.min_length}" {wordlist} > {trimmed_temp}')
        output_temp = self.split(trimmed, job_id)
        if compare:
            self.run_shell(f'{self.bin_rli2} {output_temp} {compare} >> {destination}')
            self.append(destination, compare)
            self.sort(compare)
        else:
            self.move(output_temp, destination)
        # NOTE: Case when temporary files are really not needed.
        self.delete_all(job_id, self.temp_dir)

    def concat(self, destination, wordlists):
        logs.logger.debug(f'Concatenating: {destination}')
        self.delete(destination)
        self.ensure_path(destination)
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
