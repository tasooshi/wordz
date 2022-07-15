import pathlib
import shlex
import subprocess
import shutil
import tempfile

import pytest

from wordz import cli


def test_run_main_help(capfd):
    subprocess.run(['wordz', '-h'])
    out, err = capfd.readouterr()
    assert 'show this help message and exit' in out


def test_generic_use_case(cwd, tmp_dir, out_dir):
    args = shlex.split(f'-b {cwd} -p {cwd}/data/classes.py::Passwords -t {tmp_dir} -o {out_dir}')
    parser = cli.get_parser()
    cli.run(parser, args)
    output_file = out_dir + '/passwords.txt'
    with open(output_file) as fil:
        assert fil.readlines() == ['!ACAPULCO\n', '!acapulco\n', '!ACAPULCO!\n', '!acapulco!\n', '!ACAPULCO123\n', '!acapulco123\n', '!CERVEJA\n', '!cerveja\n', '!CERVEJA!\n', '!cerveja!\n', '!CERVEJA123\n', '!cerveja123\n', '123ACAPULCO\n', '123acapulco\n', '123ACAPULCO!\n', '123acapulco!\n', '123ACAPULCO123\n', '123acapulco123\n', '123CERVEJA\n', '123cerveja\n', '123CERVEJA!\n', '123cerveja!\n', '123CERVEJA123\n', '123cerveja123\n', 'ACAPULCO!\n', 'acapulco!\n', 'ACAPULCO123\n', 'acapulco123\n', 'CERVEJA!\n', 'cerveja!\n', 'CERVEJA123\n', 'cerveja123\n']


def test_hashcat_doesnt_exist(cwd, tmp_dir):
    args = shlex.split(f'-b {cwd} -p {cwd}/data/classes.py::Passwords -t {tmp_dir} --bin-hashcat weedcat')
    parser = cli.get_parser()
    with pytest.raises(Exception) as exc_info:
        cli.run(parser, args)
    assert exc_info.match('Failed on startup')


def test_temp_doesnt_exist(cwd):
    args = shlex.split(f'-b {cwd} -p {cwd}/data/classes.py::Passwords -t DOES_NOT_EXIST')
    parser = cli.get_parser()
    with pytest.raises(Exception) as exc_info:
        cli.run(parser, args)
    assert exc_info.match('Failed on startup')


def test_import_path_exceptions(cwd):
    with pytest.raises(Exception) as exc_info:
        cli.class_import('xxx')
    assert exc_info.match('Could not import')

    with pytest.raises(Exception) as exc_info:
        cli.class_import(f'{cwd}/data/classes.py')
    assert exc_info.match('Could not import')


def test_import_class_exceptions(cwd):
    with pytest.raises(Exception) as exc_info:
        cli.class_import(f'{cwd}/data/classes.py::')
    assert exc_info.match('Class not found')

    with pytest.raises(Exception) as exc_info:
        cli.class_import(f'{cwd}/data/classes.py::Void')
    assert exc_info.match('Class not found')


def test_quiet(cwd, tmp_dir, caplog):
    args = shlex.split(f'-p {cwd}/data/classes.py::Passwords -q -t {tmp_dir}')
    parser = cli.get_parser()
    cli.run(parser, args)
    assert caplog.text == ''
