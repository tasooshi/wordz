import pathlib
import shlex
import tempfile

import pytest

from wordz import cli


def test_generic_use_case():
    cur_dir = pathlib.Path(__file__).parent
    tmp_dir = tempfile.mkdtemp()
    out_dir = tempfile.mkdtemp()
    args = shlex.split(f'-b {cur_dir} -p {cur_dir}/data/classes.py::Passwords -t {tmp_dir} -o {out_dir}')
    parser = cli.get_parser()
    cli.run(parser, args)
    with open(out_dir + '/passwords.txt') as fil:
        assert fil.readlines() == [
            '!ACAPULCO\n',
            '!acapulco\n',
            '!ACAPULCO!\n',
            '!acapulco!\n',
            '!ACAPULCO123\n',
            '!acapulco123\n',
            '!CERVEJA\n',
            '!cerveja\n',
            '!CERVEJA!\n',
            '!cerveja!\n',
            '!CERVEJA123\n',
            '!cerveja123\n',
            '123ACAPULCO\n',
            '123acapulco\n',
            '123ACAPULCO!\n',
            '123acapulco!\n',
            '123ACAPULCO123\n',
            '123acapulco123\n',
            '123CERVEJA\n',
            '123cerveja\n',
            '123CERVEJA!\n',
            '123cerveja!\n',
            '123CERVEJA123\n',
            '123cerveja123\n',
            'ACAPULCO!\n',
            'acapulco!\n',
            'ACAPULCO123\n',
            'acapulco123\n',
            'CERVEJA!\n',
            'cerveja!\n',
            'CERVEJA123\n',
            'cerveja123\n',
        ]
