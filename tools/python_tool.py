"""
Module 13 — Python Tool.

A sandboxed-ish Python execution tool for calculations, table formatting,
report generation, and CSV processing (e.g. "Calculate employee
attendance percentage", "Create a summary table"). Uses LangChain's
PythonAstREPLTool with pandas pre-loaded.
"""
import io
import contextlib

import pandas as pd
from langchain_core.tools import tool
from langchain_experimental.tools.python.tool import PythonAstREPLTool

_repl = PythonAstREPLTool(locals={"pd": pd})


@tool("python_calculator", return_direct=False)
def python_calculator(code: str) -> str:
    """Execute Python code for calculations, building summary tables, or
    processing CSV data. `pandas` is pre-imported as `pd`. The code should
    end with an expression or print() statement so the result is visible.
    Example: 'attendance = 22/24*100; print(round(attendance, 2))'"""
    try:
        return str(_repl.run(code))
    except Exception as e:
        return f"Execution error: {e}"


@tool("csv_summary", return_direct=False)
def csv_summary(csv_path: str) -> str:
    """Read a CSV file from disk and return a quick statistical summary
    (row/column counts, dtypes, describe() output) useful for reports."""
    try:
        df = pd.read_csv(csv_path)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
            print(f"Columns: {list(df.columns)}")
            print(df.describe(include='all').to_string())
        return buf.getvalue()
    except Exception as e:
        return f"Could not read CSV: {e}"


PYTHON_TOOLS = [python_calculator, csv_summary]
