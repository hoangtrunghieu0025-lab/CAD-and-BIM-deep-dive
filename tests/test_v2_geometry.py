"""TASK-018 M2: segments.py và walls.py trên ca tổng hợp có đáp án."""
import math

import pytest
from shapely.geometry import Polygon

from src.cad2bim import segments as sg
from src.cad2bim import walls as wl


def rect_segs(x0, y0, x1, y1):
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    return list(zip(pts, pts[1:]))


def double_line_room(w=4.0, h=3.0, t=0.2):
    h2 = t / 2
    return rect_segs(-h2, -h2, w + h2, h + h2) + rect_segs(h2, h2, w - h2, h - h2)


def test_snap_endpoints_merges_close_points():
    segs = [((0, 0), (1, 0)), ((1.004, 0.002), (1, 1))]
    out = sg.snap_endpoints(segs, 0.01)
    assert out[0][1] == out[1][0]


def test_snap_drops_degenerate_segments():
    assert sg.snap_endpoints([((0, 0), (0.001, 0))], 0.01) == []


def test_node_and_chain_splits_t_and_preserves_length():
    segs = [((0, 0), (6, 0)), ((3, 0), (3, 4))]
    chains = sg.node_and_chain(segs)
    assert len(chains) == 3
    assert sum(c.length for c in chains) == pytest.approx(10.0)


def test_node_and_chain_joins_l_corner_into_one_chain():
    chains = sg.node_and_chain([((0, 0), (5, 0)), ((5, 0), (5, 3))])
    assert len(chains) == 1 and chains[0].length == pytest.approx(8.0)


@pytest.mark.parametrize("gap, tol, extended", [(0.15, 0.30, 1), (0.30, 0.30, 1), (0.40, 0.30, 0)])
def test_extend_free_ends_closes_gap_within_tolerance(gap, tol, extended):
    segs = [((0, 0), (6, 0)), ((3, gap), (3, 4))]
    out, n = sg.extend_free_ends(segs, tol)
    assert n == extended
    assert (out[1][0][1] == pytest.approx(0.0)) == bool(extended)


def test_extend_free_ends_does_not_move_touching_ends():
    segs = [((0, 0), (6, 0)), ((3, 0), (3, 4))]
    out, n = sg.extend_free_ends(segs, 0.5)
    assert n == 0                      # các đầu tự do không có vật cản trong tầm với nên không đổi
    assert out == segs


def test_free_end_count():
    assert sg.free_end_count([((0, 0), (6, 0)), ((3, 0), (3, 4))]) == 3   # (0,0), (6,0), (3,4)


def test_pair_walls_double_line_room():
    pieces, left = wl.pair_walls(double_line_room())
    assert len(pieces) == 4 and left == []
    assert all(p.source == "pair" and p.thickness == pytest.approx(0.2) for p in pieces)
    assert sum(p.axis.length for p in pieces) == pytest.approx(2 * 3.8 + 2 * 2.8)   # axes chưa kéo tới góc


def test_footprint_of_double_line_room_is_the_exact_ring():
    pieces, _ = wl.pair_walls(double_line_room())
    fp = wl.footprint(pieces)
    expected = Polygon([(-.1, -.1), (4.1, -.1), (4.1, 3.1), (-.1, 3.1)], [[(.1, .1), (.1, 2.9), (3.9, 2.9), (3.9, .1)]])
    assert fp.area == pytest.approx(expected.area, abs=1e-6)
    assert fp.symmetric_difference(expected).area < 1e-6
    assert fp.is_valid and fp.geom_type == "Polygon"


def test_pair_walls_two_thicknesses():
    segs = [((0, 0), (5, 0)), ((0, 0.1), (5, 0.1)), ((0, 4), (5, 4)), ((0, 4.3), (5, 4.3))]
    pieces, left = wl.pair_walls(segs)
    assert sorted(round(p.thickness, 3) for p in pieces) == [0.1, 0.3]
    assert left == []


def test_corridor_wider_than_max_is_not_a_wall():
    pieces, left = wl.pair_walls([((0, 0), (6, 0)), ((0, 1.5), (6, 1.5))])
    assert pieces == [] and len(left) == 2


def test_opening_candidate_from_door_gap():
    # tường nét đôi dài 6 m, có khe cửa 1,0 m ở giữa (x từ 2,5 đến 3,5)
    segs = [((0, 0.1), (2.5, 0.1)), ((3.5, 0.1), (6, 0.1)), ((0, -0.1), (2.5, -0.1)), ((3.5, -0.1), (6, -0.1))]
    pieces, _ = wl.pair_walls(segs)
    assert len(pieces) == 2
    cands = wl.opening_candidates(pieces)
    assert len(cands) == 1 and cands[0]["width"] == pytest.approx(1.0)
    assert cands[0]["center"] == pytest.approx((3.0, 0.0))


def test_near_vertical_segments_with_opposite_orientation_group_together():
    # hai nét dọc, một nét vẽ từ trên xuống, một nét từ dưới lên, lệch góc rất nhỏ quanh ±90°
    segs = [((0, 0), (0.0001, 5)), ((0.2, 5), (0.2, 0))]
    pieces, left = wl.pair_walls(segs)
    assert len(pieces) == 1 and pieces[0].thickness == pytest.approx(0.2, abs=1e-3)


def test_partial_overlap_leaves_remainder():
    pieces, left = wl.pair_walls([((0, 0), (6, 0)), ((0, 0.2), (4, 0.2))])
    assert len(pieces) == 1 and pieces[0].axis.length == pytest.approx(4.0)
    assert sum(math.dist(a, b) for a, b in left) == pytest.approx(2.0)


def test_single_walls_mitre_l_corner_area():
    ws = wl.single_walls([((0, 0), (5, 0)), ((5, 0), (5, 3))], 0.2)
    fp = wl.footprint(ws)
    assert fp.area == pytest.approx(0.2 * 8, abs=1e-6)


def test_node_and_chain_single_segment_regression():
    """Ca tái hiện: đầu vào chỉ một đoạn -> unary_union trả LineString, linemerge từng ném ValueError (bản vẽ thật)."""
    chains = sg.node_and_chain([((0, 0), (2, 0))])
    assert len(chains) == 1 and chains[0].length == pytest.approx(2.0)


def test_node_and_chain_duplicate_segments_collapse():
    chains = sg.node_and_chain([((0, 0), (2, 0)), ((2, 0), (0, 0)), ((0, 0), (2, 0))])
    assert len(chains) == 1 and chains[0].length == pytest.approx(2.0)
