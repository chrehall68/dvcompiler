# CS147 DaVinci Compiler

This repository contains an assembler for the CS147 DaVinci instruction set.

Simply install the package by running `pip install .`, then you can use the assembler as follows:

```sh
dvassembler /path/to/assembly.asm
```

Output will be generated into standard out. You can redirect it into a file as follows:

```sh
dvassembler /path/to/assembly.asm > my_memdump.dat
```

## Example

You can find examples of programs written in the CS147 DaVinci assembly language in
the `examples` directory. You'll notice some differences
with this version of assembly compared to MIPS assembly. For one,
you must have a label `main` for code that is to be executed upon program load. You **must** define any functions
your program needs before defining main. If you don't, the code will still get assembled, but the processor will fall off of main and
start executing any functions defined after it.

Another difference is that the data segment only supports full words. Thus, we don't support any data specifiers like
`byte` or `half`. To add data, simply label the data and provide the list of words, which must be literals.

One last difference is that each instruction must end with a semicolon,
and arguments must be comma separated, otherwise the assembler will error.
