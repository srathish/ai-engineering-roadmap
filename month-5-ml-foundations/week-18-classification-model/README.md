# Week 18 — Classification Model

Train and compare two simple classifiers on a built-in scikit-learn dataset.

## What it does

`train_model.py` loads the Breast Cancer Wisconsin dataset (bundled with
scikit-learn, no download needed), splits it into train/test sets, trains a
**Logistic Regression** and a **Decision Tree**, and prints the test accuracy of
each so you can compare a linear model against a tree-based one.

## How to run

```bash
pip install -r requirements.txt
python3 train_model.py
```

You'll see dataset info, the train/test split sizes, and each model's accuracy.

## What I learned

- Logistic regression is just a linear model with an S-curve squashing the output
  into a probability between 0 and 1 — it draws a straight decision boundary, which
  is surprisingly strong on a lot of real datasets.
- Decision trees think completely differently: they split the data on one feature at
  a time ("is this measurement above X?"), so they handle non-linear patterns but
  happily overfit if you let them grow deep. Capping `max_depth` is a real knob.
- The train/test split finally clicked as the whole point of ML — you score the model
  on data it never saw, otherwise you're just measuring memorization.
- Little details matter: scaling features helped logistic regression converge, and I
  learned to fit the scaler on the training data *only* so test info doesn't leak in.
- `stratify=y` keeps the class balance consistent across the split, which avoids a
  lucky/unlucky split skewing the comparison between the two models.
- Running both models side by side made it concrete that there's no single "best"
  algorithm — the right one depends on the data, and comparing is cheap and worth it.
