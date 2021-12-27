#!/usr/bin/env python
"""Rewrites FST examples.

This script assumes the input is provided one example per line."""

__author__ = "Kyle Gorman"

import argparse
import functools
import logging
import multiprocessing

from typing import Iterator, Tuple, List

import pynini
from pynini.lib import rewrite


TOKEN_TYPES = ["byte", "utf8"]


class Rewriter:
    def __init__(
        self,
        fst: pynini.Fst,
        input_token_type: pynini.TokenType,
        output_token_type: pynini.TokenType,
        nshortest: int = 10,
    ):


        self.top_k_rewrite = functools.partial(
            rewrite.top_rewrites,
            rule=fst,
            input_token_type=input_token_type,
            output_token_type=output_token_type,
            nshortest=nshortest,
        )

    def __call__(self, i: str) -> List[str]:
        try:
            return self.top_k_rewrite(i)
        except rewrite.Error:
            return ["<composition failure>",]


def _reader(path: str) -> Iterator[str]:
    """Reads strings from a single-column filepath."""
    from tqdm import tqdm
    with open(path, "r") as source:
        for line in tqdm(source):
            yield line.rstrip()


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
    from sys import stderr
    print(f'{input_token_type}\t{output_token_type}', file=stderr)

    rewriter = Rewriter(
        fst,
        input_token_type=input_token_type,
        output_token_type=output_token_type,
        nshortest=args.n,
    )
    jobs = []
    pool = multiprocessing.Pool(args.cores)
    # sum_fst.set_output_symbols(output_token_type)
    for line in _reader(args.input_path):
        jobs.append(pool.apply_async(rewriter, (line,)))
    pool.close()
    pool.join()
    with open(args.output_path, mode='w') as w_fh:
        for line, hyps in zip(_reader(args.input_path), jobs):
            for hyp in hyps.get():
                w_fh.write(f'{line}\t{hyp}\n')

if __name__ == "__main__":
    logging.basicConfig(level="INFO", format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-path", required=True, help="path to file of words to rewrite"
    )
    parser.add_argument('--n', default=10, type=int)
    parser.add_argument(
        "--output-path", required=True, help="path to rewrite fst FST"
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
