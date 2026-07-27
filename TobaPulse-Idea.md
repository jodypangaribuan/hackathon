# TobaPulse

## AI Early-Warning and Intervention System for Sustainable Tourism Quality

> TobaPulse transforms fragmented visitor reviews into explainable early-warning signals and prioritized interventions for tourism destinations around Lake Toba.

## 1. Executive Summary

Tourism managers currently have thousands of visitor ratings and reviews, but no scalable way to convert them into operational decisions. A destination may have a high overall rating while repeatedly receiving complaints about dirty toilets, waste, damaged access roads, unclear prices, or poor maintenance. Average ratings hide these specific problems.

TobaPulse trains an Indonesian aspect-based review classification model using the organizer's tourism dataset. The model detects concrete destination issues, measures their severity and frequency, combines them with destination metadata and facilities, then displays prioritized interventions on an interactive web map.

TobaPulse adopts a narrow environmental component from the TobaClean concept: cleanliness, waste, sanitation, crowding, and visible environmental degradation become first-class early-warning categories. It does not attempt to become a complete environmental monitoring platform. Review-derived signals are treated as reports requiring field verification, not scientific environmental measurements.

The primary users are destination managers, BPODT/local government, and tourism program planners. The principal output is not sentiment. It is an evidence-backed answer to:

> Which destination problem should be verified and addressed first, why, and what intervention is appropriate?

## 2. Problem Statement

The supplied data contains thousands of tourism reviews, ratings, destination facilities, coordinates, operating hours, prices, and supporting information. However:

- Reviews remain unstructured text and cannot be monitored manually at scale.
- Overall ratings do not explain what is working or failing.
- Positive scenery reviews can hide sanitation, waste, access, or safety complaints.
- Destination managers lack a consistent method to prioritize limited intervention budgets.
- Environmental complaints are usually discovered reactively rather than identified as early signals.
- Incomplete and inconsistent data makes decisions difficult to audit.

This creates a decision gap: the ecosystem has visitor feedback, but it does not yet have actionable intelligence.

## 3. Proposed Solution

TobaPulse consists of three tightly scoped capabilities.

### 3.1 Aspect and Issue Detection

The trained model converts each review into one or more aspects with polarity and severity.

Example:

```text
Review:
"Pemandangannya indah, tetapi toiletnya kotor dan banyak sampah
di dekat tempat parkir. Jalan masuk juga rusak."

Predictions:
- scenery: positive
- sanitation: negative, high confidence
- waste: negative, high confidence
- access: negative, medium confidence
```

### 3.2 Early-Warning Signals

TobaPulse aggregates review predictions by destination and identifies repeated or severe signals involving:

- Cleanliness
- Waste
- Toilets and sanitation
- Crowding
- Visible environmental degradation
- Access and road condition
- Safety
- Parking and facilities
- Price transparency
- Service and maintenance

The first five categories are the focused contribution from TobaClean. TobaPulse does not claim to measure water quality, biodiversity, emissions, or ecological damage without suitable scientific data.

### 3.3 Intervention Prioritization

The system ranks destination issues using review evidence, severity, persistence, visitor exposure, facility gaps, confidence, and estimated intervention feasibility.

Example output:

```text
Priority: High
Destination: Example Destination A
Issue: Toilet and sanitation
Evidence: 18 of 64 recent textual reviews mention dirty or unavailable toilets
Supporting data: Toilet facility is not recorded in destination metadata
Recommended verification: On-site sanitation inspection
Candidate intervention: Cleaning schedule, maintenance checklist, complaint QR
Confidence: 86%
```

## 4. Product Scope

### Included

- Indonesian tourism review classification
- Aspect-specific sentiment and issue severity
- Destination Tourism Health Score
- Environmental early-warning signals from visitor reports
- Interactive geospatial issue map
- Destination evidence pages
- Intervention priority ranking
- Scenario-based intervention simulator
- Data confidence and provenance indicators

### Explicitly Excluded

- General-purpose chatbot
- Tourist itinerary generation
- Booking or payment
- Full UMKM marketplace
- Real-time crowd tracking
- Scientific water, air, or biodiversity monitoring
- Guaranteed causal impact prediction
- Unsupported claims that a place is safe, clean, or environmentally damaged

