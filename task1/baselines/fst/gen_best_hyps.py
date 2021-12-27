def find_best_run(l, num_runs, checkpoint_prefix):
    from numpy import mean, std
    best_cer = 200
    best_run = None
    for ngram in range(3, 10):
        cers, wers = get_wers_cers(l, ngram, num_runs, 'dev', checkpoint_prefix)
        cer_mean = mean(cers)
        if best_cer > cer_mean:
            best_cer = cer_mean
            best_run = ngram
    return best_run

def get_er(fname):
    with open(fname) as fh:
        lines = [_.strip().split('\t') for _ in fh]
    return float(lines[0][1]), float(lines[1][1])

def get_wers_cers(l, ngram, num_runs, split, checkpoint_prefix):
    wers, cers = [], []
    for run in range(num_runs):
        try:
            dev_fname = f'{checkpoint_prefix}/{l}-{ngram}-{split}.type.{run}.inv.weighted.unweighted.res'
            wer, cer = get_er(dev_fname)
        except Exception as e:
            dev_fname = f'{checkpoint_prefix}/{l}-{ngram}-{split}.{run}.inv.weighted.unweighted.res'
            wer, cer = get_er(dev_fname)
        wers.append(wer)
        cers.append(cer)
    return cers, wers

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--checkpoint-prefix')
    parser.add_argument('--language')
    args = parser.parse_args()

    num_runs = 5
    best_run = find_best_run(args.language, num_runs, args.checkpoint_prefix)
    print(best_run)

if __name__ == '__main__':
    main()