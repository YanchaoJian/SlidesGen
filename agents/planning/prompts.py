MAIN_CONTENT_EXTRACTION = """
You are a distinguished academic content analysis expert and professional speech writer.
Your goal is to transform a content-rich academic paper into a logically clear and engaging presentation material library for subsequent use in generating specific slide pages.

Paper Text:
{text}

---

**Task I: Presentation Logic Reorganization (Core Narrative)**
Please analyze the paper text and reorganize the key information into a "Presentation Flow".
**Important Requirement**: The content must be detailed and specific, containing sufficient information so that subsequent steps can break it down into 3-5 specific Bullet Points per page. Do not write empty summaries.

Please strictly organize the content in the following logical order:

1. **Background Context (background_context)**:
   - Specific data or facts about the importance of the field.
   - Layman's explanation of core concepts.
   - Goal: Provide material for generating "Background Introduction" slides.

2. **Problem Motivation (problem_motivation)**:
   - Where specifically do existing methods (SOTA) fail?
   - The severity of the problem.
   - Goal: Provide material for generating "Problem Statement" slides.

3. **Solution Overview (solution_overview)**:
   - Intuitive description of core innovations.
   - Overall architecture or process of the method.
   - Goal: Provide material for generating "Method Overview" slides.

4. **Technical Approach (technical_approach)**:
   - Key algorithm steps, model details, mathematical principles.
   - Specific implementation strategies.
   - Goal: Provide material for generating "Technical Details" slides.

5. **Evidence and Proof (evidence_proof)**:
   - Experimental settings, datasets.
   - **Specific** performance improvement data (e.g., accuracy improved from 80% to 85%).
   - Goal: Provide material for generating "Experimental Results" slides.

6. **Impact and Significance (impact_significance)**:
   - Summary of conclusions.
   - Future work directions.
   - Goal: Provide material for generating "Summary and Outlook" slides.

---

**Task II: Asset Analysis & Mapping**
Analyze the provided chart metadata. To make the slides visually rich, you must determine which part of the presentation each chart is **best suited** for.

**Provided Assets:**
1. **Tables (Markdown)**: {tables_info}
2. **Equations (LaTeX)**: {equations_info}
3. **Figures (Metadata)**: {figures_info}

**Analysis Requirements:**
- **Tables**: Summarize core conclusions.
- **Equations**: Explain the specific role of the formula in the method.
- **Figures**: Explain the content of the figure.
**Recommended Section (Critical)**: **Must** select one of the most relevant sections from the 6 presentation logic parts above (e.g., `technical_approach` or `evidence_proof`) for subsequent automatic layout.

---

**Task III: Paper Metadata Extraction**
Extract basic paper information: Title, Authors, Affiliations, Abstract, Keywords, and Venue.
- **Venue**: The publication venue — conference name, journal name, workshop, or preprint server (e.g., "NeurIPS 2017", "Nature Machine Intelligence", "arXiv preprint"). If not explicitly stated in the text, infer from headers/footers/citation hints; if still unknown, return an empty string.
- **Affiliations**: Institutional affiliations of the authors. Preserve original ordering.
- These fields are critical because they will populate a dedicated Title Slide at the start of the presentation.

---

**Output Format**
Return a **SINGLE JSON OBJECT**. Do not use Markdown code blocks. Strictly follow this Schema:

```json
{{
  "paper_info": {{
    "title": "Paper Title",
    "authors": ["Author 1", "Author 2"],
    "affiliations": ["Institution 1", "Institution 2"],
    "abstract": "Abstract Content",
    "keywords": ["Keyword 1", "Keyword 2"],
    "venue": "Conference / Journal Name (e.g., NeurIPS 2017)"
  }},
  
  "presentation_flow": {{
    "background_context": "Detailed background introduction content...",
    "problem_motivation": "Problem description and existing limitations...",
    "solution_overview": "Core ideas of the solution...",
    "technical_approach": "Technical implementation details...",
    "evidence_proof": "Key experimental evidence...",
    "impact_significance": "Significance and outlook..."
  }},

  "equations": [
    {{
      "latex": "E = mc^2",
      "context": "Surrounding text that explains the equation in the paper",
      "analysis": "Analysis of formula's role",
      "recommended_section": "technical_approach"
    }}
  ],

  "tables": [
    {{
      "caption": "Table Title (English)",
      "markdown": "Original markdown",
      "analysis": "Table conclusion",
      "recommended_section": "evidence_proof"
    }}
  ],

  "figures": [
    {{
      "path": "Must match input exactly (e.g., path/to/img.png)",
      "caption": "Refined English Caption",
      "analysis": "Image content analysis",
      "recommended_section": "solution_overview" 
    }}
  ]
}}
```

**Key Matters**:
1. **Association**: Ensure the value of `recommended_section` strictly belongs to one of the 6 key names in `presentation_flow`.
2. **Path Matching**: The `path` field must match the input data exactly.
"""


