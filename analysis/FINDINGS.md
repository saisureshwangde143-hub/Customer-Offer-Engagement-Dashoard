# RewardsNext - Customer Offer Engagement: Findings

Generated from 17,000 customers, 76,277 offer deliveries, 138,953 transactions.


## 1. Headline KPIs

| Metric                                         | Value          |
| ---------------------------------------------- | -------------- |
| Total customers                                | 17,000         |
| Customers targeted                             | 16,994         |
| Offers sent (deliveries)                       | 76,277         |
| Offers viewed                                  | 56,350         |
| View rate                                      | 73.9%          |
| Promotional offers sent (excl. informational)  | 61,042         |
| Offers completed                               | 32,710         |
| Redemption rate (completed / promotional sent) | 53.6%          |
| Naive redemption rate (completed / all sent)   | 42.9%          |
| Influenced redemption (viewed then completed)  | 22,971 (37.6%) |
| Completed without viewing                      | 9,739          |
| Total spend                                    | $1,775,452     |
| Transactions                                   | 138,953        |
| Average transaction                            | $12.78         |


## 2. Offer funnel

| Stage           | Volume | Pct of received |
| --------------- | ------ | --------------- |
| Offer received  | 76277  | 1.000           |
| Offer viewed    | 56350  | 0.739           |
| Offer completed | 32710  | 0.429           |

| offer_type    | sent  | viewed | completed | view_rate | redemption_rate |
| ------------- | ----- | ------ | --------- | --------- | --------------- |
| bogo          | 30499 | 25206  | 15263     | 0.826     | 0.500           |
| discount      | 30543 | 21362  | 17447     | 0.699     | 0.571           |
| informational | 15235 | 9782   | 0         | 0.642     |                 |


## 3. Offer performance

| offer_label         | offer_type | difficulty | reward | duration | channel_count | sent | view_rate | redemption_rate | influenced_rate | unviewed_completions | avg_hours_to_complete |
| ------------------- | ---------- | ---------- | ------ | -------- | ------------- | ---- | --------- | --------------- | --------------- | -------------------- | --------------------- |
| Discount 2/10 (10d) | discount   | 10         | 2      | 10       | 4             | 7597 | 0.964     | 0.686           | 0.600           | 654                  | 71.494                |
| Discount 3/7 (7d)   | discount   | 7          | 3      | 7        | 4             | 7646 | 0.959     | 0.661           | 0.562           | 754                  | 55.902                |
| Bogo 5/5 (7d)       | bogo       | 5          | 5      | 7        | 3             | 7677 | 0.537     | 0.554           | 0.271           | 2171                 | 56.796                |
| Bogo 5/5 (5d)       | bogo       | 5          | 5      | 5        | 4             | 7571 | 0.950     | 0.551           | 0.453           | 742                  | 40.679                |
| Discount 2/10 (7d)  | discount   | 10         | 2      | 7        | 3             | 7632 | 0.531     | 0.511           | 0.272           | 1824                 | 62.327                |
| Bogo 10/10 (7d)     | bogo       | 10         | 10     | 7        | 3             | 7658 | 0.872     | 0.470           | 0.333           | 1043                 | 53.234                |
| Discount 5/20 (10d) | discount   | 20         | 5      | 10       | 2             | 7668 | 0.346     | 0.428           | 0.169           | 1990                 | 100.282               |
| Bogo 10/10 (5d)     | bogo       | 10         | 10     | 5        | 4             | 7593 | 0.951     | 0.427           | 0.353           | 561                  | 40.925                |

| offer_label            | duration | channel_count | sent | view_rate | avg_hours_to_view |
| ---------------------- | -------- | ------------- | ---- | --------- | ----------------- |
| Informational 0/0 (3d) | 3        | 3             | 7618 | 0.792     | 19.454            |
| Informational 0/0 (4d) | 4        | 3             | 7617 | 0.493     | 25.219            |


## 4. Effect of difficulty and reward

| difficulty | sent  | view_rate | redemption_rate |
| ---------- | ----- | --------- | --------------- |
| 5          | 15248 | 0.742     | 0.553           |
| 7          | 7646  | 0.959     | 0.661           |
| 10         | 30480 | 0.829     | 0.523           |
| 20         | 7668  | 0.346     | 0.428           |

