@echo off
setlocal

if not exist .venv (
  python -m venv .venv
)

set PYEXE=.venv\Scripts\python.exe

%PYEXE% -m pip install -r requirements.txt
%PYEXE% -m pip install -e ".[dev,ml]"
%PYEXE% -m main
