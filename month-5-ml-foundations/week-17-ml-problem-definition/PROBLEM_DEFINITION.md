# ML Problem Definition: Customer Churn Prediction

A structured definition of a realistic machine learning project, written before any
model is built. The goal is to decide whether ML is the right tool, frame the problem
correctly, and agree on how we'll know if it worked.

---

## 1. Problem statement

A subscription SaaS business (monthly billing) is losing customers. Right now the team
only finds out a customer left *after* they cancel, which is too late to do anything
about it. The business wants to know **which active customers are likely to cancel in
the next 30 days**, so the success team can reach out with retention offers before the
customer is gone.

In plain terms: *given what we know about a customer today, how likely are they to
churn within the next month?*

## 2. Is this actually an ML problem? Could a rule work?

This is the most important question to answer before writing any code.

**A rule-based approach is the honest first thing to try.** For example:
> "Flag any customer who hasn't logged in for 14+ days AND has an open support ticket."

Simple rules like this are cheap, explainable, and often catch the obvious cases. If a
handful of rules already catch most churners, **we should not build an ML model at all** —
the maintenance cost isn't worth it.

ML becomes the better choice when:
- Churn depends on *many* weak signals interacting (usage trend + plan type + tenure +
  support history + payment failures), not one or two thresholds.
- Those interactions are hard to write down as rules by hand, and the patterns drift
  over time as the product changes.
- We have enough historical labeled data (customers who *did* and *didn't* churn) to
  learn from.

For this project I'm assuming we've already tried obvious rules and they leave too many
churners undetected — so a model that weighs many signals together is justified. If that
assumption turned out to be false, the right call would be to ship the rules and stop.

## 3. Supervised vs. unsupervised framing

This is a **supervised learning** problem, specifically **binary classification**.

- *Supervised*: we have historical examples where we know the outcome — each past
  customer either churned or didn't. The model learns the mapping from features to that
  known label.
- *Classification, not regression*: the answer is a category (churn / no-churn), not a
  continuous number. We will, however, use the model's predicted **probability** of
  churn so the team can prioritize the highest-risk customers.

Unsupervised learning (e.g., clustering customers into segments) could be a useful
*exploratory* step to understand the customer base, but it can't directly answer "will
this specific customer churn?" because it has no labels to learn from.

## 4. Target variable (label)

**`churned_30d`** — a binary label, defined as:
- `1` if the customer cancelled their subscription within 30 days of the snapshot date.
- `0` if they remained active through that window.

Careful definition matters:
- We must pick a fixed **snapshot date** per customer and only use information available
  *as of that date* to build features (avoiding "time leakage" — see risks).
- "Churn" must be defined precisely: is a downgrade churn? Is a failed payment that later
  recovers churn? For this project, churn = subscription fully cancelled. Downgrades and
  recovered payments are *not* churn.

## 5. Features (model inputs)

Each feature is something we can compute *at the snapshot date* without peeking into the
future.

| Feature | Why it might predict churn |
|---|---|
| `tenure_months` | Brand-new and very old customers churn for different reasons |
| `plan_type` | Cheaper/free-trial plans churn more than committed annual plans |
| `logins_last_30d` | Drop in engagement is a classic early warning |
| `login_trend` | Declining usage (this month vs. last) signals disengagement |
| `feature_adoption_count` | Customers using more of the product tend to stay |
| `support_tickets_last_90d` | High friction / unresolved issues drive churn |
| `avg_ticket_resolution_hrs` | Slow support correlates with frustration |
| `failed_payments_last_90d` | Billing problems often precede cancellation |
| `monthly_spend` | Higher-value customers may behave differently |
| `nps_or_csat_last_response` | Direct satisfaction signal, when available |

We deliberately **exclude** anything that is only known *because* the customer churned
(e.g., "cancellation reason") — those are leakage.

## 6. Data sources

- **Billing system** — subscription start/end dates (defines the label), plan type,
  spend, payment failures.
- **Product analytics / event logs** — logins, feature usage, usage trends.
- **Support / helpdesk system** — ticket counts, resolution times.
- **Survey tool** — NPS/CSAT responses (sparse; many customers won't have one).

These need to be joined per customer on a stable customer ID, and snapshotted at a
consistent point in time so features and label line up correctly.

## 7. Success metrics

We need *two* layers of metrics: model metrics and business metrics.

**Model metrics** (the dataset is imbalanced — most customers don't churn — so plain
accuracy is misleading):
- **Recall on the churn class** — of the customers who actually churned, how many did we
  flag? This is what the retention team cares about most.
- **Precision on the churn class** — of the customers we flagged, how many actually
  churned? Low precision wastes the team's outreach time.
- **F1 / PR-AUC** — to balance the two and to compare models fairly on imbalanced data.

**Business metric (the real goal):**
- **Net revenue retained** from successful interventions, minus the cost of outreach and
  any discounts given. The model is only worth it if saved revenue exceeds that cost.

We'll pick an operating threshold by trading off precision vs. recall against how many
customers the team realistically has capacity to contact each week.

## 8. Baseline

Before claiming the model "works," we compare it against simple baselines:
1. **Majority-class baseline** — predict "no one churns." This gets high accuracy but
   zero recall, and shows why accuracy alone is useless here.
2. **Rule-based baseline** — the hand-written rules from Section 2 (e.g., inactive +
   open ticket). This is the bar the model must clearly beat to justify its complexity.

A model that doesn't beat the rule baseline on recall *at equal precision* is not worth
shipping.

## 9. Risks and things that can go wrong

- **Data leakage** — accidentally including post-churn information (cancellation reason,
  final-month behavior) inflates offline metrics and collapses in production. Strict
  snapshot discipline is the main defense.
- **Class imbalance** — churners are rare; naive training will just predict "no churn."
  Mitigate with class weighting, resampling, and the right metrics (recall/PR-AUC).
- **Concept drift** — customer behavior and the product change over time, so a model
  trained on last year's data decays. Plan to monitor and retrain.
- **Acting on predictions changes the outcome** — if outreach actually prevents churn,
  the label distribution shifts and future evaluation gets harder to interpret.
- **Fairness / unintended bias** — make sure "risk" isn't a proxy for something we
  shouldn't act on; retention offers should be applied consistently.
- **Cost of being wrong** — a false positive wastes a discount; a false negative loses a
  customer. These costs aren't equal and should shape the threshold, not just F1.

---

### Summary

This is a supervised binary classification problem predicting 30-day churn, justified
*only if* simple rules have already proven insufficient. Success is measured primarily by
recall and precision on the rare churn class — and ultimately by net revenue retained —
benchmarked against a majority-class and a rule-based baseline, with data leakage and
class imbalance as the biggest risks to watch.
