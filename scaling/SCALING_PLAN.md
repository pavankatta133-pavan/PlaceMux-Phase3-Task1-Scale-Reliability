# Phase 3 Task 4 — Horizontal Scale & Load Readiness

## Objective

The objective is to validate the horizontal scalability of the PlaceMux
AI inference service and identify the safe operating capacity under
increasing concurrent request load.

## Load Testing

The inference endpoint was tested at progressively increasing QPS levels.

The test measured:

- Actual QPS
- Request count
- Success rate
- Average latency
- P95 latency
- Maximum latency
- Failed requests

The load-test results are stored in:

`load_testing/reports/load_test_report.json`

## Capacity Analysis

The tested capacity was evaluated against:

- P95 latency SLO
- Minimum success-rate requirement

The analysis identifies:

- Highest passing QPS
- First breaking QPS
- Recommended operating capacity
- Required headroom

Results:

`load_testing/reports/capacity_analysis.json`

## Scaling Strategy

The recommended production strategy is horizontal scaling.

Additional inference instances should be added when traffic approaches
the measured safe capacity of a single instance.

### Scale-Out Signals

The main scale-out signals are:

1. Requests per second per instance
2. P95 inference latency
3. Error rate
4. Sustained CPU utilization

### Scale-In

Instances can be removed during sustained low traffic while maintaining
a minimum production replica count.

## Batching

Batching is not enabled for the primary online recommendation path
because the service is latency-sensitive.

Batch processing may be considered for offline recommendation generation
or non-interactive workloads.

## Precomputation

Precomputation is not required for the current online path.

It can be introduced later for frequently requested or cacheable
recommendations.

## Model-Unavailable Behaviour

When the model is unavailable, the service should fail safely rather than
return an invalid recommendation.

Expected behaviour:

- Return a degraded response
- Set recommendation availability to false
- Return a clear model-unavailable error
- Avoid cascading failures

## Headroom

A 30% operating headroom target is used.

The recommended operating capacity is therefore below the measured
maximum passing capacity.

## Conclusion

The load-test and capacity-analysis results provide evidence for the
safe operating range of the inference service.

Horizontal scaling is recommended as the primary production strategy,
with latency, request rate, error rate, and resource utilization used as
scaling signals.