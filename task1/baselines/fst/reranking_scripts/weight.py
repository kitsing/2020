#!/usr/bin/env python
"""Weights input-output pairs under a given FST.

This script assumes that each input-output pair appears per line, separated by tab"""

import argparse
import functools
import logging
import multiprocessing

from typing import Iterator, Tuple, List

import pynini
from pynini.lib import rewrite


TOKEN_TYPES = ["byte", "utf8"]

def _reader(path: str) -> Iterator[str]:
    """Reads strings from a single-column filepath."""
    from tqdm import tqdm
    with open(path, "r") as source:
        for line in tqdm(source):
            yield line.strip().split('\t')


def main(args: argparse.Namespace) -> None:
    fst = pynini.Fst.read(args.fst_path)
    if args.invert:
        from sys import stderr
        print('inverting', file=stderr)
        fst.invert()
        print('inverted', file=stderr)
    input_token_type = (
        args.input_token_type
        if args.input_token_type in TOKEN_TYPES
        else pynini.SymbolTable.read_text(args.input_token_type)
    )
    output_token_type = (
        args.output_token_type
        if args.output_token_type in TOKEN_TYPES
        else pynini.SymbolTable.read_text(args.output_token_type)
    )
    logging.log(logging.INFO, f'input token type: {input_token_type}\t output token type: {output_token_type}')

    sum_fst = pynini.arcmap(fst, map_type='to_log')

    jobs = []
    pool = multiprocessing.Pool(args.cores)
    for l_idx, line in enumerate(_reader(args.input_path)):
        inp, out = line
        jobs.append(pool.apply_async(compute_Z, (inp, input_token_type, out, output_token_type, sum_fst)))
    pool.close()
    pool.join()
    results = [_.get() for _ in jobs]
    with open(args.output_path, mode='w') as w_fh:
        for r in results:
            w_fh.write(f'{r}\n')


def compute_Z(inp, input_token_type, out, output_token_type, sum_fst):
    with pynini.default_token_type(input_token_type):
        m = pynini.compose(inp, sum_fst)
    with pynini.default_token_type(output_token_type):
        m = pynini.compose(m, out)
    partition_function = pynini.shortestdistance(m, reverse=True)[m.start()]
    return partition_function


if __name__ == "__main__":
    logging.basicConfig(level="INFO", format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-path", required=True, help="path to file of i-o pairs to rerank"
    )
    parser.add_argument(
        "--output-path", required=True, help="output path"
    )
    parser.add_argument(
        "--fst-path", required=True, help="FST path"
    )
    parser.add_argument('--invert', action='store_true')
    parser.add_argument(
        "--cores",
        type=int,
        default=multiprocessing.cpu_count(),
        help="number of cores (default: %(default)s)",
    )
    parser.add_argument(
        "--input-token-type", default="utf8", help="input_token type"
    )
    parser.add_argument(
        "--output-token-type", default="utf8", help="output_token type"
    )
    main(parser.parse_args())
