from alphalens.benchmark import evaluate_timing_benchmark

def test_benchmark_counts():
    r=evaluate_timing_benchmark(range(3))
    assert r["cases"] == 6
    assert sum(r[k] for k in ("true_positive","true_negative","false_positive","false_negative"))==6

def test_benchmark_reproducible():
    assert evaluate_timing_benchmark(range(4)) == evaluate_timing_benchmark(range(4))

def test_benchmark_no_real_world_claim():
    r=evaluate_timing_benchmark(range(2))
    assert "synthetic" in r["limitation"].lower()
