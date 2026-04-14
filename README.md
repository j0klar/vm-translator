# vm-translator

A VM translator for the Hack virtual machine written in Python, built as part of the [Nand2Tetris](https://www.nand2tetris.org/) course (Projects 7 & 8).

Translates `.vm` files written in the Hack VM language into `.asm` Hack assembly files. Supports both single-file and multi-file (directory) translation, including bootstrap code and the complete set of VM commands.

## Usage

```bash
python translator.py <file.vm>        # single file
python translator.py <directory>      # directory of .vm files
```

The output `.asm` file will be created in the same directory as the input.

## Examples

```bash
python translator.py FibonacciElement   # produces FibonacciElement.asm
```

## Supported Commands

**Memory access:** `push`, `pop` - segments: `constant`, `local`, `argument`, `this`, `that`, `temp`, `pointer`, `static`

**Arithmetic-logical:** `add`, `sub`, `neg`, `eq`, `gt`, `lt`, `and`, `or`, `not`

**Branching:** `label`, `goto`, `if-goto`

**Functions:** `function`, `call`, `return`

## Project Structure

```
vm-translator/
├── translator.py     # Main entry point
├── code_writer.py    # Translates VM commands to Hack assembly
├── parser.py         # Parses .vm files into commands
└── examples
        
```