This scope keeps the product technically deep, coherent, and feasible during the hackathon.

## 5. Target Users

### Primary User: Destination Manager

Needs to identify recurring operational and environmental complaints, inspect supporting evidence, and decide which issue to verify first.

### Secondary User: Government or BPODT Planner

Needs a regional view of problem clusters, facility gaps, and intervention priorities to allocate limited resources.

### Beneficiaries

- Visitors receive cleaner, safer, and better-maintained experiences.
- Local communities benefit from more sustainable destination management.
- Tourism operators receive structured feedback instead of undifferentiated ratings.

## 6. Dataset Utilization

TobaPulse uses the organizer's data as the core source.

| Dataset Group | Use in TobaPulse |
| --- | --- |
| `wisata-v2.csv` | Attraction review training and issue detection |
| `resto-hotel-v2.csv` | Supporting service-quality model development and comparative analysis |
| `wisata-metadata.csv` | Destination identity, coordinates, type, fee, rating, status, hours |
| `tempat-wisata-v1.csv` | Additional facilities, representative reviews, status validation |
| `waktu operasional destinasi.csv` | Facility and operating-hour enrichment |
| `hotel-metadata.csv` | Nearby accommodation/service context |
| `resto-metadata.csv` | Nearby food/service context |
| `transportasi.csv` | Access and transport context |
| Articles and attraction information | Cultural and destination context, not model ground truth |

Relevant scale identified in the supplied files:

- 12,691 attraction reviews
- 9,611 hotel and restaurant reviews
- 22,302 reviews in total
- 139 attraction metadata records
- 323 coordinate-bearing attraction, hotel, and restaurant records
- Approximately 50% of attraction reviews have no review text and must not be used as text-training examples

## 7. Data Engineering Pipeline

### 7.1 Cleaning

- Decode all files using UTF-8 with BOM support.
- Remove embedded spreadsheet header rows.
- Normalize blank and unnamed columns.
- Convert decimal-comma ratings such as `4,5` to numeric values.
- Remove exact duplicate rows while preserving legitimate repeated generic comments.
- Separate rating-only records from textual reviews.
- Normalize Indonesian and English relative dates where scrape dates are available.
- Preserve raw values alongside normalized values for auditability.

### 7.2 Entity Resolution

No universal cross-file ID exists. TobaPulse creates a canonical `destination_id` using:

- Normalized place name
- Name similarity
- Address similarity
- Coordinate proximity
- Place category

Every match stores:

- Source record
- Match confidence
- Applied matching rules
- Alternative aliases

Manual evaluation should measure false merges because incorrectly combining two destinations is more harmful than leaving an uncertain match unresolved.

### 7.3 Feature Engineering

Destination-level features include:

- Aspect complaint rate
- Aspect praise rate
- Severe complaint rate
- Review volume
- Bayesian-adjusted rating
- Facility presence or absence
- Destination type
- Status and operating-hour confidence
- Nearby supporting-service density
- Data freshness
- Data completeness

## 8. Model Training

### 8.1 Prediction Task

Use a two-level supervised task:

1. Multilabel aspect detection: identify all aspects present in a review.
2. Aspect-level polarity and severity: classify each identified aspect.

Proposed aspects:

| Group | Labels |
| --- | --- |
| Environmental | cleanliness, waste, sanitation, crowding, environmental_condition |
| Infrastructure | access, road_condition, parking, public_facilities |
| Visitor experience | scenery, comfort, safety, price_transparency |
| Operations | staff_service, maintenance, opening_hours |

Polarity:

```text
positive | negative | neutral
```

Severity for negative issues:

```text
low | medium | high
```

### 8.2 Annotation Strategy

Target 1,500-2,500 manually verified review examples.

1. Create a detailed annotation guideline with positive and negative examples.
2. Select reviews using stratified sampling by destination, rating, length, and keywords.
3. Use rules or an LLM only to propose initial labels.
4. Require human verification before labels enter the gold dataset.
5. Double-annotate at least 15-20% of examples.
6. Resolve disagreements and update the guideline.

Measure inter-annotator agreement using Cohen's kappa or Krippendorff's alpha. This demonstrates that the labels are sufficiently clear for supervised learning.

### 8.3 Models

