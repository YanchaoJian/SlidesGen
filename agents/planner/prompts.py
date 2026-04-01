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
Extract basic paper information: Title, Authors, Affiliations, Abstract, Keywords.

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

- **Content Deduplication Rule**
  - **Never create slides that repeat information from the title slide**.
  - **Strictly Prohibited**: Creating any slide that includes "Authors:", "Institutional Affiliations:", or repeats paper metadata.
  - **Mandatory**: The first content slide (Slide 2) **must** be about the importance/background of the field, **not** the paper's details.

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

**Part 1: Problem Identification (Why should the audience care?)**
1.  **Title Slide (1 slide)**: Includes title, authors, and affiliations. (This is auto-generated by LaTeX titlepage, do **not** create a separate slide entry for it).
2.  **Background & Field Importance (1-2 slides)** - **Mandatory First Content Slide**:
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
    "slide_page": 2,
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
    "slide_page": 3,
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
    "slide_page": 4,
    "title": "Methodology: Graph-Based Workflow Representation",
    "content": [
        "Medical workflows are represented as a graph-based structure with nodes and edges.",
        "Nodes are categorized into basic nodes (LLM interaction) and tool nodes (external tools).",
        "The hierarchical search space supports three levels of modification."
    ],
    "includes_figure": true,
    "figure_reference": {{
      "caption": "Workflow evolution over iterations with diagnostic feedback loops",
      "path": "output/1230_1234/images/_page_2_Figure_0.jpeg"
    }},
    "includes_table": false,
    "table_reference": null,
    "includes_equation": false,
    "equation_reference": null,
    "presenter_notes": "Explain the technical foundation with a visual workflow diagram."
  }},
  {{
    "slide_page": 5,
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
    "slide_page": 6,
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
    "slide_page": 7,
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
    "slide_page": 8,
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
    "slide_page": 9,
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