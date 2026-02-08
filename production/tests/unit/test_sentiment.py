"""Unit tests for sentiment scoring and priority routing (Phase 14: T105-T106)."""
import pytest

from production.workers.message_processor import score_sentiment, route_priority_by_sentiment


class TestScoreSentiment:
    """Test keyword-based sentiment scoring."""

    def test_neutral_message(self):
        score = score_sentiment("How do I reset my password?")
        assert 0.3 <= score <= 0.7

    def test_positive_message(self):
        score = score_sentiment("Thanks for the great help! Everything works perfectly now.")
        assert score > 0.5

    def test_negative_message(self):
        score = score_sentiment("This is terrible and broken. The worst product ever.")
        assert score < 0.3

    def test_all_caps_angry(self):
        score = score_sentiment("WHY IS EVERYTHING BROKEN THIS IS RIDICULOUS")
        assert score < 0.3

    def test_excessive_exclamation(self):
        score = score_sentiment("This is broken!!! Fix it now!!!")
        assert score < 0.5

    def test_empty_message(self):
        score = score_sentiment("")
        assert score == 0.5

    def test_score_bounds(self):
        # Very negative
        score = score_sentiment("terrible awful horrible worst broken unusable ridiculous")
        assert 0.0 <= score <= 1.0

        # Very positive
        score = score_sentiment("great thanks wonderful excellent helpful love fantastic")
        assert 0.0 <= score <= 1.0

    def test_mixed_sentiment(self):
        score = score_sentiment("The app is great but the sync feature is broken")
        assert 0.2 <= score <= 0.8


class TestRoutePriorityBySentiment:
    """Test sentiment-based priority adjustment (T106)."""

    def test_very_negative_forces_high(self):
        assert route_priority_by_sentiment(0.1, "low") == "high"
        assert route_priority_by_sentiment(0.1, "medium") == "high"
        assert route_priority_by_sentiment(0.2, "low") == "high"

    def test_moderately_negative_bumps_low(self):
        assert route_priority_by_sentiment(0.4, "low") == "high"

    def test_moderately_negative_keeps_medium(self):
        assert route_priority_by_sentiment(0.4, "medium") == "medium"

    def test_positive_keeps_priority(self):
        assert route_priority_by_sentiment(0.7, "low") == "low"
        assert route_priority_by_sentiment(0.7, "medium") == "medium"
        assert route_priority_by_sentiment(0.7, "high") == "high"

    def test_neutral_keeps_priority(self):
        assert route_priority_by_sentiment(0.5, "low") == "low"
        assert route_priority_by_sentiment(0.5, "medium") == "medium"
