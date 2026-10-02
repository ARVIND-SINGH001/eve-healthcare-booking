from decimal import Decimal

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.dependencies import CurrentUser, DbSession
from app.models.centre_test import CentreTest
from app.models.diagnostic_centre import DiagnosticCentre
from app.models.diagnostic_test import DiagnosticTest
from app.schemas.catalogue import CentreCreate, CentreResponse, CentreTestCreate, CentreTestResponse


router = APIRouter(prefix="/centres", tags=["centres and tests"])


@router.post("", response_model=CentreResponse, status_code=status.HTTP_201_CREATED)
def create_centre(payload: CentreCreate, db: DbSession, user: CurrentUser):
    centre = DiagnosticCentre(name=payload.name.strip(), location=payload.location.strip())
    db.add(centre)
    db.commit()
    db.refresh(centre)
    return centre


@router.get("", response_model=list[CentreResponse])
def list_centres(db: DbSession):
    return list(db.scalars(select(DiagnosticCentre).order_by(DiagnosticCentre.name)))


@router.post("/{centre_id}/tests", response_model=CentreTestResponse, status_code=status.HTTP_201_CREATED)
def add_test_to_centre(centre_id: int, payload: CentreTestCreate, db: DbSession, user: CurrentUser):
    centre = db.get(DiagnosticCentre, centre_id)
    if centre is None:
        raise HTTPException(status_code=404, detail="Diagnostic centre not found")
    name = payload.test_name.strip()
    test = db.scalar(select(DiagnosticTest).where(DiagnosticTest.name == name))
    if test is None:
        test = DiagnosticTest(name=name, description=payload.description)
        db.add(test)
        db.flush()
    elif payload.description and not test.description:
        test.description = payload.description
    if db.scalar(select(CentreTest).where(CentreTest.centre_id == centre_id, CentreTest.test_id == test.id)):
        raise HTTPException(status_code=409, detail="This test is already offered by the centre")
    offering = CentreTest(centre_id=centre_id, test_id=test.id, price=Decimal(str(payload.price)))
    db.add(offering)
    db.commit()
    db.refresh(offering)
    return CentreTestResponse(offering_id=offering.id, centre_id=centre.id, centre_name=centre.name, test_id=test.id, test_name=test.name, description=test.description, price=float(offering.price))


@router.get("/{centre_id}/tests", response_model=list[CentreTestResponse])
def list_centre_tests(centre_id: int, db: DbSession):
    centre = db.get(DiagnosticCentre, centre_id)
    if centre is None:
        raise HTTPException(status_code=404, detail="Diagnostic centre not found")
    rows = db.execute(select(CentreTest, DiagnosticTest).join(DiagnosticTest, DiagnosticTest.id == CentreTest.test_id).where(CentreTest.centre_id == centre_id).order_by(DiagnosticTest.name)).all()
    return [CentreTestResponse(offering_id=o.id, centre_id=centre.id, centre_name=centre.name, test_id=t.id, test_name=t.name, description=t.description, price=float(o.price)) for o, t in rows]
