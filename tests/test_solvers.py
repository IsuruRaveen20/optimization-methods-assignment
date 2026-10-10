import itertools
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tsp import data, exact, heuristics  # noqa: E402


def random_matrix(n, seed):
    rng = random.Random(seed)
    pts = [("p%d" % i, rng.uniform(6.7, 7.2), rng.uniform(79.8, 80.1)) for i in range(n)]
    return data.distance_matrix(pts)


def brute_force(d):
    n = len(d)
    return min(heuristics.tour_length([0, *p, 0], d) for p in itertools.permutations(range(1, n)))


class SolverTests(unittest.TestCase):
    def test_held_karp_matches_brute_force(self):
        for seed in range(5):
            d = random_matrix(8, seed)
            best, tour = exact.held_karp(d)
            self.assertAlmostEqual(best, brute_force(d), places=9)
            self.assertAlmostEqual(best, heuristics.tour_length(tour, d), places=9)

    def test_one_tree_bound_is_a_valid_lower_bound(self):
        for seed in range(5):
            d = random_matrix(9, seed)
            opt, _ = exact.held_karp(d)
            self.assertLessEqual(exact.one_tree_bound(d), opt + 1e-9)

    def test_tours_are_feasible_and_never_better_than_optimum(self):
        d = random_matrix(10, 42)
        opt, _ = exact.held_karp(d)
        tours = [heuristics.nearest_neighbour(d),
                 heuristics.two_opt(heuristics.nearest_neighbour(d), d),
                 heuristics.local_search(heuristics.nearest_neighbour(d), d),
                 heuristics.multi_start(d, 5, seed=1),
                 heuristics.iterated_local_search(d, 20, seed=1)]
        for t in tours:
            self.assertEqual(t[0], 0)
            self.assertEqual(t[-1], 0)
            self.assertEqual(sorted(t[:-1]), list(range(10)))
            self.assertGreaterEqual(heuristics.tour_length(t, d), opt - 1e-9)

    def test_local_search_never_worsens(self):
        d = random_matrix(30, 7)
        nn = heuristics.nearest_neighbour(d)
        self.assertLessEqual(heuristics.tour_length(heuristics.two_opt(nn, d), d), heuristics.tour_length(nn, d))
        self.assertLessEqual(heuristics.tour_length(heuristics.local_search(nn, d), d),
                             heuristics.tour_length(heuristics.two_opt(nn, d), d) + 1e-9)


class DatasetTests(unittest.TestCase):
    def test_dataset_passes_validation(self):
        self.assertEqual(data.validate(data.load_locations()), [])


if __name__ == "__main__":
    unittest.main()
