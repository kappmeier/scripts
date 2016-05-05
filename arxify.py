#!/usr/env/python3
# coding: utf-8
# © Jan-Philipp Kappmeier

r""" Combines a tex file hierarchy into a single document file for arXiv.

The root tex file is read and all files included using '\input' tex commands are
inserted recursively.

During the process, all comments are stripped in a way that lines ending with
comments continue to end with '%'. Comment only lines are completely removed.
The source code is cleaned such that it does not contain consecutive blank
lines.

Usage: arxify.py base_dir root_doc out_file

Example: The call

    $ ./arxify.py ./doc/ document.tex ./doc/document-arxiv.tex

    converts the document contained in document.tex in the subfolder doc/ into a
    single document called document-arxiv.tex in the same subfolder.
"""

import os
import sys

def parse_opions():
    """Parses the input directory and file and the output parameters.
    """
    if len(sys.argv) < 3:
        print("Missing parameter!\n")
        exit(1)

    base_dir = sys.argv[1]
    base_file = sys.argv[2]
    out_file = sys.argv[3]
    verbose = True if len(sys.argv) > 4 and sys.argv[4] == 'v' else False

    if not base_dir.endswith('/'):
        base_dir = base_dir + '/'

    return (base_dir, base_file, out_file, verbose)

# takes a line that is read
# removes a comment part, if any
# if line starts with coment, nothing is returned
# empty lines are returned as empty line
def convert_line_to_arxiv(line):
    """ Convert a line of tex code to be used in arXiv publication.

    Strips away comments, but a last '%' is remained on comment lines.
    
    >>> convert_line_to_arxiv(r"\section{sec} % section 2")
    '\\\\section{sec} %'
    
    >>> convert_line_to_arxiv(r"\section{sec}")
    '\\\\section{sec}'
    
    >>> convert_line_to_arxiv(r"    \section{sec}    ")
    '\\\\section{sec}'
    
    >>> convert_line_to_arxiv("    ")
    ''

    >>> convert_line_to_arxiv("% comment only line")
    ''

    Args:
        line(str):    A line in the tex source code.

    Returns:
        The stripped input without comment.
    """
    stripped = line.strip()
    if not stripped:
        return ""
    index = comment_index(stripped) + 1 # lines ending with comment should continue to end with it
    before_comment = stripped[:index]
    return before_comment if before_comment and before_comment != "%" else ""

def comment_index(line):
    r"""Return the starting index of a comment for a given line of tex code.

    Comments are considered to start with the character '%'. However, the symbol
    appears as '\%', where it is ignored.

    >>> comment_index("\someCommand{param} more text %we do this because...")
    30
    
    >>> comment_index("some line contains a \% value %we do this because...")
    30

    >>> comment_index(r"new line andcomment \\% value")
    22

    >>> comment_index("without comment")
    15

    Args:
        line (str): The line.

    Returns: The first index of '%' used as a comment, line.len() if the line
        does not contain a comment.
    """
    # searching for '\%' is not feasible as '\' can be used in constructs like '\\%'
    # simple approach: strip all occurences of '\\' and afterwards of '\%'
    tmp = line.replace(r"\\", "@@")
    tmp = tmp.replace(r"\%", "@@") + "%"
    return tmp.index("%")

def file_name_from_input(command):
    r"""Return path and file name of a tex input command

    Include commands look like '\input{path/to/filename}'. The value is assumed
    to be placed between the first pair of opening and closing curly braces.

    >>> file_name_from_input("\input{path/to/filename}")
    'path/to/filename'
    
    also works if the input command line contains more text
    
    >>> file_name_from_input("  \input{path/to/filename} % include file")
    'path/to/filename'
    
    This fails
    >>> file_name_from_input("\section{sec} \input{path/to/filename}")
    'sec'

    Args:
        command (str): The tex command, and maybe some additional text as long
        as no '{' occur before the input command.

        Returns: The text between opening and closing braces.
    """
    open_index = command.index("{")
    end_index = command.index("}")
    return command[open_index+1:end_index]

def read_from_file(base_dir, input_file, out_file, last_empty=False, verbose=False):
    r"""Write contents of a given file with removed tex commands.

    Opens the given input file, parses it line by line, and appends lines
    containing text to the output file. For each line, comments are stripped,
    but lines ending with a comment continue to end with the comment
    character '%'.

    Consecutive empty lines are removed, lines only consisting of a comment are
    considered to be empty.

    If another file is included using the '\input' tex command, the command is
    replaced by the content of the file. The replacing of inputs happens
    recursiveley. For this method to work, the '\input' commands must appear as
    a single latex command on a line, maybe preceeded or followed by whitespace
    or comments. All file paths are assumed to be relative to the base
    directory.

    Args:
        input_file (str): The (tex) file to be parsed
        out_file (file): The file handle used to append contents of the input
                         file.
        last_empty: Specifies, if the last line written to the output file was
                    whitespace.
    """
    with open(base_dir + input_file, "r") as source_file:
        line_number = 0
        for line in source_file:
            line_number += 1
            converted = convert_line_to_arxiv(line)
            if not converted.strip():
                if last_empty:
                    converted = ""
                else:
                    last_empty = True
            else:
                last_empty = False
            if verbose:
                print(converted)
            if converted.strip().startswith(r"\input"):
                print("Read file {}".format(file_name_from_input(converted)))
                file_name = get_include_file(base_dir, file_name_from_input(converted))
                if file_name is None:
                    print("Cannot include file from {}:{}. Stop.".format(base_dir + input_file, line_number),
                          file=sys.stderr)
                    sys.exit(1)
                last_empty = read_from_file(base_dir, file_name, out_file, last_empty)
            else:
                out_file.write(converted)
    return last_empty

def get_include_file(base_dir, include_name):
    """Checks whether an included file exists directly or with ending '.tex'.

    Args:
        include_name (str): the file to be included as in the tex document

        Returns: the name of the file to be included or None
    """
    file_name = include_name + ".tex"
    if os.path.isfile(base_dir + file_name):
        return file_name
    file_name = include_name
    return file_name if os.path.isfile(base_dir + file_name) else None

def main():
    """Executes the arxify script.
    """
    base_dir, base_file, out_file, verbose = parse_opions()
    with open(out_file, "w") as target_file:
        read_from_file(base_dir, base_file, target_file, verbose=verbose)

if __name__ == '__main__':
    main()
