# AI Engineering Roadmap — 6-Month Build Log

A hands-on journey from Python fundamentals to shipping production-grade, agentic AI systems. Each week has a small, focused project, and every project's README includes a **"What I learned"** section in my own words.

The goal: learn AI engineering by *building*, not just reading — 24 projects across 6 months.

## How this repo is organized

```
month-N-topic/
  week-NN-name/
    <code + sample data>
    README.md   ← what it does, how to run, what I learned
```

## The roadmap

### 🟢 Month 1 — Python, Git & Engineering Basics
| Week | Project | Key skills |
|------|---------|-----------|
| 01 | [Calculator + number guessing game](month-1-python-git-basics/week-01-python-fundamentals/) | variables, types, conditionals, loops, debugging |
| 02 | [Marks analyzer + to-do app](month-1-python-git-basics/week-02-functions-and-data-structures/) | functions, scope, lists/dicts/tuples/sets |
| 03 | [Mini library management system](month-1-python-git-basics/week-03-oop-and-file-handling/) | OOP, inheritance, file I/O (JSON), exceptions |
| 04 | [Weather CLI (public API)](month-1-python-git-basics/week-04-git-github-and-apis/) | Git, REST APIs with `requests`, error handling |

### 🟢 Month 2 — Data, Text & Embeddings Foundations
| Week | Project | Key skills |
|------|---------|-----------|
| 05 | [Dataset analysis with pandas](month-2-data-text-embeddings/week-05-pandas-data-handling/) | load/filter/sort/groupby, EDA |
| 06 | [Data cleaning & prep](month-2-data-text-embeddings/week-06-data-cleaning/) | missing values, duplicates, feature engineering |
| 07 | [Text cleaner + tokenizer](month-2-data-text-embeddings/week-07-text-processing/) | tokenization, stopwords, normalization, regex |
| 08 | [Semantic search over notes](month-2-data-text-embeddings/week-08-embeddings-semantic-search/) | embeddings, cosine similarity, semantic vs keyword |

### 🟡 Month 3 — Generative AI & Prompt Engineering
| Week | Project | Key skills |
|------|---------|-----------|
| 09 | [LLM chatbot](month-3-generative-ai-prompting/week-09-llm-chatbot/) | tokens, context windows, multi-turn state |
| 10 | [Document summarizer](month-3-generative-ai-prompting/week-10-document-summarizer/) | role-based prompting, prompt iteration |
| 11 | [Multi-model API wrapper + cost tracking](month-3-generative-ai-prompting/week-11-multi-model-api-wrapper/) | API errors/retries, token & cost tracking |
| 12 | [LLM PDF data extractor](month-3-generative-ai-prompting/week-12-pdf-data-extractor/) | structured outputs (JSON), parsing |

### 🟡 Month 4 — RAG, Vector Stores & Frameworks
| Week | Project | Key skills |
|------|---------|-----------|
| 13 | [Document chunking pipeline](month-4-rag-vector-stores/week-13-chunking-pipeline/) | chunking strategies, metadata |
| 14 | [Vector search system](month-4-rag-vector-stores/week-14-vector-search/) | embeddings store, similarity at scale |
| 15 | [Document Q&A bot (RAG)](month-4-rag-vector-stores/week-15-document-qa-bot/) | retrieval + generation, context injection, citations |
| 16 | [Production-style RAG with logging](month-4-rag-vector-stores/week-16-production-rag/) | reranking, observability, from-scratch vs frameworks |

### 🔵 Month 5 — Machine Learning Foundations
| Week | Project | Key skills |
|------|---------|-----------|
| 17 | [ML problem definition](month-5-ml-foundations/week-17-ml-problem-definition/) | framing a real problem as an ML task |
| 18 | [Classification model](month-5-ml-foundations/week-18-classification-model/) | train/test split, scikit-learn, model comparison |
| 19 | [Model evaluation report](month-5-ml-foundations/week-19-model-evaluation/) | precision/recall/F1, cross-validation, over/underfitting |
| 20 | [ML-enhanced RAG re-ranker](month-5-ml-foundations/week-20-ml-reranker/) | re-ranking, when fine-tuning is worth it |

### 🔴 Month 6 — Agentic Systems, Production & Capstone
| Week | Project | Key skills |
|------|---------|-----------|
| 21 | [Agentic workflow (tool use)](month-6-agentic-systems/week-21-agentic-workflow/) | agent loop, tool calling, orchestration |
| 22 | [Eval + cost analysis](month-6-agentic-systems/week-22-eval-and-cost-analysis/) | LLM-as-judge, golden datasets, cost/latency |
| 23 | [Deployed app + observability](month-6-agentic-systems/week-23-deployed-app-observability/) | logging, prompt versioning, Docker, responsible AI |
| 24 | [Capstone: end-to-end AI assistant](month-6-agentic-systems/week-24-capstone/) | tying it all together + a one-pager |

## Running the projects

Most projects are self-contained. Each folder's README has exact commands.

- **Months 1–2 & 5** run on Python's standard library or common data libs (`pandas`, `scikit-learn`, `sentence-transformers`).
- **Months 3, 4 (gen step), 6** call the Anthropic API and need an API key:
  ```bash
  pip install -r <project>/requirements.txt
  export ANTHROPIC_API_KEY=sk-ant-...
  ```
  Retrieval (embeddings) in the RAG projects runs locally with `sentence-transformers`, so only the final answer generation needs a key.

## Why I built this

I'm learning AI engineering end-to-end and wanted a public, honest record of the work — real code, real tradeoffs, and what each step actually taught me.
