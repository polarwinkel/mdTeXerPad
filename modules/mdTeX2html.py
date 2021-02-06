#!/usr/bin/python3
'''
This will convert Markdown with included LaTeX-equations to HTML.
The Formulas will be in MathML-Format.

block-equations need to start with $$ or \[
inline-equations start with \( or $
'''

from latex2mathml.converter import convert as tex2mathml
from markdown import markdown as md2html
import re

def convert(mdtex):
    ''' converts recursively the mdTeX-mixture to HTML with MathML '''
    found = False
    # find first $$-formula:
    parts = re.split('\${2}', mdtex)
    if len(parts)>1:
        found = True
        result = convert(parts[0])+'\n'
        result += tex2mathml(parts[1])+'\n'
        result += convert('$$'.join(parts[2:]))
    #else find first $-formulas:
    else:
        parts = re.split('\${1}', mdtex)
    if len(parts)>1 and not found:
        found = True
        result = convert(parts[0]+tex2mathml(parts[1])+'$'.join(parts[2:]))
    # convert text recursively and formulas right away:
    if not found:
        # no more formulas found
        result = md2html(mdtex)
    # TODO: parse for \[ for newline and \( for inline-equations as well
    # support for numbered or aligned equations is not planned at the moment
    return result
