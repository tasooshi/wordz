import argparse
import importlib.util
import multiprocessing
import pathlib
import sys
import tempfile

from wordz import (
    logs,
    version,
)


def class_import(path):
    try:
        file_path, class_name = path.split('::')
        spec = importlib.util.spec_from_file_location('wordz_combinator_clss', file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except (AttributeError, ValueError, FileNotFoundError):
        raise Exception(f'Could not import class from `{path}`')
    try:
        cls = getattr(module, class_name)
    except AttributeError:
        raise Exception(f'Class not found: `{path}`')
    else:
        return cls

def get_parser():
    cpu_count = multiprocessing.cpu_count()
    if cpu_count > 1:
        cpu_count = cpu_count - 1
    base_dir = pathlib.Path.cwd()
    parser = argparse.ArgumentParser(
        prog='wordz',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.print_usage = parser.print_help
    parser.add_argument('-p', '--path', required=True, default=argparse.SUPPRESS, help='Class path (e.g. classes/passwords.py::ExtraPasswords)')
    parser.add_argument('-b', '--base-dir', default=base_dir, help='Base directory path')
    parser.add_argument('-t', '--temp-dir', default='tmp', help='Temporary directory path')
    parser.add_argument('-o', '--output-dir', default=base_dir, help='Output directory path')
    parser.add_argument('-v', '--version', action='version', version=version.__version__, help='Print version')
    parser.add_argument('--min-length', default=4, help='Minimal length for a password when merging lists')
    parser.add_argument('--cores', default=cpu_count, type=str, help='Number of cores to be used for sorting')
    parser.add_argument('--memory', default='80%', help='Percentage of memory to be used for sorting')
    parser.add_argument('--bin-hashcat', default='hashcat', help='Hashcat binary')
    parser.add_argument('--bin-combinator', default='combinator.bin', help='Hashcat utils `combinator` binary')
    parser.add_argument('--bin-rli2', default='rli2.bin', help='Hashcat utils `rli2` binary')
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument('-d', '--debug', action='store_const', dest='loglevel', const=logs.logging.DEBUG, default=logs.logging.INFO)
    verbosity.add_argument('-q', '--quiet', action='store_const', dest='loglevel', const=logs.logging.NOTSET, default=logs.logging.INFO)
    return parser


def run(parser, args):
    parsed = parser.parse_args(args)
    logs.init(parsed.loglevel)
    CombinatorClass = class_import(parsed.path)
    combinator = CombinatorClass(
        parsed.base_dir,
        parsed.temp_dir,
        parsed.output_dir,
        parsed.min_length,
        parsed.cores,
        parsed.memory,
        parsed.bin_hashcat,
        parsed.bin_combinator,
        parsed.bin_rli2
    )
    combinator.run()


def main():
    parser = get_parser()
    try:
        run(parser, sys.argv[1:])
    except Exception as exc:
        logs.logger.error(exc)
        parser.error(exc)
    except KeyboardInterrupt:
        logs.logger.info(f'Exiting')


if __name__ == '__main__':
    sys.exit(main())
