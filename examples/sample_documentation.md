# E-commerce Performance — Analyst Reference

## Scope

- Vertical: Fashion (apparel + accessories)
- Channel: Direct-to-consumer website + app, India
- Currency: INR
- Reporting period: calendar month
- All figures are already aggregated — do not recompute from raw orders.

## Metric definitions

| Metric | Definition |
|---|---|
| **GMV** | Gross Merchandise Value. Total order value before returns, discounts already applied. |
| **Orders** | Count of placed orders (one order can contain multiple items). |
| **AOV** | Average Order Value = GMV / Orders. |
| **Sessions** | Unique site + app visits. |
| **CVR** | Conversion rate = Orders / Sessions. |
| **Return rate** | Items returned / items shipped, attributed to the shipping month. |

## Healthy benchmarks (fashion D2C, India)

| Metric | Healthy band | Flag if... |
|---|---|---|
| CVR | 1.8% – 2.2% | < 1.6% or > 2.6% |
| AOV | ₹1,400 – ₹1,600 | swing > ₹150 MoM |
| Return rate | 7% – 10% | > 12% sustained for 2+ months |
| GMV MoM growth | –5% to +15% (non-sale months) | > +30% → likely sale-event driven |

## Known caveats

1. **Sale-month distortion** — Big Billion Days / End-of-Season Sale months
   inflate GMV and orders but depress AOV (discount-led basket mix).
   Compare sale months to the prior year's sale month, not to the
   immediately adjacent non-sale months.
2. **Return-lag** — Returns are reported against the **shipping** month.
   Returns from a given month continue to trickle in for up to 90 days,
   so the most recent month's return rate is an under-estimate.
3. **New-SKU dilution** — When a new category launches, CVR dips for
   1–2 months as browsing exceeds purchase intent.
4. **App vs. web split** — App typically has ~1.5× the CVR of web; a
   shift in traffic mix can move blended CVR without any real change
   in user behaviour.

## Glossary

- **GMV** — gross merchandise value
- **AOV** — average order value
- **CVR** — conversion rate (orders / sessions)
- **RR** — return rate
- **MoM** — month over month
- **YoY** — year over year
- **SKU** — stock keeping unit (individual product variant)
- **D2C** — direct-to-consumer

## When in doubt

Prefer quantitative statements tied to the data ("GMV rose 71% from Mar to
Apr") over qualitative ones ("sales were strong"). If a caveat applies
to a month, flag it explicitly rather than drawing conclusions through it.
