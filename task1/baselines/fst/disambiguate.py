#!/usr/bin/env python

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('f')
    parser.add_argument('--shuffle', action='store_true')
    parser.add_argument('--seed', default=42, type=int)
    parser.add_argument('--output', default='./output.tsv')
    args = parser.parse_args()
    buffer = []
    with open(args.f) as fh:
        for l in fh:
            splitted = l.split('\t')
            assert len(splitted) == 3
            times = int(splitted[2])
            for _ in range(times):
                buffer.append(f'{splitted[0]}\t{splitted[1]}\n')
    if args.shuffle:
        import numpy as np
        rng = np.random.default_rng(args.seed)
        rng.shuffle(buffer)

    with open(args.output, mode='w') as fh:
        for l in buffer:
            fh.write(l)

if __name__ == '__main__':
    main()