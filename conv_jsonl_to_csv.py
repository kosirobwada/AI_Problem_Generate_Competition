import pandas as pd

import argparse

def main(args):
    df = pd.read_json(args.input_file, orient="records", lines=True)
    print(df)

    df.columns = ['theme', 'question', 'answer', 'reference']
    df.to_csv(args.output_file,  index=None, encoding='utf_8_sig')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file",
                        type=str)
    parser.add_argument("output_file",
                        type=str)
    args = parser.parse_args()
    main(args)
    