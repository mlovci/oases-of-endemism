# Contributing Guidelines

Thank you for contributing to the **Oases of Endemism** data processing workspace. To maintain high standards of data integrity and code organization, please follow these guidelines when adding, modifying, or verifying data conversion pipelines.

---

## 1. Directory Structure and Organization

Keep the workspace clean and well-structured. Each data table or file processing pipeline should follow this layout:

```text
Oases of Endemism/
├── Data_Table_S5.docx          # Source data files (Word format)
├── Data_Table_S5.xlsx          # Generated output files (Excel format)
├── convert.py                  # Python conversion script(s)
├── requirements.txt            # Python dependencies
├── methods.md                  # Detailed methodology and conversion logic
├── CONTRIBUTING.md             # This file (organization guidelines)
└── venv/                       # Local Python virtual environment (ignored by Git)
```

### File Naming Conventions
- **Source Files**: Use the original publication names (e.g., `Data_Table_S[X].docx`).
- **Converted Files**: Use matching names with appropriate extensions (e.g., `Data_Table_S[X].xlsx`).
- **Scripts**: Keep conversion scripts self-contained and descriptive (e.g., `convert.py` or `convert_table_s5.py`).

---

## 2. Python Coding Standards

To ensure scripts remain readable, maintainable, and robust, adhere to the following standards:

### Development Setup
Always run scripts within a dedicated virtual environment using Python 3.10+:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Style & Formatting
- **Standard Formatting**: Write PEP 8 compliant code. Use 4-space indentation.
- **Explicit Type Casting**: Avoid storing numerical values as text in Excel. Write robust parsers that dynamically attempt to cast values to `int` or `float` using regular expressions.
- **Graceful Error Handling**: Do not let scripts crash on individual corrupted cells. Implement safe conversion helpers that fall back to raw text and log a warning if parsing fails.
- **Comments and Docstrings**: Write descriptive docstrings for all functions, documenting arguments, return types, and exceptions.

---

## 3. Documentation Requirements

Every conversion pipeline must have a matching documentation section in `methods.md` before it is published or integrated. The documentation must detail:
1. **Pipeline Architecture**: A high-level description of libraries used and execution flow.
2. **Data Cleaning Rules**: Explicit rules applied (e.g., stripping whitespace, removing non-breaking spaces `\xa0`, handling empty or missing cells).
3. **Type-Casting Rules**: Which columns or fields are cast to which types, and how exceptions are handled.
4. **Visual Layout Treatment**: Specific styles applied in Excel (fonts, colors, borders, headers, alignments).

---

## 4. Verification and Quality Assurance

Before pushing changes or submitting outputs:
1. **Check Dimensions**: Verify that row and column counts in the generated `.xlsx` match the source document exactly.
2. **Inspect Cell Types**: Run a verification check to ensure cells intended to hold numeric data actually hold numeric types (`int` or `float`) and not string representations of numbers.
3. **Review Column Widths**: Ensure all column dimensions are adjusted dynamically so that headers and contents are fully readable and do not trigger `###` overflow issues.
4. **Verify Alignment**: Ensure numbers are right-aligned, text is left-aligned, and headers are centered.
