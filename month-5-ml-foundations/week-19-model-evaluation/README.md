# Week 19 — Model Evaluation

Go beyond accuracy: a full evaluation report with the metrics that actually
matter, plus a hands-on look at overfitting vs. underfitting.

## What it does

`evaluate_model.py` trains a decision tree and then evaluates it properly:

- **Accuracy, precision, recall, and F1** on a held-out test set
- A **confusion matrix** (TN / FP / FN / TP) so you can see *which* errors happen
- **Cross-validation** with `cross_val_score` to check the score is stable, not
  just lucky on one split
- A **depth sweep** that prints train vs. test accuracy as model complexity grows,
  making underfitting and overfitting visible in the numbers

It all prints as a clean text report.

## How to run

```bash
pip install -r requirements.txt
python3 evaluate_model.py
```

## What I learned

- Accuracy on its own is misleading — it can look great while the model quietly
  misses the cases you care about. Precision and recall split that single number
  into "when it says yes, is it right?" vs. "did it catch all the real yeses?"
- The confusion matrix made false positives and false negatives concrete. Seeing the
  four cells laid out is way clearer than any single score, and F1 is just the
  balance of precision and recall when you want one number.
- A single train/test split can be lucky or unlucky. Cross-validation re-splits the
  data k times and averages, and the standard deviation tells you how much to trust
  the mean — that was a genuine "oh, that's why people do CV" moment.
- The depth sweep is the part that stuck: a depth-1 tree underfits (both train and
  test accuracy are low), while an unlimited tree memorizes the training set (train
  near 1.0, test lower, big gap). The best model is where test accuracy peaks.
- Overfitting and underfitting finally feel like two ends of one dial — complexity —
  rather than two unrelated problems, and the train-vs-test gap is how you read it.
