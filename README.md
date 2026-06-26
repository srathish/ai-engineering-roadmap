# AI Engineering Roadmap

A hands-on journey from Python fundamentals to shipping production-grade, agentic AI systems. Each stage has small, focused projects, and every project's README includes a **"What I learned"** section in my own words.

The goal: learn AI engineering by *building*, not just reading — 24 projects across six skill areas.

## How this repo is organized

```
NN-skill-area/
  week-NN-name/
    <code + sample data>
    README.md   ← what it does, how to run, what I learned
```

## The roadmap

### 🟢 Engineering Foundations
| Project | Key skills |
|---------|-----------|
| [Calculator + number guessing game](01-engineering-foundations/week-01-python-fundamentals/) | variables, types, conditionals, loops, debugging |
| [Marks analyzer + to-do app](01-engineering-foundations/week-02-functions-and-data-structures/) | functions, scope, lists/dicts/tuples/sets |
| [Mini library management system](01-engineering-foundations/week-03-oop-and-file-handling/) | OOP, inheritance, file I/O (JSON), exceptions |
| [Weather CLI (public API)](01-engineering-foundations/week-04-git-github-and-apis/) | Git, REST APIs with `requests`, error handling |

### 🟢 Data & Embeddings
| Project | Key skills |
|---------|-----------|
| [Dataset analysis with pandas](02-data-and-embeddings/week-05-pandas-data-handling/) | load/filter/sort/groupby, EDA |
| [Data cleaning & prep](02-data-and-embeddings/week-06-data-cleaning/) | missing values, duplicates, feature engineering |
| [Text cleaner + tokenizer](02-data-and-embeddings/week-07-text-processing/) | tokenization, stopwords, normalization, regex |
| [Semantic search over notes](02-data-and-embeddings/week-08-embeddings-semantic-search/) | embeddings, cosine similarity, semantic vs keyword |

### 🟡 Generative AI & Prompting
| Project | Key skills |
|---------|-----------|
| [LLM chatbot](03-generative-ai-and-prompting/week-09-llm-chatbot/) | tokens, context windows, multi-turn state |
| [Document summarizer](03-generative-ai-and-prompting/week-10-document-summarizer/) | role-based prompting, prompt iteration |
| [Multi-model API wrapper + cost tracking](03-generative-ai-and-prompting/week-11-multi-model-api-wrapper/) | API errors/retries, token & cost tracking |
| [LLM PDF data extractor](03-generative-ai-and-prompting/week-12-pdf-data-extractor/) | structured outputs (JSON), parsing |

### 🟡 Retrieval-Augmented Generation (RAG)
| Project | Key skills |
|---------|-----------|
| [Document chunking pipeline](04-retrieval-augmented-generation/week-13-chunking-pipeline/) | chunking strategies, metadata |
| [Vector search system](04-retrieval-augmented-generation/week-14-vector-search/) | embeddings store, similarity at scale |
| [Document Q&A bot (RAG)](04-retrieval-augmented-generation/week-15-document-qa-bot/) | retrieval + generation, context injection, citations |
| [Production-style RAG with logging](04-retrieval-augmented-generation/week-16-production-rag/) | reranking, observability, from-scratch vs frameworks |

### 🔵 Machine Learning Foundations
| Project | Key skills |
|---------|-----------|
| [ML problem definition](05-machine-learning-foundations/week-17-ml-problem-definition/) | framing a real problem as an ML task |
| [Classification model](05-machine-learning-foundations/week-18-classification-model/) | train/test split, scikit-learn, model comparison |
| [Model evaluation report](05-machine-learning-foundations/week-19-model-evaluation/) | precision/recall/F1, cross-validation, over/underfitting |
| [ML-enhanced RAG re-ranker](05-machine-learning-foundations/week-20-ml-reranker/) | re-ranking, when fine-tuning is worth it |

### 🔴 Agentic Systems & Production
| Project | Key skills |
|---------|-----------|
| [Agentic workflow (tool use)](06-agentic-systems-and-production/week-21-agentic-workflow/) | agent loop, tool calling, orchestration |
| [Eval + cost analysis](06-agentic-systems-and-production/week-22-eval-and-cost-analysis/) | LLM-as-judge, golden datasets, cost/latency |
| [Deployed app + observability](06-agentic-systems-and-production/week-23-deployed-app-observability/) | logging, prompt versioning, Docker, responsible AI |
| [Capstone: end-to-end AI assistant](06-agentic-systems-and-production/week-24-capstone/) | tying it all together + a one-pager |

## Running the projects

Most projects are self-contained. Each folder's README has exact commands.

- **Engineering Foundations, Data & Embeddings, and ML Foundations** run on Python's standard library or common data libs (`pandas`, `scikit-learn`, `sentence-transformers`).
- **Generative AI, RAG (generation step), and Agentic Systems** call the Anthropic API and need an API key:
  ```bash
  pip install -r <project>/requirements.txt
  export ANTHROPIC_API_KEY=sk-ant-...
  ```
  Retrieval (embeddings) in the RAG projects runs locally with `sentence-transformers`, so only the final answer generation needs a key.

## Why I built this

I'm learning AI engineering end-to-end and wanted a public, honest record of the work — real code, real tradeoffs, and what each step actually taught me.
