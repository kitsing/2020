#!/usr/bin/env python

def main():
    from argparse import ArgumentParser
    from glob import glob
    parser = ArgumentParser()
    parser.add_argument('--input-path-prefix')
    parser.add_argument('--shuffle', action='store_true')
    parser.add_argument('--seed', default=42, type=int)
    parser.add_argument('--output-path-prefix', default='./')
    args = parser.parse_args()

    langids = {'bn', 'gu', 'hi', 'kn', 'ml', 'mr', 'pa', 'sd', 'si', 'ta', 'te', 'ur'}

    chunks = {'train', 'dev', 'test'}

    for lang in langids:
        for chunk in chunks:
            fname = f'{args.input_path_prefix}/{lang}/lexicons/{lang}.translit.sampled.{chunk}.tsv'
            output_fname = f'{args.output_path_prefix}/{chunk}/{lang}_{chunk}.tsv'
            buffer = []
            with open(fname) as fh:
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

            with open(output_fname, mode='w') as fh:
                for l in buffer:
                    fh.write(l)

if __name__ == '__main__':
    main()