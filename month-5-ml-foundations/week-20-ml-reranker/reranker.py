"""
Week 20 - A small ML-enhanced re-ranker for RAG.

In a RAG pipeline you first retrieve candidate passages with a cheap similarity
score (e.g. vector search). That first-pass ranking is fast but crude. A
*re-ranker* then re-scores the top candidates more carefully and reorders them so
the best passages float to the top before they're handed to the LLM.

This script:
  1. Starts from naive similarity scores (the "before" ranking).
  2. Builds simple features per (query, passage): similarity, keyword overlap,
     and a length signal.
  3. Re-scores with a learned model when scikit-learn is available, training a
     tiny LogisticRegression on a few labeled examples; otherwise it falls back
     to a transparent feature-weighted heuristic.
  4. Prints the before/after ranking so you can see what moved.

Run:
    python3 reranker.py
"""

import math
import re

# ---------------------------------------------------------------------------
# Demo data: a query and candidate passages, each with a naive similarity score
# from a hypothetical first-pass vector search, plus a relevance label used only
# to train the tiny re-ranker (1 = relevant, 0 = not).
# ---------------------------------------------------------------------------

QUERY = "How do I reset my account password?"

CANDIDATES = [
    # (passage_text, naive_similarity, is_relevant)
    ("To reset your password, open Settings, click Security, then "
     "Reset Password and follow the email link.", 0.61, 1),
    ("Our company was founded in 2014 and has offices in three countries.",
     0.66, 0),
    ("If you forgot your password, use the 'Forgot password' link on the "
     "login page to receive a reset email.", 0.58, 1),
    ("Passwords must be at least 12 characters and include a number.",
     0.64, 0),
    ("Account billing is handled monthly; update your card under Billing.",
     0.55, 0),
    ("You can change or reset your password anytime from the account "
     "security page.", 0.52, 1),
]


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

def tokenize(text):
    """Lowercase word tokens, used for keyword-overlap features."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def keyword_overlap(query, passage):
    """Fraction of query words that appear in the passage (0..1)."""
    q = tokenize(query)
    p = tokenize(passage)
    if not q:
        return 0.0
    return len(q & p) / len(q)


def length_signal(passage):
    """A squashed length feature.

    Very short passages are often unhelpful and very long ones are noisy; a log
    keeps the value in a reasonable range so it doesn't dominate.
    """
    return math.log1p(len(passage.split()))


def build_features(query, passage, similarity):
    """Turn a (query, passage) pair into a small feature vector."""
    return [
        similarity,                        # first-pass vector similarity
        keyword_overlap(query, passage),   # lexical overlap with the query
        length_signal(passage),            # length signal
    ]


# ---------------------------------------------------------------------------
# Re-rankers: learned model preferred, heuristic fallback
# ---------------------------------------------------------------------------

def rerank_with_model(query, candidates):
    """Train a tiny LogisticRegression re-ranker and score each candidate.

    Returns a list of (passage, new_score) or None if scikit-learn is missing.
    In a real system you'd train on far more (query, passage, label) data; here
    we use the handful of labels just to demonstrate the mechanism.
    """
    try:
        from sklearn.linear_model import LogisticRegression
    except ImportError:
        return None

    X = [build_features(query, p, sim) for (p, sim, _) in candidates]
    y = [label for (_, _, label) in candidates]

    model = LogisticRegression()
    model.fit(X, y)

    # Probability of the "relevant" class becomes the new ranking score.
    scores = model.predict_proba(X)[:, 1]
    return [(candidates[i][0], float(scores[i])) for i in range(len(candidates))]


def rerank_with_heuristic(query, candidates):
    """Transparent feature-weighted fallback when no ML library is available.

    Weights are hand-set to favor keyword overlap (a strong relevance signal)
    while still respecting the first-pass similarity.
    """
    w_similarity, w_overlap, w_length = 0.4, 0.8, 0.05
    out = []
    for (passage, similarity, _) in candidates:
        sim, overlap, length = build_features(query, passage, similarity)
        score = w_similarity * sim + w_overlap * overlap + w_length * length
        out.append((passage, score))
    return out


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def shorten(text, width=58):
    return text if len(text) <= width else text[: width - 1] + "…"


def print_ranking(title, ranked):
    print(title)
    print("-" * 72)
    for rank, (passage, score) in enumerate(ranked, start=1):
        print(f"  {rank}. [{score:.3f}] {shorten(passage)}")
    print()


def main():
    print("=" * 72)
    print("Week 20 - ML-enhanced re-ranker for RAG")
    print(f"Query: {QUERY}")
    print("=" * 72)
    print()

    # BEFORE: order by the naive first-pass similarity score.
    before = sorted(
        [(p, sim) for (p, sim, _) in CANDIDATES],
        key=lambda x: x[1],
        reverse=True,
    )
    print_ranking("BEFORE  (naive vector similarity)", before)

    # AFTER: re-score with the learned model, falling back to the heuristic.
    rescored = rerank_with_model(QUERY, CANDIDATES)
    if rescored is not None:
        method = "learned LogisticRegression re-ranker"
    else:
        rescored = rerank_with_heuristic(QUERY, CANDIDATES)
        method = "feature-weighted heuristic (scikit-learn not installed)"

    after = sorted(rescored, key=lambda x: x[1], reverse=True)
    print_ranking(f"AFTER   ({method})", after)

    print("=" * 72)
    print("The re-ranker pushes passages that actually describe resetting a")
    print("password above superficially-similar ones (password *rules*, company")
    print("history) that the first-pass similarity ranked too highly.")
    print("=" * 72)


if __name__ == "__main__":
    main()
