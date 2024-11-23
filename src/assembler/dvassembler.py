from assembler.assembler import assemble
from assembler.grammar import process
from argparse import ArgumentParser


def main():
    parser = ArgumentParser("CS147 Assembler")
    parser.add_argument("INPUT_FILE", type=str)
    args = parser.parse_args()
    contents = open(args.INPUT_FILE).read()
    statements = process(contents)
    output = assemble(statements)
    print(output)