| reward | sent  | view_rate | redemption_rate |
| ------ | ----- | --------- | --------------- |
| 2      | 15229 | 0.747     | 0.598           |
| 3      | 7646  | 0.959     | 0.661           |
| 5      | 22916 | 0.609     | 0.511           |
| 10     | 15251 | 0.911     | 0.448           |

| duration | sent  | view_rate | redemption_rate |
| -------- | ----- | --------- | --------------- |
| 5        | 15164 | 0.950     | 0.489           |
| 7        | 30613 | 0.725     | 0.549           |
| 10       | 15265 | 0.654     | 0.556           |


## 5. Channel mix

| channel | deliveries | view_rate | redemption_rate |
| ------- | ---------- | --------- | --------------- |
| social  | 38065      | 0.939     | 0.559           |
| mobile  | 53374      | 0.823     | 0.551           |
| web     | 53384      | 0.747     | 0.545           |
| email   | 61042      | 0.763     | 0.536           |

_Channels overlap: one offer uses several, so these are not independent. The combination column below is the cleaner read._

| channels_text              | deliveries | view_rate | redemption_rate |
| -------------------------- | ---------- | --------- | --------------- |
| email, mobile, social, web | 30407      | 0.956     | 0.581           |
| email, mobile, web         | 15309      | 0.534     | 0.532           |
| email, mobile, social      | 7658       | 0.872     | 0.470           |
| email, web                 | 7668       | 0.346     | 0.428           |


## 6. Customer segmentation

### By gender
| gender_clean  | customers | offers_sent | view_rate | redemption_rate |
| ------------- | --------- | ----------- | --------- | --------------- |
| Female        | 6103      | 21918       | 0.764     | 0.691           |
| Male          | 8450      | 30562       | 0.748     | 0.524           |
| Not Disclosed | 2164      | 7841        | 0.811     | 0.136           |
| Other         | 211       | 721         | 0.849     | 0.681           |

### By age group
| age_group | customers | offers_sent | view_rate | redemption_rate |
| --------- | --------- | ----------- | --------- | --------------- |
| 18-25     | 1009      | 3647        | 0.690     | 0.454           |
| 26-35     | 1354      | 4985        | 0.704     | 0.485           |
| 36-45     | 1971      | 7068        | 0.787     | 0.569           |
| 46-55     | 3119      | 11144       | 0.767     | 0.619           |
| 56-65     | 3342      | 12151       | 0.763     | 0.631           |
| 66-75     | 2325      | 8368        | 0.759     | 0.621           |
| 76+       | 1644      | 5838        | 0.761     | 0.649           |
| Unknown   | 2164      | 7841        | 0.811     | 0.136           |

### By income band
| income_band | customers | offers_sent | view_rate | redemption_rate |
| ----------- | --------- | ----------- | --------- | --------------- |
| 100k+       | 1003      | 3637        | 0.678     | 0.758           |
| 40-60k      | 4542      | 16293       | 0.750     | 0.521           |
| 60-80k      | 4545      | 16342       | 0.780     | 0.631           |
| 80-100k     | 2549      | 9141        | 0.810     | 0.747           |
| <40k        | 2125      | 7788        | 0.691     | 0.420           |
| Unknown     | 2164      | 7841        | 0.811     | 0.136           |

### By tenure
| tenure_band | customers | offers_sent | view_rate | redemption_rate |
| ----------- | --------- | ----------- | --------- | --------------- |
| 1-2 yr      | 3442      | 12298       | 0.768     | 0.722           |
| 2-3 yr      | 3442      | 12422       | 0.768     | 0.712           |
| 3+ yr       | 1372      | 4929        | 0.758     | 0.523           |
| <1 yr       | 8672      | 31393       | 0.760     | 0.395           |