Baseline sequence:

1. Keyword/rule baseline
2. TF-IDF plus one-vs-rest logistic regression
3. IndoBERT multilabel classifier
4. IndoBERT with class weighting and calibrated thresholds

Recommended primary model:

```text
IndoBERT encoder
    -> multilabel aspect head
    -> aspect-specific polarity head
    -> severity head for negative aspects
```

Class-weighted binary cross-entropy or focal loss can reduce majority-label dominance. Thresholds should be calibrated separately for each aspect.

### 8.4 Leakage Prevention

Split train, validation, and test sets by destination rather than randomly by review. Reviews from one destination often contain repeated place-specific vocabulary. A random review split could produce an unrealistically high score.

Suggested split:

```text
70% destinations: training
15% destinations: validation
15% destinations: testing
```

## 9. Model Evaluation

### Aspect Detection

- Micro F1
- Macro F1
- Per-label precision and recall
- Precision at the high-severity alert threshold
- Exact-match ratio

### Polarity and Severity

- Macro F1
- Confusion matrix
- High-severity precision
- Calibration error

### Entity Resolution

- Pairwise precision
- Pairwise recall
- F1
- False-merge rate

### System-Level Evaluation

Create expert-reviewed destination cases and evaluate:

- Evidence correctness
- Unsupported alert rate
- Intervention relevance
- Priority-ranking agreement
- Time saved compared with manual review inspection

Target goals for the preliminary prototype:

```text
Aspect Micro F1 >= 0.82
Aspect Macro F1 >= 0.70
High-severity alert precision >= 0.85
Entity resolution F1 >= 0.90
Unsupported evidence claims < 5%
```

Targets are goals, not results. The submission must report actual measurements honestly.

## 10. Tourism Health and Priority Scores

### 10.1 Aspect Health Score

For each aspect and destination:

```text
AspectHealth = 100 * (1 - WeightedComplaintRate)
```

`WeightedComplaintRate` accounts for model confidence, severity, and review evidence. Bayesian smoothing prevents destinations with very few reviews from receiving extreme scores.

### 10.2 Tourism Health Score

```text
TourismHealth =
  0.25 environmental_health
+ 0.20 sanitation_health
+ 0.15 infrastructure_health
+ 0.15 safety_health
+ 0.15 operational_health
+ 0.10 visitor_experience_health
```

Weights should be configurable and validated with domain experts. The app must always show component scores rather than presenting one opaque number.

### 10.3 Intervention Priority

```text
Priority =
  IssueSeverity
* ComplaintFrequency
* EvidenceConfidence
* VisitorExposure
* Persistence
* FacilityGap
* FeasibilityWeight
```

This is a transparent decision-support score, not a causal prediction.

Priority labels:

```text
Critical | High | Medium | Monitor | Insufficient Data
```

## 11. Web Application

### 11.1 Regional Overview

Displays:

- Regional Tourism Health Score
- Number of high-priority alerts
- Dominant issue categories
- Destination and review coverage
- Data-confidence distribution
- Top recommended verification targets

### 11.2 Intelligence Map

Map layers:

- Overall Tourism Health
- Cleanliness and waste
- Sanitation
- Crowding
- Access and infrastructure
- Safety
- Data confidence

Filters:

- Kabupaten
- Destination type
- Issue severity
- Review volume
- Confidence
- Operating status

### 11.3 Destination Detail

Each destination page shows:

- Component health scores
- Issue timeline where dates are usable
- Positive and negative aspects
- Number of supporting reviews
- Anonymized evidence snippets
- Facilities and metadata
- Data conflicts and missing fields
- Recommended field verification
- Candidate interventions

### 11.4 Intervention Queue

A sortable operational table:

| Priority | Destination | Issue | Evidence | Confidence | Suggested Next Step |
| --- | --- | --- | --- | --- | --- |
| High | Destination A | Sanitation | 18 review signals | 86% | Verify toilets on site |
| High | Destination B | Waste | 12 review signals | 82% | Inspect waste points |
| Medium | Destination C | Access | 9 review signals | 74% | Validate road condition |

Managers can mark an item as:

```text
New | Verification Planned | Verified | Intervention Planned | Resolved | Rejected
```

