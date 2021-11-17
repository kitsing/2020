#!/usr/bin/env python

def get_er(fname):
    with open(fname) as fh:
        lines = [_.strip().split('\t') for _ in fh]
    return float(lines[0][1]), float(lines[1][1])

def main():
    from numpy import mean, std
    languages = {'bn','gu','hi','kn','ml','mr','pa','sd','si','ta','te','ur'}
    num_runs = 5

    for l in languages:
        best_cer = 200
        best_run = None
        for ngram in range(3, 10):
            cers, wers = get_wers_cers(l, ngram, num_runs, 'dev')
            cer_mean = mean(cers)
            if best_cer > cer_mean:
                best_cer = cer_mean
                best_run = ngram
        cers_dev, wers_dev = get_wers_cers(l, best_run, num_runs, 'dev')
        cers_test, wers_test = get_wers_cers(l, best_run, num_runs, 'test')

        print(f'{l}\tdev wer mean: {mean(wers_dev)} std: {std(wers_dev)}\ttest wer mean: {mean(wers_test)} std: {std(wers_test)}')


def get_wers_cers(l, ngram, num_runs, split):
    wers, cers = [], []
    for run in range(num_runs):
        dev_fname = f'{l}-{ngram}-{split}.type.{run}.inv.res'
        wer, cer = get_er(dev_fname)
        wers.append(wer)
        cers.append(cer)
    return cers, wers


if __name__ == '__main__':
    main()
