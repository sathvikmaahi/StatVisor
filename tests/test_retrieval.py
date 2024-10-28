from backend.app.retrieval import fuse_scores


def test_fuse_scores_prefers_agreement():
    dense = [0.9, 0.1, 0.2]
    sparse = [0.8, 0.0, 0.1]
    fused = fuse_scores(dense, sparse, 0.65, 0.35)
    assert fused[0] == max(fused)


def test_fuse_scores_handles_flat_dense():
    dense = [1.0, 1.0, 1.0]
    sparse = [0.0, 5.0, 1.0]
    fused = fuse_scores(dense, sparse, 0.5, 0.5)
    assert fused[1] == max(fused)