For the hackathon prototype, state changes may be stored locally or in a simple database.

### 11.5 Intervention Simulator

Users select a candidate intervention, such as:

- Add or repair toilets
- Increase cleaning frequency
- Add waste collection points
- Improve parking organization
- Add signage
- Improve access-road maintenance

The app recalculates the score under explicit assumptions. Output must be labeled:

> Scenario estimate, not a guaranteed real-world outcome.

## 12. Explainability and Responsible AI

Every alert must answer:

- What issue was detected?
- How many reviews support it?
- Which anonymized excerpts are evidence?
- What metadata supports or conflicts with it?
- How confident is the model?
- What should a human verify?

Safeguards:

- Never expose reviewer names or personal identifiers.
- Do not label a destination as dangerous or polluted based solely on reviews.
- Use `reported issue` or `early-warning signal` language.
- Hide alerts below minimum evidence and confidence thresholds.
- Distinguish no issue from insufficient data.
- Allow managers to reject incorrect alerts and record reasons.
- Document popularity bias: frequently reviewed places generate more signals.
- Apply Bayesian smoothing and minimum-support thresholds.
- Retain review provenance for audit, subject to privacy constraints.

## 13. Technical Architecture

```text
CSV datasets
    |
    v
Cleaning and entity-resolution pipeline
    |
    +--> Canonical tourism database
    |
    +--> Human annotation workspace
              |
              v
        IndoBERT training pipeline
              |
              v
        Versioned classifier
              |
              v
Batch review inference and aggregation
              |
              v
Tourism Health and Priority Engine
              |
              v
REST API -> Web application -> Interactive map
```

Practical stack:

| Layer | Suggested Technology |
| --- | --- |
| Data processing | Python, Pandas or Polars |
| Model training | PyTorch, Hugging Face Transformers |
| Baselines | scikit-learn |
| API | FastAPI |
| Database | PostgreSQL/PostGIS or SQLite for prototype |
| Web | Next.js or React |
| Map | MapLibre GL or Leaflet |
| Charts | ECharts, Recharts, or Plotly |
| Deployment | Docker; DGX B200-compatible inference service |

The final prototype should work without external model APIs so it can run reliably during the onsite lockdown and DGX B200 deployment.

## 14. Minimum Viable Product

The preliminary MVP should demonstrate:

1. Cleaned and linked attraction data.
2. A labeled review subset and documented annotation guideline.
3. Three evaluated models: keyword, TF-IDF, and IndoBERT.
4. Aspect and issue predictions for attraction reviews.
5. Destination-level health and priority scores.
6. Interactive map with at least five issue layers.
7. Destination evidence page.
8. Intervention queue.
9. Quantitative model and system evaluation.

Do not spend preliminary-round time implementing accounts, complex permissions, notifications, or a full workflow system.

## 15. Development Plan

### Phase 1: Data and Validation

- Profile and clean all relevant files.
- Build canonical destination entities.
- Quantify review and facility coverage.
- Interview or validate assumptions with at least one tourism stakeholder if possible.

### Phase 2: Annotation and Baselines

- Define taxonomy and annotation guide.
- Label a balanced dataset.
- Measure annotator agreement.
- Train keyword and TF-IDF baselines.

### Phase 3: Primary Model

- Fine-tune IndoBERT.
- Calibrate thresholds.
- Perform destination-separated testing.
- Analyze errors and biases.

### Phase 4: Intelligence Engine

- Aggregate predictions by destination.
- Implement health and priority formulas.
- Add evidence and confidence rules.

### Phase 5: Web Product

- Build overview, map, destination detail, and intervention queue.
- Connect real inference results.
- Add scenario simulator only after core pages work.

### Phase 6: Submission

- Run reproducible evaluation.
- Record a failure-to-intervention demo story.
- Document limitations and responsible-AI measures.
- Prepare deployment package and offline fallback.

## 16. Impact Measurement

### Prototype Metrics

- Model Macro/Micro F1
- High-severity alert precision
- Evidence correctness
- Number of destinations analyzed
- Percentage of alerts with sufficient evidence
- Manual review-analysis time saved

### Pilot Metrics

- Alert verification rate
- Median time from alert to field verification
- Percentage of verified issues receiving intervention
- Complaint-rate change after intervention
- Visitor health-score change after intervention
- Destination-manager adoption and repeat usage

