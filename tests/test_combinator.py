import shlex

import pytest

from wordz import cli


def test_workflow(cwd, tmp_dir, out_dir):
    args = shlex.split(f'-b {cwd} -p {cwd}/data/classes.py::WorkflowA -t {tmp_dir} -o {out_dir}')
    parser = cli.get_parser()
    cli.run(parser, args)
    output_file = out_dir + '/workflow-a.txt'
    with open(output_file) as fil:
        assert fil.readlines() == ['!ACAPULCO!\n', '!acapulco!\n', '!ACAPULCO#\n', '!acapulco#\n', '!ACAPULCO@\n', '!acapulco@\n', '!CERVEJA!\n', '!cerveja!\n', '!CERVEJA#\n', '!cerveja#\n', '!CERVEJA@\n', '!cerveja@\n', '#ACAPULCO!\n', '#acapulco!\n', '#ACAPULCO#\n', '#acapulco#\n', '#ACAPULCO@\n', '#acapulco@\n', '#CERVEJA!\n', '#cerveja!\n', '#CERVEJA#\n', '#cerveja#\n', '#CERVEJA@\n', '#cerveja@\n', '$c$pulc)!\n', '$c$pulc)#\n', '$c$pulc)@\n', '2022ACAPULCO\n', '2022acapulco\n', '2022CERVEJA\n', '2022cerveja\n', '@ACAPULCO!\n', '@acapulco!\n', '@ACAPULCO#\n', '@acapulco#\n', '@ACAPULCO@\n', '@acapulco@\n', '@CERVEJA!\n', '@cerveja!\n', '@CERVEJA#\n', '@cerveja#\n', '@CERVEJA@\n', '@cerveja@\n', 'ACAPULCO\n', 'acapulco\n', 'ACAPULCO!!\n', 'acapulco!!\n', 'acapulco#\n', 'ACAPULCO##\n', 'acapulco##\n', 'ACAPULCO2020\n', 'acapulco2020\n', 'ACAPULCO2021\n', 'acapulco2021\n', 'ACAPULCO2022\n', 'acapulco2022\n', 'ACAPULCO@@\n', 'acapulco@@\n', 'c#rv#j$!\n', 'c#rv#j$#\n', 'c#rv#j$@\n', 'CERVEJA\n', 'cerveja\n', 'cerveja!\n', 'CERVEJA!!\n', 'cerveja!!\n', 'cerveja#\n', 'CERVEJA##\n', 'cerveja##\n', 'CERVEJA2020\n', 'cerveja2020\n', 'CERVEJA2021\n', 'cerveja2021\n', 'CERVEJA2022\n', 'cerveja@\n', 'CERVEJA@@\n', 'cerveja@@\n']

    args = shlex.split(f'-b {cwd} -p {cwd}/data/classes.py::WorkflowB -t {tmp_dir} -o {out_dir}')
    parser = cli.get_parser()
    cli.run(parser, args)
    output_file = out_dir + '/workflow-b.txt'
    with open(output_file) as fil:
        assert fil.readlines() == ['$c$pulc)!!\n', '$c$pulc)##\n', '$c$pulc)@@\n', 'c#rv#j$!!\n', 'c#rv#j$##\n', 'c#rv#j$@@\n']

    with open(tmp_dir + '/passwords-all.txt') as fil:
        assert fil.readlines() == ['!ACAPULCO!\n', '!acapulco!\n', '!ACAPULCO#\n', '!acapulco#\n', '!ACAPULCO@\n', '!acapulco@\n', '!CERVEJA!\n', '!cerveja!\n', '!CERVEJA#\n', '!cerveja#\n', '!CERVEJA@\n', '!cerveja@\n', '#ACAPULCO!\n', '#acapulco!\n', '#ACAPULCO#\n', '#acapulco#\n', '#ACAPULCO@\n', '#acapulco@\n', '#CERVEJA!\n', '#cerveja!\n', '#CERVEJA#\n', '#cerveja#\n', '#CERVEJA@\n', '#cerveja@\n', '$c$pulc)!\n', '$c$pulc)!!\n', '$c$pulc)#\n', '$c$pulc)##\n', '$c$pulc)@\n', '$c$pulc)@@\n', '2022ACAPULCO\n', '2022acapulco\n', '2022CERVEJA\n', '2022cerveja\n', '@ACAPULCO!\n', '@acapulco!\n', '@ACAPULCO#\n', '@acapulco#\n', '@ACAPULCO@\n', '@acapulco@\n', '@CERVEJA!\n', '@cerveja!\n', '@CERVEJA#\n', '@cerveja#\n', '@CERVEJA@\n', '@cerveja@\n', 'ACAPULCO\n', 'acapulco\n', 'acapulco!\n', 'ACAPULCO!!\n', 'acapulco!!\n', 'acapulco#\n', 'ACAPULCO##\n', 'acapulco##\n', 'ACAPULCO2020\n', 'acapulco2020\n', 'ACAPULCO2021\n', 'acapulco2021\n', 'ACAPULCO2022\n', 'acapulco2022\n', 'acapulco@\n', 'ACAPULCO@@\n', 'acapulco@@\n', 'c#rv#j$!\n', 'c#rv#j$!!\n', 'c#rv#j$#\n', 'c#rv#j$##\n', 'c#rv#j$@\n', 'c#rv#j$@@\n', 'CERVEJA\n', 'cerveja\n', 'cerveja!\n', 'CERVEJA!!\n', 'cerveja!!\n', 'cerveja#\n', 'CERVEJA##\n', 'cerveja##\n', 'CERVEJA2020\n', 'cerveja2020\n', 'CERVEJA2021\n', 'cerveja2021\n', 'CERVEJA2022\n', 'cerveja2022\n', 'cerveja@\n', 'CERVEJA@@\n', 'cerveja@@\n']
