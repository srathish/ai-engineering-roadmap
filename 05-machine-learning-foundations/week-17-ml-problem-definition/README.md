# Week 17 — ML Problem Definition

This week's build is a **document, not code**: a complete machine learning problem
definition for a realistic project (predicting customer churn for a subscription SaaS).

## What it does

Walks through how to frame a real-world situation as an ML task *before* building
anything: the problem statement, whether ML is even the right tool (or a rule would do),
supervised vs. unsupervised framing, the target variable, candidate features, data
sources, success metrics, baselines to beat, and the risks involved.

See **[PROBLEM_DEFINITION.md](./PROBLEM_DEFINITION.md)** for the full write-up.

## How to run

There's nothing to run — it's a written deliverable. Just open the document:

```bash
open PROBLEM_DEFINITION.md   # or read it on GitHub
```

## What I learned

- The hardest part of ML isn't the model — it's deciding whether you even need one. I
  kept wanting to jump to "train a classifier," but forcing myself to ask "could a rule
  do this?" first changed how I think about every problem.
- I finally internalized the difference between supervised and unsupervised: it comes
  down to whether you have labels. Churn has clear past outcomes, so it's supervised, and
  because the answer is a category it's specifically classification.
- Defining the target variable precisely is sneakily important. "What counts as churn?"
  (is a downgrade churn? a recovered failed payment?) has to be nailed down or the labels
  are garbage.
- Accuracy is a trap on imbalanced problems. Writing out the metrics section made it
  obvious why recall and precision on the rare class matter more than overall accuracy.
- Baselines aren't a formality — a model has to *beat the rules* to be worth its
  complexity, and "predict the majority class" is the embarrassingly simple bar to clear.
- Leakage scared me the most once I understood it: using any information that only exists
  *because* the customer churned makes the offline numbers look amazing and the real
  system useless.
