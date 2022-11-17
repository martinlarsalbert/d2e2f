import re
import os
import logging
import shutil
import yaml
import subprocess

with open("_config.yml") as f:
    config = yaml.safe_load(f)

file_path = os.path.join(
    r"_build/latex", config["latex"]["latex_documents"]["targetname"]
)

## Open
with open(file_path, mode="r", encoding="cp1252") as file:
    s = file.read()

## Fix documentclass:
result = re.search(r"\\documentclass.*{(.+)}", s)
replacement = re.sub(result.group(1), r"article", result.group(0))
s = s.replace(result.group(0), replacement)

## Adding float barrier to keep figures within the section
s = s.replace(r"\subsection", r"\FloatBarrier\subsection")
s = s.replace(r"\section", r"\FloatBarrier\section")

## Adding page break for sections
s = s.replace(r"\section", r"\clearpage\section")

## Save
with open(file_path, mode="w") as file:
    file.write(s)

subprocess.check_call(
    ["xelatex", config["latex"]["latex_documents"]["targetname"]], cwd="_build/latex"
)

# Open PDF
subprocess.Popen(
    [config["latex"]["latex_documents"]["targetname"].replace("tex", "pdf")],
    cwd="_build/latex",
    shell=True,
)
