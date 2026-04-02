import re
import logging
from typing import List

logger = logging.getLogger(__name__)

# 特殊字符映射表：Unicode字符 -> LaTeX命令
UNICODE_TO_LATEX_MAP = {
    # 希腊字母（小写）
    'α': r'$\alpha$',
    'β': r'$\beta$',
    'γ': r'$\gamma$',
    'δ': r'$\delta$',
    'ε': r'$\varepsilon$',
    'ζ': r'$\zeta$',
    'η': r'$\eta$',
    'θ': r'$\theta$',
    'ι': r'$\iota$',
    'κ': r'$\kappa$',
    'λ': r'$\lambda$',
    'μ': r'$\mu$',
    'ν': r'$\nu$',
    'ξ': r'$\xi$',
    'ο': r'$o$',
    'π': r'$\pi$',
    'ρ': r'$\rho$',
    'σ': r'$\sigma$',
    'τ': r'$\tau$',
    'υ': r'$\upsilon$',
    'φ': r'$\phi$',
    'χ': r'$\chi$',
    'ψ': r'$\psi$',
    'ω': r'$\omega$',

    # 希腊字母（大写）
    'Α': r'$A$',
    'Β': r'$B$',
    'Γ': r'$\Gamma$',
    'Δ': r'$\Delta$',
    'Ε': r'$E$',
    'Ζ': r'$Z$',
    'Η': r'$H$',
    'Θ': r'$\Theta$',
    'Ι': r'$I$',
    'Κ': r'$K$',
    'Λ': r'$\Lambda$',
    'Μ': r'$M$',
    'Ν': r'$N$',
    'Ξ': r'$\Xi$',
    'Ο': r'$O$',
    'Π': r'$\Pi$',
    'Ρ': r'$P$',
    'Σ': r'$\Sigma$',
    'Τ': r'$T$',
    'Υ': r'$\Upsilon$',
    'Φ': r'$\Phi$',
    'Χ': r'$X$',
    'Ψ': r'$\Psi$',
    'Ω': r'$\Omega$',

    # 常用符号
    '✓': r'$\checkmark$',
    '✗': r'$\times$',
    '✘': r'$\times$',
    '×': r'$\times$',
    '±': r'$\pm$',
    '∓': r'$\mp$',
    '≈': r'$\approx$',
    '≠': r'$\neq$',
    '≤': r'$\leq$',
    '≥': r'$\geq$',
    '≪': r'$\ll$',
    '≫': r'$\gg$',
    '→': r'$\rightarrow$',
    '←': r'$\leftarrow$',
    '↑': r'$\uparrow$',
    '↓': r'$\downarrow$',
    '↔': r'$\leftrightarrow$',
    '⇒': r'$\Rightarrow$',
    '⇐': r'$\Leftarrow$',
    '⇔': r'$\Leftrightarrow$',

    # 数学符号
    '∞': r'$\infty$',
    '∑': r'$\sum$',
    '∏': r'$\prod$',
    '∫': r'$\int$',
    '∂': r'$\partial$',
    '∇': r'$\nabla$',
    '∀': r'$\forall$',
    '∃': r'$\exists$',
    '∈': r'$\in$',
    '∉': r'$\notin$',
    '∅': r'$\emptyset$',
    '⊂': r'$\subset$',
    '⊃': r'$\supset$',
    '⊆': r'$\subseteq$',
    '⊇': r'$\supseteq$',
    '∪': r'$\cup$',
    '∩': r'$\cap$',
    '⊕': r'$\oplus$',
    '⊗': r'$\otimes$',
    '⊥': r'$\perp$',
    '∥': r'$\parallel$',
    '∠': r'$\angle$',
    '∴': r'$\therefore$',
    '∵': r'$\because$',

    # 上下标符号
    '⁰': r'$^0$',
    '¹': r'$^1$',
    '²': r'$^2$',
    '³': r'$^3$',
    '⁴': r'$^4$',
    '⁵': r'$^5$',
    '⁶': r'$^6$',
    '⁷': r'$^7$',
    '⁸': r'$^8$',
    '⁹': r'$^9$',

    # 其他常用符号
    '°': r'$^\circ$',
    '‰': r'$\permille$',
    '…': r'$\ldots$',
    '–': r'--',
    '—': r'---',
    '\u2018': r"'",   # 左单引号
    '\u2019': r"'",   # 右单引号
    '\u201c': r'``',  # 左双引号
    '\u201d': r"''",  # 右双引号
}


def preprocess_content_for_llm(content: str) -> str:
    """在送入 LLM 之前预处理内容，用占位符保护特殊字符。"""
    protected_content = content

    for greek_char in ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']:
        if greek_char in protected_content:
            protected_content = protected_content.replace(greek_char, f"[GREEK:{greek_char}]")

    symbol_map = {'✓': '[CHECKMARK]', '✗': '[XMARK]', '×': '[TIMES]'}
    for symbol, placeholder in symbol_map.items():
        if symbol in protected_content:
            protected_content = protected_content.replace(symbol, placeholder)

    return protected_content


def postprocess_content_from_llm(content: str) -> str:
    """处理 LLM 返回的内容，恢复特殊字符占位符。"""
    restored_content = content

    greek_pattern = r'\[GREEK:([αβγδεζηθικλμνξοπρστυφχψω])\]'
    restored_content = re.sub(greek_pattern, lambda m: m.group(1), restored_content)

    symbol_restore_map = {'[CHECKMARK]': '✓', '[XMARK]': '✗', '[TIMES]': '×'}
    for placeholder, symbol in symbol_restore_map.items():
        restored_content = restored_content.replace(placeholder, symbol)

    return restored_content


def validate_special_chars_in_output(original_text: str, processed_text: str) -> List[str]:
    """验证处理后的文本是否保留了原文的特殊字符（考虑 LaTeX 转换）。"""
    original_special_chars = set()
    truly_lost_chars = []

    for char in UNICODE_TO_LATEX_MAP:
        if char in original_text:
            original_special_chars.add(char)

    for char in original_special_chars:
        latex_equivalent = UNICODE_TO_LATEX_MAP[char]
        if char not in processed_text and latex_equivalent not in processed_text:
            truly_lost_chars.append(char)

    if truly_lost_chars:
        logger.warning(f"Validation found missing special characters in output: {truly_lost_chars}")

    return truly_lost_chars