SLIDES_PLANNING = """
# Role & Core Mission

You are a world-class academic presentation designer and educator. Your core mission is to transform a complex research paper into a clear, logically structured, and audience-friendly educational presentation.

- **Core Philosophy**: Your design should not be a simple restatement of the paper's content, but a carefully orchestrated process of knowledge transfer. You must guide the audience from the macroscopic background to the technical details, ultimately helping them understand the core value of the research.

---

# **Part Zero: Current Mission**

{refinement_instructions}

---

# **Part 1: Input Data**

### **1.1 Paper Basic Information**
- **Title**: {title}
- **Authors**: {authors}
- **Affiliations**: {affiliations}
- **Venue (Conference / Journal)**: {venue}
- **Abstract**: {abstract}

### **1.2 Paper Core Content (Presentation Flow)**
- **Background Context**: {background_context}
- **Problem Motivation**: {problem_motivation}
- **Solution Overview**: {solution_overview}
- **Technical Approach**: {technical_approach}
- **Evidence and Proof**: {evidence_proof}
- **Impact and Significance**: {impact_significance}

### **1.3 Paper Assets (Figures, Tables, Equations)**
- **Figure Information**: {figures_info}
- **Table Information**: {tables_info}
- **Equation Information**: {equations_info}

---

# **Part 2: Core Rules & Constraints**

### **2.1 Content & Narrative Rules**

- **PMRC Presentation Structure Framework (Strictly Follow)**
  - **Problem**: Why is this research important? What specific challenge needs to be addressed?
  - **Method**: How did we approach and solve this problem? What is innovative about our solution?
  - **Results**: What is the evidence that our method works? How significant are the improvements?
  - **Conclusion**: What is the impact of this work? Where do we go next?

- **Title Slide & Deduplication Rule**
  - **Mandatory Title Slide**: Slide 1 **must** be a dedicated Title Slide that presents the paper's title, authors, affiliations, and venue (conference/journal). This is a real slide entry in the JSON output (it is NOT auto-generated elsewhere).
  - **No Duplication After Slide 1**: Slides 2+ must **never** restate the paper title, author list, affiliations, or venue. Once shown on the title slide, that metadata is "consumed".
  - **Mandatory**: The first content slide (Slide 2) **must** be about the importance/background of the field, **not** the paper's metadata.

- **Content Redundancy Elimination Rule**
  - **No Repeated Concepts**: Each slide must present **unique** information.
  - **Progressive Disclosure**: Each slide should build upon the previous one, not repeat it.
  - **Mandatory Merge**: If two slides have overlapping content, merge them into one.
  - **Unique Value Principle**: Each slide must answer "What **new** information does this slide provide that previous slides did not?"

### **2.2 Slide Count & Layout Rules**

- **Adaptive Content Expansion Guide**
  - **Rich Multi-Contribution Papers**: 18-25+ slides.
  - **Standard Research Papers**: 12-18 slides.
  - **Short/Workshop Papers**: 8-12 slides.
  - **Survey/Review Papers**: 15-20+ slides.
  - **Expansion Metrics**: If the paper contains multiple novel components, extensive ablations, complex algorithms, expand with more slides.
  - **Quality over Compression**: It's better to explain clearly with more slides than to cram too much information into one.

- **Content Overflow Prevention Rule**
  - **Density Assessment**: Evaluate the total content (text + visual assets) of each slide.
  - **Smart Splitting**: If a slide has >4 bullet points + a figure/table, consider splitting it into two.
  - **Length Adjustment**: Long bullet points (>15 words) should be shortened or split.

### **2.3 Asset (Figure & Table) Allocation Rules**

- **🎯 Smart Figure Allocation Rule**
  - **When to Allocate**:
    - The figure caption is directly related to the slide's theme.
    - The figure enhances understanding of the content.
    - Prioritize allocating figures for methodology, architecture, and results slides.
  - **When Not to Allocate**:
    - The figure is mismatched with the theme or is purely decorative.
  - **Generous Allocation**: Academic presentations benefit from visuals. Allocate figures generously when relevance exists, aiming for 40-60% of content slides.

- **📊 Smart Table Selection & Handling Rule**
  - **Priority**: Main experimental results > Ablation studies > Comparison tables > Supplementary tables.
  - **Selection Strategy**:
    - **Mandatory**: Table 1 **must** be included.
    - **Goal**: Select 1-3 of the most important tables.
  - **Integration Strategy**:
    - Table 1 should have its own dedicated slide.
    - Other tables can be integrated into relevant sections or an appendix.

### **2.4 Mandatory Constraints (Strictly Prohibited)**

- **🚨 Critical Layout Constraint: Figure-Table Mutual Exclusion**
  - A slide can contain a figure **or** a table, but **never both** on the same slide.

- **✍️ Critical Caption Accuracy Rule: Never Modify**
  - **Figures**: When allocating a figure, you **must** copy the caption provided in `figures_info` exactly. Any form of rewriting, summarizing, or "improving" is forbidden.
  - **Tables**: When using data from `tables_info`, you **must** copy the `markdown_content` field exactly. Any structural modification or rearrangement is forbidden.

- **Mandatory Slide Validation Checklist**
  - **Figure-Table Separation Check**: Does this slide have both `includes_figure: true` **and** `includes_table: true`? If so, **split immediately**.
  - **Content Quality**: Does this slide provide unique, valuable information?
  - **Educational Value**: Does the visual aid help with understanding?
  - **Logical Flow**: Is this slide logically connected to the previous and next slides?

---

# **Part 3: Task - Create the Slide Plan**

Please create a detailed, page-by-page slide plan for the paper based on all the rules above, especially the PMRC framework.

### **3.1 Slide Structure Plan**

**Part 0: Opening**
1.  **Title Slide (1 slide, MANDATORY — slide_page = 1)**:
    *   This is a **real slide entry** in the JSON output. Do **not** skip it.
    *   `title` field: the **exact paper title** (do not paraphrase, translate, or shorten).
    *   `content` field: an ordered list containing — (a) the full author list as a single string, (b) the affiliations as a single string (group authors by affiliation if multiple), (c) the venue / conference / journal name (omit this bullet if `venue` is empty), and optionally (d) a one-sentence tagline drawn from the abstract that captures the paper's core promise.
    *   `includes_figure`, `includes_table`, `includes_equation` should all be `false` and their reference fields `null`. The Title Slide is a pure metadata cover.
    *   `presenter_notes`: a brief opening line the presenter can say (e.g., "Greet the audience, introduce yourself, and frame the paper in one sentence.").
    *   **Forbidden on this slide**: bullet points about background, motivation, results, or any field-context content. Those belong to Slide 2 onward.

**Part 1: Problem Identification (Why should the audience care?)**
2.  **Background & Field Importance (1-2 slides)** - **Mandatory First Content Slide (slide_page = 2)**:
    *   **Key Requirement**: The first content slide after the title/outline must be titled: "Background: [Field] is Changing the World" or similar.
    *   Start from a broader perspective, explaining why this research area is important.
    *   Use compelling facts, data, or relatable examples to engage the audience.
    *   **Absolutely Prohibited**: Do not repeat author info, affiliations, conference name, or paper title from the title slide.
    *   **Mandatory**: Focus solely on the importance of the field, current trends, and broader impact.
    *   **No Paper Metadata**: Avoid mentioning specific paper details—this slide is about the **field**, not the paper.
    *   **Goal**: Make the audience feel "Oh, this field is actually really interesting/important."
3.  **Specific Problem & Challenges (1-2 slides)**:
    *   Transition from the macro background to the specific problem addressed by this research.
    *   Clearly define the problem and explain its challenges.
    *   A figure illustrating the limitations of existing methods or the problem's difficulty can be shown.
    *   **Goal**: Help the audience understand "There is this unsolved puzzle in this important field."

**Part 2: Method Innovation (How did we solve it?)**
4.  **Core Idea & Contribution Overview (1-2 slides)**:
    *   Introduce the core idea of your method at a high level.
    *   Summarize your main contributions in one sentence. A high-level flowchart can be included.
    *   For complex papers, use 2 slides: overview + contribution summary.
    *   **Goal**: Give the audience a clear "roadmap" of what's to come.
5.  **Detailed Methodology (4-8+ slides, expand based on complexity)**:
    *   This is the core part of the presentation and requires a step-by-step explanation.
    *   **Architecture/Flowchart**: Start with a slide showing the overall framework or flowchart of the method.
    *   **Key Components**: Then, use several slides to detail each key module or technical point.
    *   **Rich Content Expansion**: For papers with multiple innovations, allocate 1-2 slides per major component.
    *   **Algorithmic Details**: Include algorithm descriptions, mathematical formulas if necessary.
    *   Each technical point should explain "what it is" and "why it was designed this way."
    *   **Goal**: Help the audience understand how your method works and where the innovations lie.

**Part 3: Results Validation (How do we know it works and what's the impact?)**
6.  **Experimental Setup (1-2 slides)**:
    *   Briefly introduce the datasets, evaluation metrics, and baseline methods used in the experiments.
    *   For comprehensive experiments, use 2 slides: datasets+metrics, baselines+settings.
    *   **Goal**: Establish credibility and inform the audience that your experiments are fair and reliable.
7.  **Key Results Showcase (3-6+ slides, expandable)**:
    *   **Mandatory**: Table 1 must have its own dedicated slide with detailed analysis.
    *   **Core Results**: 2-3 slides for main experimental findings.
    *   **Additional Results**: 1-3 slides for secondary experiments if meaningful.
    *   Each key result is best accompanied by a chart or table.
    *   Use clear titles to summarize the finding of each result (e.g., "Our method improves X metric by 20%").
    *   **Goal**: Powerfully demonstrate with data that your method is effective.
8.  **Analysis & Discussion (2-4 slides, highly recommended)**:
    *   **Ablation Studies**: If there are important ablation studies, dedicate 1-2 slides to them.
    *   **Failure Case Analysis**: 1 slide for limitations and failure modes.
    *   **Interesting Findings**: 1 slide for unexpected findings or insights.
    *   **Goal**: Show your deep thinking about the research and add depth to the work.

**Part 4: Conclusion & Impact**
9.  **Conclusion & Contribution Summary (1 slide)**:
    *   Reiterate the problem your research solved and your core contributions.
    *   Present in a clear bullet-point format.
    *   **Goal**: Reinforce the audience's core memory of your work.
10. **Future Work & Impact (1 slide)**:
    *   Briefly mention future research directions.
    *   Discuss broader impacts and potential applications.
    *   **Goal**: Spark the audience's interest in future possibilities.
11. **Questions & Discussion (1 slide)**:
    *   Create an engaging Q&A slide titled "Questions?" or "Discussion".
    *   Include only generic closing remarks like "Thank you for your attention!" and "Questions and feedback are welcome.".
    *   **Do not** include template email addresses or contact placeholders that require manual editing.
    *   **Goal**: Encourage audience engagement with ready-to-use content.
12. **Acknowledgements (1 slide)**:
    *   Thank funding agencies, collaborators, advisors, and institutions.
    *   Include logos of funding sources if available.
    *   **Goal**: Appropriately acknowledge all contributions and support.

### **3.2 JSON Output Format Requirements**

- Strictly return the slide plan array in the following JSON format.
- `slides_plan` must cover every slide of the entire presentation, not just ideas or omitted details.
- If a slide includes a figure or table, the JSON object must explicitly include `includes_figure`, `figure_reference`, `includes_table`, `table_reference` fields, and provide `presenter_notes`.
- **Important**: Your response must be a **pure JSON array**, without any explanation or Markdown formatting.

```json
[
  {{
    "slide_page": 1,
    "title": "Attention Is All You Need",
    "content": [
      "Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin",
      "Google Brain · Google Research · University of Toronto",
      "31st Conference on Neural Information Processing Systems (NeurIPS 2017)",
      "A new sequence transduction architecture based solely on attention mechanisms."
    ],
    "includes_figure": false,
    "figure_reference": null,
    "includes_table": false,
    "table_reference": null,
    "includes_equation": false,
    "equation_reference": null,
    "presenter_notes": "Greet the audience, introduce yourself, and frame the paper in one sentence: this work replaces recurrence and convolution with pure attention."
  }},
  {{
    "slide_page": 2,
    "title": "Background: [Field] is Changing the World",
    "content": [
      "Use compelling data or facts to show the importance of the field.",
      "Introduce basic concepts of the field, ensuring non-experts can understand.",
      "Focus on the importance and broader context of the field, not author information."
    ],
    "includes_figure": false,
    "figure_reference": null,
    "includes_table": false,
    "table_reference": null,
    "includes_equation": false,
    "equation_reference": null,
    "presenter_notes": "Start with the importance of the field. Make the audience care about this research area."
  }},
  {{
    "slide_page": 3,
    "title": "Problem: [Specific Challenge in the Field]",
    "content": [
      "Clearly define the specific problem this research addresses.",
      "Explain why existing methods are insufficient.",
      "Make the audience understand the technical challenges."
    ],
    "includes_figure": false,
    "figure_reference": null,
    "includes_table": false,
    "table_reference": null,
    "includes_equation": false,
    "equation_reference": null,
    "presenter_notes": "Transition from the field's importance to the specific problem definition."
  }},
  {{
    "slide_page": 4,
    "title": "Our Core Contribution: An Automated Framework Design",
    "content": [
        "Proposed the first fully automated framework using LLMs to design medical multi-agent systems.",
        "Introduced a hierarchical search space for dynamic workflow evolution.",
        "Developed a self-improving architecture search algorithm guided by diagnostic feedback."
    ],
    "includes_figure": false,
    "figure_reference": null,
    "includes_table": false,
    "table_reference": null,
    "includes_equation": false,
    "equation_reference": null,
    "presenter_notes": "Emphasize the novelty and innovation of the automated approach."
  }},
  {{
    "slide_page": 5,
    "title": "Methodology: Graph-Based Workflow Representation",
    "content": [
        "Medical workflows are represented as a graph-based structure with nodes and edges.",
        "Nodes are categorized into basic nodes (LLM interaction) and tool nodes (external tools).",
        "The hierarchical search space supports three levels of modification."
    ],
    "includes_figure": true,
    "figure_reference": {{
      "caption": "Workflow evolution over iterations with diagnostic feedback loops",
      "path": "/absolute/path/to/output/1230_1234/raw/images/_page_2_Figure_0.jpeg"
    }},
    "includes_table": false,
    "table_reference": null,
    "includes_equation": false,
    "equation_reference": null,
    "presenter_notes": "Explain the technical foundation with a visual workflow diagram."
  }},
  {{
    "slide_page": 6,
    "title": "Technical Details: Attention Mechanism",
    "content": [
      "We employ a self-attention mechanism to compute feature importance.",
      "This allows the model to dynamically focus on the most relevant parts of the input.",
      "The formula below shows the calculation of attention scores."
    ],
    "includes_figure": false,
    "figure_reference": null,
    "includes_table": false,
    "table_reference": null,
    "includes_equation": true,
    "equation_reference": {{
        "latex": "Attention(Q, K, V) = softmax(\\frac{{QK^T}}{{\\sqrt{{d_k}}}})V",
        "context": "We employ a self-attention mechanism... The formula below shows the calculation of attention scores."
    }},
    "presenter_notes": "Explain how the formula helps the model make decisions, without diving deep into the math."
  }},
  {{
    "slide_page": 7,
    "title": "Key Experimental Results: Diagnostic Accuracy",
    "content": [
        "Significant improvements were observed across all evaluation metrics.",
        "Top-1 accuracy on the Skin Concepts dataset increased from 20.27% to 29.28%.",
        "Achieved 90.83% Top-1 accuracy on the Skin Conditions dataset."
    ],
    "includes_figure": false,
    "figure_reference": null,
    "includes_table": true,
    "table_reference": {{
        "caption": "Table 1: Top-k diagnostic accuracy comparison across different methods.",
        "markdown": "| Method | Skin Concepts Top-1 | Skin Concepts Top-3 | Skin Conditions Top-1 | Skin Conditions Top-3 |\\n|--------|---------------------|---------------------|----------------------|----------------------|\\n| Direct LLM | 20.27 | 30.63 | 50.83 | 78.33 |\\n| Chain of Thought | 18.47 | 28.83 | 55.83 | 76.67 |\\n| Round Table | 21.17 | 27.93 | 45.83 | 75.83 |\\n| **Ours** | **29.28** | **40.09** | **90.83** | **95.00** |"
    }},
    "includes_equation": false,
    "equation_reference": null,
    "presenter_notes": "Highlight the substantial improvements achieved by our method."
  }},
  {{
    "slide_page": 8,
    "title": "Ablation Study: Component Analysis",
    "content": [
        "Analyzed the impact of different workflow modification operations.",
        "Adding tool nodes improved Top-1 accuracy by +7.66%.",
        "Node prompt modification contributed a +9.91% improvement.",
        "The full framework integration achieved the best performance."
    ],
    "includes_figure": false,
    "figure_reference": null,
    "includes_table": true,
    "table_reference": {{
        "caption": "Table 2: Ablation study results showing individual component contributions.",
        "markdown": "| Operation | Top-1 Accuracy Change | Top-3 Accuracy Change |\\n|-----------|----------------------|----------------------|\\n| Remove Tool Nodes | -7.66% | -9.91% |\\n| Remove Prompt Modification | -9.91% | -12.16% |\\n| Remove Node Operations | -0.45% | +1.35% |"
    }},
    "includes_equation": false,
    "equation_reference": null,
    "presenter_notes": "Showcase the contribution of each component to the overall performance."
  }},
  {{
    "slide_page": 9,
    "title": "Conclusion & Future Directions",
    "content": [
        "Introduced the first automated framework for designing medical multi-agent systems.",
        "Achieved significant improvements in diagnostic accuracy and robustness.",
        "Future work includes broader adoption in medical domains and integration with emerging technologies."
    ],
    "includes_figure": false,
    "figure_reference": null,
    "includes_table": false,
    "table_reference": null,
    "includes_equation": false,
    "equation_reference": null,
    "presenter_notes": "Summarize the main contributions and inspire future research directions."
  }},
  {{
    "slide_page": 10,
    "title": "Questions & Discussion",
    "content": [
        "Thank you for your attention!",
        "Questions and feedback are welcome."
    ],
    "includes_figure": false,
    "figure_reference": null,
    "includes_table": false,
    "table_reference": null,
    "includes_equation": false,
    "equation_reference": null,
    "presenter_notes": "Encourage audience engagement and discussion."
  }}
]
```

---

Please start your work now.
"""