Avoid promising direct visitor or revenue growth during the prototype stage. Measure operational response first.

## 17. Pilot Plan

Run a limited pilot with 5-10 destinations representing different destination types and review volumes.

1. Generate TobaPulse alerts from historical reviews.
2. Ask managers to assess relevance without seeing the model ranking first.
3. Compare expert assessment with model output.
4. Conduct field verification for high-priority signals.
5. Record confirmed, rejected, and uncertain alerts.
6. Refine labels, thresholds, and priority weights.
7. Track selected interventions and subsequent review signals.

## 18. Demo Scenario

### Opening

Show a destination with a strong overall rating. Ask:

> If this rating is high, does that mean destination operations are healthy?

### Reveal

Open the destination in TobaPulse. The model reveals repeated sanitation and waste complaints hidden among positive scenery reviews.

### Evidence

Display:

- Aspect distribution
- Complaint frequency
- Severity
- Anonymized supporting excerpts
- Missing or conflicting facility metadata
- Model confidence

### Action

Open the intervention queue and show why this issue ranks above another destination's lower-confidence complaint.

### Simulation

Select a sanitation intervention. Show the scenario score, assumptions, verification requirement, and expected operational indicator.

### Regional View

Return to the map and reveal clusters of cleanliness, waste, sanitation, and access signals across Lake Toba.

Closing line:

> TobaPulse does not replace field inspection. It tells limited inspection teams where evidence says they should look first.

## 19. Pitch Positioning

### One-Sentence Pitch

> TobaPulse trains AI to transform 22,302 fragmented tourism reviews into explainable early-warning signals and prioritized interventions for cleaner, safer, and better-managed Toba destinations.

### Core Narrative

```text
Reviews are treated as opinions.
Operational problems remain hidden inside positive ratings.
Manual monitoring cannot scale.
TobaPulse detects specific issues, maps evidence, and prioritizes verification.
Managers act earlier with transparent, measurable intelligence.
```

### Differentiation

TobaPulse is not:

- A generic sentiment dashboard
- A review summarizer
- A tourism chatbot
- An environmental sensor replacement

TobaPulse is:

- A trained issue-detection model
- An explainable early-warning system
- A destination intervention queue
- A decision-support product grounded in Toba data

## 20. Rubric Alignment

| Criterion | TobaPulse Evidence |
| --- | --- |
| Novelty and problem framing | Converts reviews into intervention priorities, not generic recommendations |
| Toba ecosystem impact | Supports destination quality, sustainability, managers, visitors, and communities |
| Technical AI and data quality | Annotation, IndoBERT training, entity resolution, calibrated alerts, geospatial aggregation |
| Feasibility and sustainability | Batch inference, explainable workflow, limited pilot, deployable web app |
| Toba dataset utilization | Meaningful use of reviews, metadata, coordinates, facilities, hours, and supporting services |
| Communication and demo | Strong visual journey from hidden complaint to prioritized action |

## 21. Main Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| Sparse environmental complaints | Use balanced sampling; report per-label support; do not force unsupported categories |
| Popularity bias | Bayesian smoothing, minimum support, confidence display, low-coverage category |
| Review manipulation | Duplicate detection, repeated-text checks, robust aggregation |
| Incorrect model alerts | High-precision threshold, evidence display, human verification workflow |
| Old information | Show scrape date and freshness; label historical signals |
| Entity matching errors | Conservative matching, match confidence, manual evaluation |
| Harm to destination reputation | Neutral language, anonymized evidence, restricted management view where appropriate |
| Correlation presented as causation | Label simulator as scenario analysis; avoid guaranteed impact claims |

## 22. Final Scope Decision

TobaPulse remains focused on tourism quality intervention. It takes only the strongest, data-supported component from TobaClean: environmental and sanitation complaints become early-warning categories inside the same review intelligence model.

The winning prototype should prove one complete chain:

```text
Raw review
-> trained model prediction
-> destination-level signal
-> explainable priority
-> human-verifiable intervention
```

If this chain is accurate, measurable, visually compelling, and responsibly communicated, TobaPulse can demonstrate substantially more value than a broad feature-heavy tourism application.
