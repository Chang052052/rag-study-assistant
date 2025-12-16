# A Citation-Grounded RAG Study Assistant for Exam-Oriented PDF Study
*A citation-grounded RAG demo for exam-oriented PDF study*

## Note
This repository presents a small research-oriented demo of a retrieval-augmented generation (RAG) system.
The focus is on system design, retrieval strategies, and evaluation, rather than full system deployment.

## Problem
Students preparing for exams rely heavily on fragmented PDF lecture notes and past papers.
Traditional keyword-based search makes it difficult to locate precise explanations or relevant
examples, while large language models may hallucinate answers without reliable sources.

## Objective
The goal of this project is to design a retrieval-augmented generation (RAG) study assistant that answers exam-related questions strictly based on retrieved PDF evidence, with explicit citations to the source documents.

## Data
The system indexes 10–20 course PDFs, including Analysis III (Complex Analysis) lecture notes, tutorial sheets, and past exam papers. Each document is treated as an authoritative knowledge source for answering queries.

## Method
The proposed system follows a retrieval-augmented pipeline:
- Document segmentation into manageable text chunks  
- Sparse retrieval using keyword-based (BM25-style) methods  
- Dense retrieval using TF-IDF semantic similarity  
- Evidence-grounded answer generation with explicit source citations   

## Evaluation Plan
The system is evaluated using a manually curated set of exam-style questions.
Evaluation focuses on evidence recall, answer usefulness, and common failure modes such as missing relevant chunks or ambiguous retrieval results.

## Evaluation Questions

### Definition-based Questions
Q1. What is the definition of a complex number in canonical form?  
Q2. What does the modulus |z| of a complex number represent geometrically?  
Q3. What does it mean for a function to be holomorphic on a domain?  
Q4. What is the definition of the derivative of a complex function at a point?  
Q5. What is a harmonic function in the context of complex analysis?  

### Formula / Method-based Questions
Q6. What is Euler’s formula and how is it used to represent complex numbers in polar form?  
Q7. State the Cauchy–Riemann equations and explain their role in complex differentiability.  
Q8. How is the radius of convergence of a power series defined?  
Q9. What is the relationship between a holomorphic function and harmonic functions?  
Q10. How can the derivative of a power series be computed within its radius of convergence?  

### Location-based Questions
Q11. Where in the lecture notes are the Cauchy–Riemann equations introduced and derived?  
Q12. Which chapter discusses the geometric interpretation of complex multiplication?  
Q13. In which section is the concept of holomorphic (analytic) functions formally defined?  
Q14. Where can examples of functions that are continuous but not differentiable be found?  
Q15. Which part of the notes explains the connection between holomorphic and harmonic functions?  

### Exam-oriented / Application Questions
Q16. How can the Cauchy–Riemann equations be used to show that a function is not differentiable?  
Q17. In exam questions, how do you typically verify whether a given function is holomorphic?  
Q18. How are power series used to represent holomorphic functions locally?  
Q19. What common mistakes do students make when applying the definition of complex differentiability?  
Q20. Which topics from the notes are most frequently combined in exam-style proof questions?

## Retrieval Experiment (Mini)
Goal: compare sparse (keyword/BM25-style) vs dense (embedding) retrieval on a small subset of exam-style questions, and analyse evidence recall.

### Setup
- Data: a subset of the Complex Analysis PDFs in `docs/`
- Query set: 3 exam-style questions (Q3, Q7, Q18) selected from the Evaluation Questions section
- Output: Top-K retrieved chunks (K = 3 and K = 5) for each method with manual relevance judgement

### Experiment Design
We conduct a small-scale retrieval experiment focusing on evidence recall rather than generation quality.

**Retrieval Methods**
- Sparse retrieval: keyword-based (BM25-style)
- Dense retrieval: embedding-based semantic search

### Query Set
Three representative exam-style questions were selected from the *Evaluation Questions* section to conduct the retrieval experiment. These questions focus on definitions and conceptual understanding commonly tested in Complex Analysis exams:

- **Q3**: What does it mean for a function to be holomorphic on a domain?  
- **Q7**: State the Cauchy–Riemann equations and explain their role in complex differentiability.  
- **Q18**: How are power series used to represent holomorphic functions locally?
  
**Procedure**
For each question, the top-3 retrieved text chunks are collected for each retrieval method.
Retrieved chunks are manually inspected to determine whether they contain sufficient information to answer the question. The results are summarised in a small comparison table to support qualitative analysis.

**Evaluation Criterion**
A retrieval is considered successful if at least one of the top-3 chunks contains the relevant definition, formula, or explanation required by the question.

### Retrieval Results (Evidence Recall)

| Question ID | Retrieval Method | Relevant Chunk Retrieved? (Y/N) | Notes |
|-------------|------------------|----------------------------------|-------|
| Q3 | Sparse (Keyword) | Yes | Definition-related exam solution retrieved, but sometimes embedded in broader exam context (e.g. conformal mapping) |
| Q3 | Dense (TF-IDF) | Partial | Top-ranked chunk may prioritise related concepts over the precise definition |
| Q7 | Sparse (Keyword) | Yes | Explicit statement of the Cauchy–Riemann equations retrieved |
| Q7 | Dense (TF-IDF) | Yes | Correct lecture note section retrieved with contextual explanation |
| Q18 | Sparse (Keyword) | No | Failed to retrieve relevant local power series explanation |
| Q18 | Dense (TF-IDF) | Yes | Relevant explanation of local holomorphic expansion retrieved |

## Expected Results and Failure Analysis

### Expected Results
The hybrid retrieval approach is expected to outperform purely keyword-based retrieval in capturing semantically relevant explanations from lecture notes.
Citation-grounded generation is expected to reduce hallucinated answers and improve trust in exam-oriented responses.

### Failure Analysis
Common failure modes include loss of mathematical symbols during PDF parsing, incomplete retrieval caused by overly coarse text chunking, and ambiguity when similar definitions
appear across multiple lectures.
These observations motivate future improvements in document preprocessing and retrieval strategy design.
An observed failure mode is that top-ranked retrieved chunks may correspond to exam questions that reference a concept (e.g. holomorphic or conformal mappings) rather than the formal
textbook definition itself. This behaviour is particularly evident in sparse retrieval, where strong keyword overlap with past exam questions can outweigh semantic proximity to precise definitions.

## Conclusion and Future Work

This project presents a small-scale, citation-grounded RAG study assistant designed for exam-oriented PDF study. Through controlled retrieval experiments on representative
Complex Analysis questions (Q3, Q7, Q18), we compared sparse keyword-based retrieval with TF-IDF semantic retrieval, focusing on evidence recall rather than generation quality.

Results show that sparse retrieval performs strongly for definition-style questions with high lexical overlap, while TF-IDF semantic retrieval demonstrates advantages on
conceptual questions where relevant explanations do not share exact wording with the query.
However, semantic retrieval may prioritise contextually related material over precise definitions, highlighting a precision–semantic breadth trade-off.

Future work includes incorporating dense embedding models to improve conceptual alignment, introducing reranking mechanisms to better prioritise formal definitions, and exploring
definition-aware query handling to mitigate ambiguity between closely related concepts.