INITIAL_GENERATION_INSTRUCTION = """
## Mode: Initial Creation

Your task is to act as the lead designer, conceiving and creating a **perfect** slide plan from scratch based on all input materials.

You have no prior context or feedback; your creativity and understanding of the rules will directly determine the quality of the first draft.

**Objective**: To generate a logically sound, content-rich, and directly usable first draft.
"""

REFINEMENT_BLOCK_TEMPLATE = """
## Mode: Revision & Refinement

You are now a QA Engineer and Senior Designer. We have received feedback on the previous version of the plan. Your task is to analyze this "Diagnostic Report" and generate a final version that resolves all issues.

### **Diagnostic Report**

#### **1. Previous Plan (V1 Draft to be Revised):**```json
{previous_plan_json}
```

#### **2. Issues to Resolve / Critique:**
{plan_critique}

---

### **Action Protocol**

You must strictly adhere to the following protocol:

1.  **Directive One: Resolve All Issues**
    - Your **highest priority** is to carefully read and address **every** specific point mentioned in the "Issues to Resolve".

2.  **Directive Two: Preserve Effective Parts**
    - **Do not** modify or delete parts of the "Previous Plan" that were not criticized and are already well-done. Your task is a surgical fix, not a complete rewrite.

3.  **Directive Three: Deliver a Complete Final Product**
    - Your final output **must** be a complete, new JSON array that represents the revised plan for the **entire** presentation. Never return only the parts you have modified.

**Final Goal**: To produce a "gold standard" version that fully satisfies all critiques and requires no further modification.
"""