### By membership year
| membership_year | customers | offers_sent | view_rate | redemption_rate |
| --------------- | --------- | ----------- | --------- | --------------- |
| 2013            | 284       | 1029        | 0.759     | 0.537           |
| 2014            | 688       | 2473        | 0.767     | 0.522           |
| 2015            | 1823      | 6589        | 0.757     | 0.662           |
| 2016            | 3509      | 12572       | 0.772     | 0.724           |
| 2017            | 6441      | 23178       | 0.761     | 0.530           |
| 2018            | 4183      | 15201       | 0.760     | 0.336           |

### Heatmap: redemption rate by age group x income band
| age_group | 100k+ | 40-60k | 60-80k | 80-100k | <40k  | Unknown |
| --------- | ----- | ------ | ------ | ------- | ----- | ------- |
| 18-25     |       | 0.464  | 0.497  |         | 0.399 |         |
| 26-35     |       | 0.489  | 0.517  |         | 0.445 |         |
| 36-45     |       | 0.547  | 0.624  | 0.745   | 0.397 |         |
| 46-55     | 0.748 | 0.538  | 0.649  | 0.751   | 0.408 |         |
| 56-65     | 0.768 | 0.538  | 0.672  | 0.728   | 0.399 |         |
| 66-75     | 0.751 | 0.512  | 0.638  | 0.755   | 0.445 |         |
| 76+       | 0.761 | 0.522  | 0.668  | 0.769   | 0.486 |         |
| Unknown   |       |        |        |         |       | 0.136   |


## 7. Engagement segments

| engagement_segment | customers | avg_offers_received | avg_completion_rate | avg_total_spend | avg_txn_value | total_spend   | pct_of_revenue |
| ------------------ | --------- | ------------------- | ------------------- | --------------- | ------------- | ------------- | -------------- |
| Champion           | 8258      | 4.472               | 0.729               | 170.546         | 19.309        | 1,408,367.400 | 0.793          |
| Occasional         | 4436      | 4.688               | 0.286               | 64.996          | 11.221        | 288,321.210   | 0.162          |
| Browser            | 4183      | 4.348               | 0.000               | 18.239          | 4.468         | 76,293.210    | 0.043          |
| Dormant            | 117       | 3.103               | 0.000               | 18.970          | 6.021         | 2,219.540     | 0.001          |
| Not Targeted       | 6         | 0.000               |                     | 41.768          | 11.583        | 250.610       | 0.000          |


## 8. Transaction behaviour

| Context                         | Avg transaction | Transactions | Total spend   |
| ------------------------------- | --------------- | ------------ | ------------- |
| Inside a viewed offer window    | 12.897          | 108054       | 1,393,579.650 |
| Inside an unviewed offer window | 11.917          | 12139        | 144,662.240   |
| Outside any offer window        | 12.644          | 18760        | 237,210.080   |

| Period                  | Avg transaction | Transactions | Total spend   |
| ----------------------- | --------------- | ------------ | ------------- |
| Before first completion | 7.836           | 23844        | 186,845.820   |
| After first completion  | 16.106          | 93743        | 1,509,842.790 |

_Same customers on both sides, so the comparison controls for who they are - but not for time-in-window, so read it as directional, not causal._

| is_completer | customers | avg_total_spend | avg_txn_value | avg_txn_count |
| ------------ | --------- | --------------- | ------------- | ------------- |
| False        | 4306      | 18.292          | 4.521         | 4.962         |
| True         | 12694     | 133.661         | 16.483        | 9.263         |

Daily spend curve written to `analysis/daily_spend.csv` (30 days, peak day 25).


## 9. Data quality flags

| Flag                                     | Count   | Meaning                                                                                               |
| ---------------------------------------- | ------- | ----------------------------------------------------------------------------------------------------- |
| Customers with placeholder age 118       | 2,175   | Same 2,175 rows also lack gender and income - one incomplete-profile cohort, not three separate gaps. |
| Completions attributed to no open window | 869     | Completion fell outside the offer's validity window; excluded from journey facts.                     |
| Views attributed to no open window       | 1,375   | Same cause. Both are <2% of their event type.                                                         |
| Completions without a prior view         | 9,739   | Customer met the spend threshold without opening the offer - reward paid, no marketing influence.     |
| Informational offers                     | 2 of 10 | Cannot be 'completed'. Including them in the denominator understates redemption by ~9pp.              |
