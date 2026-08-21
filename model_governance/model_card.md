\# Model Card — PlaceMux Intelligence Layer



\## 1. Model Overview



\*\*Model name:\*\* PlaceMux Intelligence Layer  

\*\*Current production version:\*\* model\_v1  

\*\*Task:\*\* Candidate-job matching and ranking  

\*\*Model type:\*\* Matching / scoring model  

\*\*Registry:\*\* `model\_governance/registry/model\_registry.json`



The model produces a matching score using candidate-job features and supports

selection decisions and plain-English explanations.



\---



\## 2. Intended Use



The model is intended to support:



\- Candidate-job matching

\- Candidate ranking

\- Recruitment decision support

\- Matching score generation

\- Explainable candidate decisions



The model should be used as a decision-support component rather than as the

sole basis for employment decisions.



\---



\## 3. Data



\### Training / Evaluation Data



The intelligence layer uses data from:



`semantic\_search/data/search\_documents.json`



Candidate matching evaluation data is maintained in:



`fairness\_explainability/data/matching\_data.json`



The system also uses feature-level information such as:



\- Skills match

\- Education score

\- Location score

\- Experience



\---



\## 4. Model Metrics



\### Production Model — model\_v1



| Metric | Score |

|---|---:|

| Precision | 0.80 |

| Recall | 0.75 |

| F1 | 0.77 |



\### Candidate Model — model\_v2



| Metric | Score |

|---|---:|

| Precision | 0.85 |

| Recall | 0.81 |

| F1 | 0.83 |



The evaluation gate requires the candidate model's F1 score to be higher than

the currently active production model before promotion.



\---



\## 5. Model Versioning and Lineage



Models are maintained in the model registry.



Each registered model contains:



\- Version

\- Status

\- Metrics

\- Parent model

\- Training data

\- Production status



Example lineage:



`model\_v1 → model\_v2`



A previous production model can be restored through the registry rollback

mechanism.



\---



\## 6. Drift Monitoring



The system monitors production data for distribution changes.



Currently monitored features include:



\- Document count

\- Average text length



A configured threshold determines whether drift is detected.



When drift is detected, the system can trigger the retraining workflow.



Normal data:



`Drift detected: False`



Controlled drift testing:



`Drift detected: True`



\---



\## 7. Retraining and Evaluation Gate



Retraining is only allowed to promote a candidate model after evaluation.



The evaluation gate compares the candidate model's F1 score against the

currently active production model.



A candidate model with a lower F1 score is rejected.



This prevents automatic promotion of a degraded model.



\---



\## 8. Fairness



Fairness was evaluated as part of Task 14.



The system measures:



\- Selection rate

\- True positive rate

\- Demographic parity ratio

\- Equal opportunity gap



Fairness mitigation was applied and evaluated using the candidate matching

data.



After mitigation, the evaluated groups achieved balanced selection rates and

true positive rates.



See:



`fairness\_explainability/reports/bias\_audit\_report.json`



and



`fairness\_explainability/reports/mitigation\_report.json`



\---



\## 9. Explainability



The system provides a plain-English explanation for individual candidate

decisions.



The explanation includes:



\- Candidate identifier

\- Decision

\- Matching score

\- Skills contribution

\- Education contribution

\- Location contribution

\- Experience



The explanation service is available through the `/explain` API endpoint.



\---



\## 10. Limitations



The model has several limitations:



1\. Evaluation results depend on the available evaluation dataset.

2\. Historical or biased data can affect model behavior.

3\. Drift thresholds are configured and may require adjustment as production

&#x20;  data changes.

4\. Fairness metrics depend on the groups and labels available in the data.

5\. Model scores should not be interpreted as guarantees of candidate success.

6\. The system should not be used as the sole decision-maker for high-impact

&#x20;  employment decisions.

7\. Retraining quality depends on the quality and representativeness of new

&#x20;  data.



\---



\## 11. Monitoring and Governance



The production model is governed through:



\- Model registry

\- Version tracking

\- Model lineage

\- Drift monitoring

\- Retraining triggers

\- Evaluation gates

\- Rollback capability

\- Fairness auditing

\- Per-decision explanations



These controls are intended to make model behavior traceable, monitored,

explainable, and recoverable.

