from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False, index=True)
    external_id = Column(String(255), nullable=True)
    title = Column(String(500), nullable=False)
    category = Column(String(100), nullable=True, index=True)
    price = Column(Float, nullable=True)
    original_price = Column(Float, nullable=True)
    discount = Column(Float, nullable=True)
    offer = Column(Text, nullable=True)
    availability = Column(Boolean, default=True)
    seller = Column(String(255), nullable=True)
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=True)
    image_url = Column(Text, nullable=True)
    product_url = Column(Text, nullable=True)
    relevance_score = Column(Float, nullable=True)
    specifications = Column(JSON, default=dict)
    delivery_time = Column(String(100), nullable=True)
    search_query = Column(String(500), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    wishlists = relationship("Wishlist", back_populates="product")


class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    query = Column(String(500), nullable=False)
    products = Column(JSON, default=list)
    price_comparison = Column(JSON, default=dict)
    review_analysis = Column(JSON, default=dict)
    recommendation = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
