#!/usr/bin/python
# coding: utf-8
# © Jan-Philipp Kappmeier

""" Combines a tex file hierarchy into a single document file for arXiv.

The root tex file is read and all files included using '\input' tex commands are inserted recursively.

During the process, all comments are stripped in a way that lines ending with comments continue to
end with '%'. Comment only lines are completely removed. The source code is cleaned such that it does
not contain consecutive blank lines.

Usage: arxify.py base_dir root_doc out_file

Example: The call

    $ ./arxify.py ./doc/ document.tex ./doc/document-arxiv.tex
    
    converts the document contained in document.tex in the subfolder doc/ into a single document called
    document-arxiv.tex in the same subfolder.
"""

import sys

if len(sys.argv) < 3:
  print "Missing parameter!\n"
  exit(1)

baseDir = sys.argv[1]
baseFile = sys.argv[2]
out = sys.argv[3]

if not baseDir.endswith('/'):
  baseDir = baseDir + '/'

# takes a line that is read
# removes a comment part, if any
# if line starts with coment, nothing is returned
# empty lines are returned as empty line
def convertLineToArxiv(line):
  """ Convert a line of tex code to be used in arXiv publication.
  
  Strips away comments, but a last '%' is remained on comment lines.
  
  Args:
    line(str):  A line in the tex source code.
  
  Returns:
    The stripped input without comment.
  """
  stripped = line.strip()
  if not stripped: return "\n"
  index = commentIndex(stripped) + 1 # lines ending with comment should continue to end with it
  beforeComment = stripped[:index];
  return beforeComment + "\n" if beforeComment and beforeComment != "%" else ""

def commentIndex(line):
  """Return the starting index of a comment for a given line of tex code.
  
  Comments are considered to start with the character '%'. However, the symbol
  appears as '\%', where it is ignored.

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
  
def fileNameFromInput(command):
  """Return path and file name of a tex input command
  
  Include commands look like '\input{path/to/filename}'. The value is assumed to
  be placed between the first pair of opening and closing curly braces.

  Args:
    command (str): The tex command, and maybe some additional text as long as no '{' occur beforeComment
      the input command.

    Returns: The text between opening and closing braces.
  """
  openIndex = command.index("{")
  endIndex = command.index("}")
  return command[openIndex+1:endIndex]

# File is a file that is to be read
# outFile is an open file handle that can be used to append text
def readFromFile(inputFile, outFile, lastEmpty = False):
  """Write contents of a given file with removed tex commands.
  
  Opens the given input file, parses it line by line, and appends lines containing text
  to the output file. For each line, comments are stripped, but lines ending with a comment
  continue to end with the comment character '%'.
  
  Consecutive empty lines are removed, lines only consisting of a comment are considered
  to be empty.
  
  If another file is included using the '\input' tex command, the command is replaced by the
  content of the file. The replacing of inputs happens recursiveley. For this method to work,
  the '\input' commands must appear as a single latex command on a line, maybe preceeded or
  followed by whitespace or comments. All file paths are assumed to be relative to the base
  directory.
  
  Args:
    inputFile (str): The (tex) file to be parsed
    outFile (file): The file handle used to append contents of the input file.
    lastEmpty: Specifies, if the last line written to the output file was whitespace.
  
  """
  with open( inputFile, "r" ) as sourceFile:
    for line in sourceFile:
      converted = convertLineToArxiv( line )
      if not converted.strip():
	if lastEmpty:
	  converted = ""
	else:
	  lastEmpty = True
      else:
	lastEmpty = False      
      print converted
      if converted.strip().startswith(r"\input"):
	print "Read file " + fileNameFromInput(converted)
	lastEmpty = readFromFile(baseDir + fileNameFromInput(converted) + ".tex", outFile, lastEmpty )
      else:
	outFile.write(converted)
  return lastEmpty

with open( out, "w" ) as targetFile:
  readFromFile(baseDir + baseFile, targetFile )
