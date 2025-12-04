# backend/rules_service/routers/rules.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db import get_db
from rules_service.models import TradingRule
from rules_service.schemas import RuleCreate, RuleUpdate, RuleRead


router = APIRouter(
    prefix="/rules",
    tags=["rules"],
)


@router.get("/", response_model=List[RuleRead])
def list_rules(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[TradingRule]:
    """Return all trading rules (paginated)."""
    return (
        db.query(TradingRule)
        .order_by(TradingRule.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post(
    "/",
    response_model=RuleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_rule(
    rule_in: RuleCreate,
    db: Session = Depends(get_db),
) -> TradingRule:
    """Create a new trading rule."""
    rule = TradingRule(
        title=rule_in.title,
        description=rule_in.description,
        category=rule_in.category,
        is_active=rule_in.is_active,
    )

    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.get("/{rule_id}", response_model=RuleRead)
def get_rule(
    rule_id: int,
    db: Session = Depends(get_db),
) -> TradingRule:
    """Return a single trading rule by ID."""
    rule = db.query(TradingRule).filter(TradingRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with id={rule_id} not found",
        )
    return rule


@router.put("/{rule_id}", response_model=RuleRead)
def update_rule(
    rule_id: int,
    rule_in: RuleUpdate,
    db: Session = Depends(get_db),
) -> TradingRule:
    """Update an existing rule (full update with optional fields)."""
    rule = db.query(TradingRule).filter(TradingRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with id={rule_id} not found",
        )

    update_data = rule_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)

    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.delete(
    "/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a rule completely."""
    rule = db.query(TradingRule).filter(TradingRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with id={rule_id} not found",
        )
    db.delete(rule)
    db.commit()
    return None


@router.patch("/{rule_id}/toggle", response_model=RuleRead)
def toggle_rule_active(
    rule_id: int,
    db: Session = Depends(get_db),
) -> TradingRule:
    """Toggle a rule's active state."""
    rule = db.query(TradingRule).filter(TradingRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with id={rule_id} not found",
        )

    rule.is_active = not rule.is_active
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule
