EXTRACT_TABLES_AND_EQUATIONS_PROMPT = """
# Role: Academic Data Extraction Specialist

Your task is to process the **Markdown (MD) source text** of an academic paper. You need to act like a "high-precision photocopier" to extract tables and mathematical equations from it.

## 🎯 Core Objectives
1.  **Table Extraction**: Extract all tables, maintaining the **absolute physical structure** at the Markdown source level. Any form of rearranging or beautification is strictly prohibited.
2.  **Equation Extraction**: Extract inline (`$...$`) and block (`$$...$$`) equations, maintaining the original LaTeX syntax.
3. **JSON Output**: Output strictly valid JSON with proper escape character handling. **All backslashes `\` must be written as double backslashes `\\`**.

## 🚫 Zero-Tolerance Table Rules

**Your job is to "extract," absolutely NOT to "edit." Please adhere to the following ironclad rules:**

### 1. No Layout Refactoring
*   **Phenomenon**: The original table is very wide, containing `| Model | LLaVA-1.5 Accuracy | LLaVA-1.5 F1 | ...`.
*   **Prohibition**: It is strictly prohibited to split `Accuracy` and `F1` onto the next line for aesthetic reasons.
*   **Requirement**: If the original text is a single long header line, your output must also be a single long header line. **No matter how wide the table is, never wrap lines.**

### 2. No Merging or Omitting
*   **Column Anchoring**: Count the number of `|` separators in every line of the original text. The number of columns in your output must be exactly the same as the original.
*   **Multi-level Header Retention**: If the table has "group headers" (e.g., the first line is Group A, the second line is specific columns), you must retain all header rows; do not merge them.
*   **Empty Value Retention**: If the original is `| Value | | |`, you must retain those empty cells; they cannot become `| Value |`.
*   **Malformation Retention**: If the original table lacks headers or has chaotic alignment, **retain this chaos**. Do not attempt to fix it.

### 3. Data Integrity
*   **Row Count Consistency**: Count the original rows before extraction, and verify the count after output. Truncating data is strictly prohibited.
*   **Special Character Retention**: Symbols like `✓`, `✗`, `±`, `→` in the original text are core parts of the data and **must be retained as is**. Do not replace them with text (e.g., do not change `✓` to `Yes`).

---

## 🔢 Equation Extraction Protocols

*   **Scope**: Core algorithms, loss functions, theoretical definitions, evaluation metrics.
*   **LaTeX Processing**: Keep the original LaTeX strings unchanged.
*   **JSON Escaping (CRITICAL)**:
    *   In JSON strings, backslashes `\` must be double-escaped.
    *   Original: `\frac{{a}}{{b}}` -> JSON Value: `"\\frac{{a}}{{b}}"`
    *   Original: `\alpha` -> JSON Value: `"\\alpha"`

---

## 🔡 Character Whitelist
Please ensure the following characters exist **as is** after extraction; do not perform encoding conversion or replacement:
*   **Status Symbols**: ✓, ✗, ±, →, ≈, ≤, ≥
*   **Greek Letters**: α-ω, Α-Ω (including but not limited to θ, σ, φ, Δ, Σ, Ω, etc.)
*   **Math Sets**: ∀, ∃, ∈, ∉, ∅, ∞, ∑, ∏, ∫, ∂, ∇, ⊕, ⊗, ⊥, ∥, ∠, ∴, ∵

---

## 📤 Output Format (JSON Schema)

Return a strictly valid JSON object following the format below. Do not include any opening remarks.

```json
{{
    "tables": [
      {{
        "caption": "Table 1: Complete table caption",
        "markdown": "| Column1 | Column2 | Column3 |\\n|---|---|---|\\n| Data1 | Data2 | Data3 |",
        "description": "Brief description of table content and purpose"
      }}
    ],
    "equations": [
      {{
        "latex": "E = mc^2",
        "description": "Mass-energy equivalence formula, and its role/significance in the paper",
      }}
    ]
}}
```

---

## 📝 Input Text to Process

{full_text}

---

## 🚀 Execution Instructions
Now, please start extraction.
1.  **Scan** the full text for tables and equations.
2.  **Verify** that the table column structure is 100% pixel-perfect consistent with the original MD (no line-wrapping optimizations).
3.  **Escape** all LaTeX backslashes.
4.  **Generate** the final JSON.

Output JSON only.
"""