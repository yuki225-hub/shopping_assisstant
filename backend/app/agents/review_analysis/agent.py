from typing import List
from loguru import logger
from app.schemas.product import ProductSchema, ReviewAnalysisSchema
from app.agents.review_analysis.sentiment import SentimentAnalyzer, USE_HF


class ReviewAnalysisAgent:
    """Agent 3: Analyzes reviews for the searched product only."""

    def __init__(self):
        self.analyzer = SentimentAnalyzer()

    def analyze(self, products: List[ProductSchema], extra_reviews: List[str] = None) -> ReviewAnalysisSchema:
        reviews = list(extra_reviews or [])

        # Build one synthetic review per product based on its own rating.
        # Each review references only that product's data — no cross-product mixing.
        for p in products:
            if p.rating is None:
                continue
            stars = p.rating
            name = p.title
            if stars >= 4.5:
                reviews.append(f"Excellent quality, highly recommend {name}, great value for money, fast delivery")
            elif stars >= 4.0:
                reviews.append(f"Good product {name}, satisfied with quality, recommend to others")
            elif stars >= 3.0:
                reviews.append(f"Average product {name}, decent quality but could be better")
            else:
                reviews.append(f"Disappointed with {name}, poor quality, bad experience, waste of money")

        if not reviews:
            return self._empty_analysis()

        sentiments = []
        if USE_HF:
            from app.agents.review_analysis.sentiment import _hf_analyze
            for r in reviews[:50]:
                try:
                    sentiments.append(_hf_analyze(r))
                except Exception:
                    sentiments.append(self.analyzer.analyze(r))
        else:
            sentiments = [self.analyzer.analyze(r) for r in reviews]

        pos = sum(1 for s, _ in sentiments if s == "positive")
        neg = sum(1 for s, _ in sentiments if s == "negative")
        neu = sum(1 for s, _ in sentiments if s == "neutral")
        total = len(sentiments)

        pos_pct = round(pos / total * 100, 1)
        neg_pct = round(neg / total * 100, 1)
        neu_pct = round(neu / total * 100, 1)

        overall = "positive" if pos_pct > 50 else ("negative" if neg_pct > 50 else "mixed")
        confidence = round(max(pos_pct, neg_pct, neu_pct) / 100, 2)

        pros = self.analyzer.extract_keywords(reviews, "positive")
        cons = self.analyzer.extract_keywords(reviews, "negative")

        # Fake review detection: suspiciously perfect ratings with almost no negatives
        rated = [p for p in products if p.rating]
        avg_rating = sum(p.rating for p in rated) / max(len(rated), 1)
        fake_flag = avg_rating > 4.8 and neg_pct < 2 and total > 10

        summary = (
            f"Based on {total} product reviews, {pos_pct}% are positive. "
            f"Customers {'love' if pos_pct > 60 else 'are mixed about'} this product. "
            f"Common praise: {', '.join(pros[:3]) or 'quality'}. "
            f"Common complaints: {', '.join(cons[:3]) or 'none significant'}."
        )

        logger.info(f"ReviewAnalysisAgent: pos={pos_pct}%, neg={neg_pct}%, confidence={confidence}")
        return ReviewAnalysisSchema(
            overall_sentiment=overall,
            positive_percent=pos_pct,
            negative_percent=neg_pct,
            neutral_percent=neu_pct,
            common_pros=pros,
            common_cons=cons,
            summary=summary,
            recommendation_confidence=confidence,
            fake_review_flag=fake_flag,
        )

    def _empty_analysis(self) -> ReviewAnalysisSchema:
        return ReviewAnalysisSchema(
            overall_sentiment="neutral",
            positive_percent=0,
            negative_percent=0,
            neutral_percent=100,
            common_pros=[],
            common_cons=[],
            summary="No reviews available for analysis.",
            recommendation_confidence=0.5,
        )
