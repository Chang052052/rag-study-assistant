# rag-study-assistant
A citation-grounded RAG demo for exam-oriented PDF study
# A Citation-Grounded RAG Study Assistant for Exam-Oriented PDF Study

## Note
This repository presents a small research-oriented demo of a retrieval-augmented generation (RAG) system.
The focus is on system design, retrieval strategies, and evaluation, rather than full system deployment.

## Problem
Students preparing for exams rely heavily on fragmented PDF lecture notes and past papers.
Traditional keyword-based search makes it difficult to locate precise explanations or relevant
examples, while large language models may hallucinate answers without reliable sources.

## Objective
The goal of this project is to design a retrieval-augmented generation (RAG) study assistant
that answers exam-related questions strictly based on retrieved PDF evidence, with explicit
citations to the source documents.

## Data
The system indexes 10–20 course PDFs, including Analysis III (Complex Analysis) lecture notes,
tutorial sheets, and past exam papers. Each document is treated as an authoritative knowledge
source for answering queries.

## Method
The proposed system follows a retrieval-augmented pipeline:
- Document segmentation into manageable text chunks  
- Hybrid retrieval using sparse (BM25) and dense embedding-based methods  
- Reranking of retrieved candidates  
- Evidence-grounded answer generation with explicit source citations  

## Evaluation Plan
The system is evaluated using a manually curated set of exam-style questions.
Evaluation focuses on evidence recall, answer usefulness, and common failure modes such as
missing relevant chunks or ambiguous retrieval results.

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

**Setup**
- Data: a subset of the Complex Analysis PDFs in `docs/`
- Query set: 5 exam-style questions (from the Evaluation Questions section)
- Output: Top-3 retrieved chunks for each method + a small result table (manual judgement)

**What counts as success?**
- Each question retrieves at least one relevant chunk that contains the definition/formula/explanation needed.

## Expected Results and Failure Analysis

### Expected Results
The hybrid retrieval approach is expected to outperform purely keyword-based retrieval in
capturing semantically relevant explanations from lecture notes.
Citation-grounded generation is expected to reduce hallucinated answers and improve trust
in exam-oriented responses.

### Failure Analysis
Common failure modes include loss of mathematical symbols during PDF parsing, incomplete
retrieval caused by overly coarse text chunking, and ambiguity when similar definitions
appear across multiple lectures.
These observations motivate future improvements in document preprocessing and retrieval
strategy design.