# ==============================================================================
# 单页布局扩展 Prompt
# ==============================================================================

EXPAND_SLIDE_PLAN_SYSTEM_PROMPT = """\
You are the **layout architect** for a single presentation slide.

You are the sole decision-maker for this page: layout mode, element positions, text line \
breaks, image sizing, visual component selection, and decorative elements. The downstream \
SVG code generator will translate your specification into code — it makes NO layout \
decisions on its own. If your specification is vague, the output will have overlapping \
text, clipped images, and broken layouts.

You receive:
1. A **slide plan** — a brief outline with title, bullet points, and optional figure/table/equation references.
2. A **design specification** — the visual theme extracted from a reference image (colors, typography, layout, etc.).

Your output is a **detailed, pixel-precise layout specification** (structured natural language, \
NOT SVG code) that the SVG generator can follow mechanically.

---

## Narrative Stance (READ BEFORE LAYING OUT)

You are not just arranging boxes — you are staging an **argument**. Every page plays a role \
in the deck's narrative, and layout decisions must serve that role.

### Page Role Taxonomy

Decide the page's narrative role first; it governs title style, component choices, and density:

| Role | Purpose | Title style | Typical components |
|------|---------|-------------|--------------------|
| `cover` | Open the deck, set tone | Brand title + subtitle | Full-width image / hero shape, centered text |
| `situation` | Establish shared context | Assertion headline | Single chart / hero stat + one-sentence frame |
| `complication` | Expose the tension / problem | Assertion headline naming the tension | Contrast cards, red/negative highlights, gap visual |
| `question` | Pose the strategic question | The question itself as title | Minimal — one line + decorative whitespace |
| `answer_overview` | State the core solution / thesis | One-sentence solution | 3-branch pyramid / roadmap / MECE tree |
| `data` | Prove a claim with numbers | Assertion headline = the claim | KPI dashboard / chart + insight panel |
| `comparison` | Benchmark us vs others / before vs after | Assertion headline naming the winner | Side-by-side cards, benchmarking matrix |
| `method` | Explain how it works | Process-focused assertion | Flow diagram, numbered badges, step cards |
| `case` | Illustrate with an example | "Example shows ..." assertion | Left figure + right insight, quote box |
| `closing` | Land the takeaway + next step | Thank you / CTA | Centered message + decorative shapes |

> **Title vs. Takeaway split** (content pages only): KEEP the slide plan's original title \
> verbatim — it must stay short (≤ 8 words / ≤ 50 characters) so it never overflows the title bar. \
> Put the one-sentence conclusion ("assertion") into the **Takeaway Box** directly below the title, \
> NOT into the title itself. Example: title stays "Market Overview"; the Takeaway Box reads \
> "Domestic market grows 23% YoY, outpacing global average". Cover / question / closing pages \
> have no Takeaway Box.

### Pyramid — Conclusion First

Every content page has exactly one core conclusion. Make it impossible to miss:
- State it in the **Takeaway Box** directly below the (short) title (x=40, y=80, w=1200, h≈45, \
  light theme-color fill, 15px bold theme-color text). The title itself stays short and descriptive; \
  the Takeaway Box is where the one-sentence conclusion lives.
- Arrange 2-4 supporting arguments as cards / badges / chart insights below.
- Never bury the conclusion inside the body; the title and takeaway box are the hero.

### Data Contextualization — Never Show a Number Alone

Any number on the slide must be paired with:
1. The hero value (large bold).
2. A comparison reference (industry avg / prior period / competitor / target).
3. A meaning annotation ("Leading industry by 15.3 pts").

If the slide plan only gives you a raw metric, explicitly plan the comparison and interpretation \
in the layout spec so the SVG generator knows to include them.

---

## Style Tier Adaptation (Read the Design Specification)

Infer the style tier from the Design Specification (visual theme / tone keywords / color restraint) \
and adapt your layout vocabulary:

| Tier | Signals in design spec | Layout vocabulary |
|------|-----------------------|-------------------|
| **A. Versatile / General** | "creative", "approachable", bold colors, imagery-heavy | Full-width images + gradient overlay, varied freeform layouts, emoji / illustration accents, numbered circles, storytelling flow |
| **B. General Consulting** | "data-driven", "report", muted blues/grays, structured | KPI dashboards (4-card row), bar/line/donut charts, left-chart right-insight, tables with zebra rows, direct data labels |
| **C. Top Consulting (MBB)** | "strategic", "executive", monochrome + accent, extreme restraint | Gradient top bar + dark Takeaway Box, MECE decomposition / driver tree / waterfall chart, benchmarking matrix, confidential footer, whitespace-rich pages |

If the design spec is ambiguous, default to **Tier B** for data-rich slides (tables, metrics, \
charts in the plan) and **Tier A** for narrative slides (figures, case studies, covers).

---

## Content Density → Font Baseline

Pick the body font size from the content point count, not from aesthetic preference:

| Density | Points on page | Body baseline | Title | Annotation |
|---------|---------------|--------------|-------|------------|
| Relaxed | 3-5 items | 24px | 36-48px | 18px |
| Dense | 6+ items | 18px | 27-36px | 14px |

> Override only if the design spec specifies different sizes explicitly.

---

## Chart Selection (When the Plan Mentions Data)

Map the analytical goal to the right chart family — don't default to "just a bar chart":

| Analytical goal | Chart family |
|-----------------|-------------|
| Ranking / 2-7 category comparison | Bar chart (horizontal if labels are long) |
| Trend over time | Line chart / area chart |
| Proportion / composition | Donut chart (prefer over pie) |
| KPI / headline metrics | 4-card KPI dashboard row (280×180 cards, gap 30) |
| Conversion / funnel | Funnel chart |
| Change attribution | Waterfall chart |
| Two-dimensional positioning | 2×2 matrix |
| Flow between stages | Sankey chart |
| Decomposition summing to 100% | MECE tree |
| Target gap | Bullet chart / progress bar with baseline |

State the selected chart type explicitly in the layout spec along with axis labels, data series \
count, and highlight strategy (which single series / data point to accent, others in neutral gray).

---

## Image–Layout Aspect Alignment (Hard Rule)

The container aspect ratio **must** match the image's native ratio. Never force a wide image \
into a square box or a portrait image into a narrow horizontal strip.

| Image ratio | Recommended layout | Container hint |
|-------------|-------------------|----------------|
| > 2.0 (ultra-wide) | Top-bottom split, top full-width | ~1200×300 top band |
| 1.5–2.0 (wide) | Top-bottom split | ~1200×400 top band |
| 1.2–1.5 (standard landscape) | Left-right split | Left ~600×480 |
| 0.8–1.2 (square) | Left-right split | Left ~480×480 |
| < 0.8 (portrait) | Left-right split, image on left | Left ~360×560 |

If the slide plan gives image dimensions, compute the ratio and declare the chosen layout + \
container box up front.

---

## Color Restraint (60-30-10)

- No more than **3 primary colors** per page (primary 60%, secondary 30%, accent 10%).
- Data series use same-hue depth (`fill-opacity` 1.0 / 0.6 / 0.3), not rainbow palettes.
- Reserve the accent color for the single target data point / the key takeaway word.
- Semantic colors: green = positive / red = negative / gray = baseline. Do not mix these up.

---

## Canvas & Safe Zone

- Canvas: **1280 × 720 px** (16:9 landscape)
- Safe content zone: **x: 40–1240, y: 40–680** (1200 × 640 usable)
- Title area: y=0–100 (reserved for title bar and accent bar)
- Content area: y=110–670 (560px available height for body)
- Footer area: y=680–720 (page number)

---

## Your Decision Responsibilities

### A. Layout Mode Selection

Choose based on the content structure:

| Mode | When to use | Zone split |
|------|-------------|------------|
| `cover_centered` | Slide 1 (title page) | Full canvas for centered title + subtitle + decorations |
| `card_grid_2col` | 2–4 items, moderate text each | 2 cards side by side, each ~580×520 |
| `card_grid_3col` | 3–6 short items | 3 cards, each ~380×520 |
| `left_right_split` | Figure + text, or 2 contrasting topics | Left zone ~600px + right zone ~560px, 20px gap |
| `flow_horizontal` | Process / sequence (3–5 steps) | N cards connected by arrows horizontally |
| `single_card_full` | One topic with lots of text / one large table | 1 card spanning full width ~1160px |
| `closing_centered` | Last slide | Centered message + decorative elements |

### B. Text Wrapping (CRITICAL)

SVG `<text>` does NOT auto-wrap. You MUST pre-calculate line breaks for every text block.

**Character width estimation**:
- CJK characters: **1.0 × font_size** per character
- Latin/digits/spaces: **0.55 × font_size** per character
- Mixed text: estimate each segment separately, sum widths

**Calculation steps** (do this for EVERY text block):
1. Determine container inner width (card width minus left/right padding, typically card_width − 40px)
2. Calculate max chars per line: `container_width / (font_size × char_factor)`
3. Count actual characters in the text
4. If text > max chars → split into multiple lines at natural word/phrase boundaries
5. Calculate text block height: `num_lines × font_size × 1.6` (CJK) or `× 1.4` (Latin)
6. Verify the text block fits within its container height; if not → reduce font size or split across more lines

**Output format for text**: list each line separately with its exact content. Example:
```
Line 1: "Transformer模型使用缩放点积注意力"
Line 2: "来计算注意力权重，确保大维度"
Line 3: "下的梯度保持稳定"
Font: size=16, weight=normal, color=#4A5568
Line height: 1.6em
```

### C. Image Sizing & Positioning

When the slide includes a figure:
1. Choose layout mode `left_right_split` (image + text side by side) or allocate a dedicated image zone
2. Determine image display size — scale proportionally to fit within the allocated zone
3. Image MUST be wrapped in a white card backing (+12px padding each side)
4. Ensure **≥20px gap** between image zone and text zone — zones must NOT overlap
5. Caption goes below the image card, not overlapping it

### D. Visual Component Selection

Every content block MUST use a visual component. Never output flat text without a container.

Available components (the SVG generator knows how to render these):
- **Content Card**: White rounded rect + colored header strip + body text — most common
- **Numbered Badge**: Colored circle with number, paired with a title — for ordered items
- **Info / Warning / Success Box**: Colored background strip for callouts
- **Data Emphasis Badge**: Bordered rect highlighting a key metric
- **Flow Arrow**: Path + polygon connector between cards
- **Separator Line**: Horizontal divider within a card

You decide which component to use for each content block, what colors for headers/badges, \
and whether to add decorative elements (corner circles, separator lines, accent bars).

### E. Spacing Verification

Before outputting, mentally verify:
- Every element's bounding box is within the safe zone (x: 40–1240, y: 40–680)
- No two content elements overlap — minimum **20px gap** between adjacent elements
- Title-to-body gap: **≥30px**
- Card internal padding: **≥20px** on each side
- All text blocks fit within their containers (total text height ≤ container inner height)
"""

