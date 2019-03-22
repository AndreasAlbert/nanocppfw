#!/usr/bin/env python
import sys
import PyBindings
import argparse

def get_input_files():
    nargs = len(sys.argv)

    if nargs==2 and sys.argv[1].endswith(".txt"):
        with open(sys.argv[1],"r") as f:
            files = [x.strip() for x in f.readlines()]
    elif nargs > 1:
        files = sys.argv[1:]
    else:
        files = []
        files.append("/home/albert/repos/nanocppfw/data/007E0986-34E9-9741-A447-957FF2F1982C.root");
        files.append("/home/albert/repos/nanocppfw/data/78341E3C-F2BD-A64E-95D6-550FCA8DDAD4.root");
        files.append("/home/albert/repos/nanocppfw/data/E4D76467-890E-E811-8523-FA163E3D9AF7.root");
    return files

def is_valid_dataset(dataset):
    forbidden = "\#|@;:'\"\',<.>/?"
    if any([x in dataset for x in forbidden]):
        return False
    return True


def parse_cli():
    parser = argparse.ArgumentParser(description='Runs HInv Analysis')
    parser.add_argument('files',type=str, nargs='+',
                        help='Input files to run over')
    parser.add_argument('--dataset', default=None, required=True, type=str,
                        help='Dataset name.')

    args = parser.parse_args()

    if not is_valid_dataset(args.dataset):
        raise ArgumentError("Invalid dataset encountered: '{}'.".format(args.dataset))

    return args


def main():
    # files = get_input_files()
    args = parse_cli()
    ana = PyBindings.HInvAnalyzer(args.files)
    ana.set_fixed_dataset(args.dataset)
    ana.run()

if __name__ == "__main__":
    main()