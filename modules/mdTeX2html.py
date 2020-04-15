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
        try:
            result += '<div class="blockformula">'+tex2mathml(parts[1])+'</div>\n'
        except:
            result += '<div class="blockformula"><font color="red">ERROR converting TeX2mathml</font></div>'
        try:
            result += convert('$$'.join(parts[2:]))
        except:
            result += '<div class="blockformula"><font color="red">ERROR: formula incomplete?</font></div>'
    #else find first $-formulas:
    else:
        parts = re.split('\${1}', mdtex)
    if len(parts)>1 and not found:
        found = True
        try:
            mathml = tex2mathml(parts[1])
        except:
            mathml = '<font color="red">ERROR converting TeX2mathml</font>'
        if len(parts)>2:
            result = convert(parts[0]+mathml+'$'.join(parts[2:]))
        else:
            result = convert(parts[0]+mathml+'<font color="red">ERROR: formula incomplete</font>')
    # convert text recursively and formulas right away:
    if not found:
        # no more formulas found
        result = md2html(mdtex)
    # TODO: parse for \[ for newline and \( for inline-equations as well
    # support for numbered or aligned equations is not planned at the moment
    return result
