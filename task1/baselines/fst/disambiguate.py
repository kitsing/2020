#!/usr/bin/env python

def main():
    import os
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
            import os
            if not os.path.exists(f'{args.output_path_prefix}/{chunk}/'):
                os.makedirs(f'{args.output_path_prefix}/{chunk}/')
            fname = f'{args.input_path_prefix}/{lang}/lexicons/{lang}.translit.sampled.{chunk}.tsv'
            output_fname = f'{args.output_path_prefix}/{chunk}/{lang}_{chunk}.tsv'
            output_fname_unrepeated = f'{args.output_path_prefix}/{chunk}/{lang}_{chunk}.type.tsv'
            buffer = []
            unrepeated_buffer = []
            with open(fname) as fh:
                for l in fh:
                    splitted = l.split('\t')
                    assert len(splitted) == 3
                    times = int(splitted[2])
                    space_delimited_romanization = ' '.join(splitted[1])
                    to_append = f'{splitted[0]}\t{space_delimited_romanization}\n'
                    unrepeated_buffer.append(to_append)
                    for _ in range(times):
                        buffer.append(to_append)
            if args.shuffle:
                import numpy as np
                rng = np.random.default_rng(args.seed)
                rng.shuffle(buffer)

            with open(output_fname_unrepeated, mode='w') as t_fh:
                for l in unrepeated_buffer:
                    t_fh.write(l)

            with open(output_fname, mode='w') as fh:
                for l in buffer:
                    fh.write(l)

if __name__ == '__main__':
    main()