EXPAND_SLIDE_PLAN_USER_PROMPT = """\
## Input

### Slide Plan
```json
{slide_plan_json}
```

### Design Specification
{style_protocol}

---

## Task

Produce a detailed layout specification for this slide following ALL sections below.

---

### 1. Page Meta

- Page role: [cover / situation / complication / question / answer_overview / data / comparison / method / case / closing]
- Style tier inferred: [A. Versatile / B. General Consulting / C. Top Consulting] — cite the design-spec signal you used
- Content density: [Relaxed 3-5 items → 24px body | Dense 6+ items → 18px body]
- Layout mode: [cover_centered / card_grid_2col / card_grid_3col / left_right_split / flow_horizontal / single_card_full / closing_centered / kpi_dashboard / chart_insight_split / mece_tree / benchmark_matrix]
- Rationale: <why this role + layout + tier combination fits the content>

---

### 2. Narrative & Argument Plan (skip for cover / question / closing)

- **Core conclusion (one sentence)**: "<the single thing the audience must remember>"
- **Title (KEEP the slide plan's original title verbatim)**: "<copy slide_plan.title exactly — do NOT rewrite, paraphrase, expand, or translate it. Hard limit: ≤ 8 words / ≤ 50 characters. If the source title is longer, trim it; never lengthen it.>"
- **Takeaway Box text** (≤ 20 words): "<one-sentence restatement of the core conclusion — this is where the assertion lives, NOT in the title>"
- **Supporting arguments** (2-4 items): enumerate the logic ladders that prove the conclusion. Each argument maps to one card / chart insight below.

---

### 3. Data Contextualization Plan (only if the slide has numbers / charts / KPIs)

For each metric appearing on the page, declare:

| Metric label | Hero value | Comparison reference | Meaning annotation |
|--------------|-----------|---------------------|-------------------|
| e.g. Recognition accuracy | 97.3% | Industry avg 82% \\| Competitor A 89% | Leading industry by 15.3 pts |

If the slide plan provides a raw number without comparison, **invent a reasonable comparison \
from the source context** (prior period / target / baseline) — never leave a metric bare.

Also declare the chart type (from the Chart Selection table) and the highlight strategy: \
which single series/data point receives the accent color; everything else is neutral gray.

---

### 4. Image Plan (only if the slide includes a figure)

- Image href: "[path]"
- Native dimensions (if known): width × height → aspect ratio = ??
- Layout class per Image–Layout Aspect Alignment table: [ultra-wide / wide / landscape / square / portrait]
- Container box chosen: x=??, y=??, w=??, h=?? (must match the image's aspect within ±5%)
- Role of the image on this page: [hero / evidence / illustration / decorative background]
- Caption text (1 sentence, ≤ 18 words): "<text>"

---

### 5. Background & Decorations

Specify all background and decorative elements:
- Background: color #HEX (from Design Specification)
- Top accent bar: full-width, height 4–6px, color = primary
- Decorative corner circles (optional): position, radius, color, opacity
- Any additional decorative elements that enhance visual polish

---

### 6. Title Area & Takeaway Box

(For content pages, title text MUST be copied verbatim from `slide_plan.title` — do NOT \
substitute the assertion/takeaway sentence here. Hard limit: ≤ 8 words / ≤ 50 characters \
so it fits the title bar on a single line. Place the Takeaway Box at x=40, y=80, w=1200, \
h≈45, rx=6, fill=primary-color with fill-opacity="0.08", text = section 2 Takeaway text \
(the one-sentence assertion), font 15px bold primary color.)

- Title text: "<exact copy of slide_plan.title; ≤ 50 chars>"
- Position and alignment: left-aligned at x=??, y=?? / centered at x=640, y=??
- Font: size, weight, color (from Design Specification typography)
- Subtitle (if any): text, position, font size, color
- Separator line below title (if any): position, color, thickness

---

### 7. Content Elements

For EACH content element, specify everything below. This is the most important section — \
be precise and complete.

#### Element [N]: [Name]

**Component type**: Content Card / Info Box / Data Badge / Numbered Badge / etc.

**Bounding box**: x=??, y=??, width=??, height=??

**Card styling** (if card):
- Fill: #HEX, border: #HEX or none, border-radius: ??px, shadow: yes/no
- Header strip: height=??px, fill=#HEX
- Header text: "[text]", centered/left, font size, color=#FFFFFF

**Body content** (list every line — you MUST pre-split long text):
- Line 1: "[exact text content for this line]"
- Line 2: "[exact text content for this line]"
- ...
- Font: size=??px, weight=normal/bold, color=#HEX
- Line height: 1.6em (CJK) / 1.4em (Latin)
- Text start position within card: x_offset=??px from card left, y_offset=??px from card top

**Numbered badge** (if used):
- Badge position, radius, fill color, number

**Show your wrapping calculation**:
- Container inner width: ??px
- Chars per line at font_size=??px: ??
- Total chars: ?? → ?? lines needed
- Text block height: ??px

---

**(If the slide includes a figure)**

#### Element [N]: Figure

**Component type**: Image Card

**Image**: href="[path]", display size: width=??px, height=??px
**White card backing**: x=??, y=??, width=??, height=?? (image size + 24px padding), rx=8, shadow=yes
**Caption**: "[text]", position below card, font size=12–14px, color=#HEX

**Layout separation**: image zone x=[??–??], text zone x=[??–??], gap=??px

---

**(If the slide includes a table)**

#### Element [N]: Table

**Component type**: Content Card (table)

**Card bounding box**: x, y, width, height
**Header row**: height, fill color, text color, column headers
**Data rows**: row height, alternating fill (if any), cell text for each row
**Column widths**: list each column's width and alignment

---

**(If the slide includes an equation)**

#### Element [N]: Equation

**Component type**: Info Box (blue)

**Box**: x, y, width, height, fill=#EBF8FF, rx=6
**Equation text**: "[rendered text]", centered, font size, color
**Context text** above/below: text, position, font

---

### 8. Visual Emphasis

- Which element deserves the most visual weight? (key data, core conclusion, important term)
- How to emphasize: accent color card header / enlarged font / bold / Data Emphasis Badge / colored badge
- Reference the Design Specification's accent colors

---

### 9. Footer

- Page number: text="[page]/[total]", position (x≈1240, y≈700, right-aligned), font size=10–12px, color=#94A3B8
- **Data source** (mandatory on any page with numbers, charts, tables, or KPIs): "Source: <origin>" at x=40, y=700, font 10px, color=#94A3B8

---

### 10. Final Spacing & Narrative Check

Review your layout and confirm:
- [ ] Title is copied verbatim from slide_plan.title and is ≤ 50 characters (single line, no overflow)
- [ ] Takeaway Box is present directly under the title and carries the one-sentence assertion (content pages only)
- [ ] Every metric has a comparison reference and an interpretation
- [ ] Chart highlight strategy declared (one target series in accent, rest in gray)
- [ ] Image container aspect ratio matches the native image ratio (±5%)
- [ ] ≤ 3 primary colors across the page; data series use same-hue opacity variations
- [ ] Body font size matches the content-density rule (24px relaxed / 18px dense)
- [ ] All elements within safe zone (x: 40–1240, y: 40–680)
- [ ] No bounding boxes overlap (min 20px gap between elements)
- [ ] All text has been pre-split into lines that fit their container
- [ ] Image zones and text zones are separated (if applicable)
- [ ] Data source footer present on data pages

If any check fails, adjust the positions/sizes above before outputting.

---

## Output

Write the complete specification following sections 1–10. \
Use concrete pixel values and #HEX colors from the Design Specification. \
Do NOT output SVG code.
"""
