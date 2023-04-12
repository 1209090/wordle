import unittest
from collections import defaultdict

class Player:
    def __init__(self, name, rating):
        self.name = name
        self.rating = rating

    def __repr__(self):
        return f"{self.name} ({self.rating})"

class EloMatch:
    def __init__(self, players):
        self.players = {player.name: player for player in players}

    def updated_ratings(self, scores):
        """Calculate the new Elo ratings."""
        res = defaultdict(int)
        for player in self.players.values():
            for opponent in self.players.values():
                if player != opponent and player.name in scores and opponent.name in scores:
                    expected_score = self.expected_score(player.rating, opponent.rating)
                    actual_score = self.actual_score(scores[player.name], scores[opponent.name])
                    res[player.name] += self.rating_adjustment(expected_score, actual_score)

        return {k: p.rating + int(round(res[k])) for k, p in self.players.items()}

    def update(self, scores):
        """Update the player ratings."""
        for name, rating in self.updated_ratings(scores).items():
            self.players[name].rating = rating

    def actual_score(self, player, opponent):
        """Calculate the actual score of a player given their opponent's score.
        Returns 0, 0.5, or 1, representing a loss, draw, or win (respectively).
        """
        if player > opponent:
            return 1
        elif player < opponent:
            return 0
        else:
            return 0.5

    @staticmethod
    def expected_score(player_rating, opponent_rating):
        """Calculate the expected score of a player given their rating and their opponent's rating.
        Returns a float between 0 and 1 where 0.999 represents high certainty of the first player winning.
        """
        return 1.0 / (1 + (10 ** ((opponent_rating - player_rating) / 400.0)))

    @staticmethod
    def rating_adjustment(expected_score, actual_score):
        """Calculate the amount a player's rating should change.
        Arguments:
            expected_score: a float between 0 and 1, representing the probability of the player winning
            actual_score: 0, 0.5, or 1, whether the outcome was a loss, draw, or win (respectively)
            rating: the rating of the player, used by the K-factor function
            k_factor: the K-factor to use for this calculation to be used instead of the normal K-factor or K-factor function
        Returns a positive or negative float representing the amount the player's rating should change.
        """
        return 24 * (actual_score - expected_score)

class TestEloMatch(unittest.TestCase):
    def test_rating_adjustment(self):
        self.assertEqual(EloMatch.rating_adjustment(0.5, 0.5), 0)
        self.assertEqual(EloMatch.rating_adjustment(0.5, 0), -12)
        self.assertEqual(EloMatch.rating_adjustment(0.5, 1), 12)

    def test_updated_ratings(self):
        players = [Player("Alice", 1000), Player("Bob", 950), Player("Charlie", 1050), Player("Dave", 1100)]
        scores = {"Alice": 3, "Bob": 2, "Charlie": 2, "Dave": 1}
        match = EloMatch(players)
        self.assertEqual(match.updated_ratings(scores), {"Alice": 1039, "Bob": 960, "Charlie": 1047, "Dave": 1054})

        players = [Player("Alice", 1000), Player("Bob", 950), Player("Charlie", 1050), Player("Dave", 1100)]
        scores = {"Alice": 2, "Bob": 2, "Charlie": 2, "Dave": 2}
        match = EloMatch(players)
        self.assertEqual(match.updated_ratings(scores), {"Alice": 1003, "Bob": 960, "Charlie": 1047, "Dave": 1090})

        players = [Player("Alice", 1000), Player("Bob", 1000), Player("Charlie", 1000), Player("Dave", 1000)]
        scores = {"Alice": 1, "Bob": 2, "Charlie": 3, "Dave": 4}
        match = EloMatch(players)
        self.assertEqual(match.updated_ratings(scores), {"Alice": 964, "Bob": 988, "Charlie": 1012, "Dave": 1036})

        players = [Player("Alice", 1000), Player("Bob", 1000), Player("Charlie", 1000), Player("Dave", 1000)]
        scores = {"Alice": 1, "Bob": 2, "Charlie": 3}
        match = EloMatch(players)
        self.assertEqual(match.updated_ratings(scores), {"Alice": 976, "Bob": 1000, "Charlie": 1024, "Dave": 1000})

    def test_update(self):
        players = [Player("Alice", 1000), Player("Bob", 950), Player("Charlie", 1050), Player("Dave", 1100)]
        scores = {"Alice": 3, "Bob": 2, "Charlie": 2, "Dave": 1}
        match = EloMatch(players)
        match.update(scores)
        [self.assertEqual(p.rating, r) for p, r in zip(players, [1039, 960, 1047, 1054])]

        scores = {"Alice": 2, "Bob": 2, "Charlie": 2, "Dave": 2}
        match.update(scores)
        [self.assertEqual(p.rating, r) for p, r in zip(players, [1037, 969, 1044, 1050])]
