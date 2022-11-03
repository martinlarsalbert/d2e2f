@ECHO OFF

jb build . --builder latex
::jb build . --all --builder latex

python latex_fixes.py
