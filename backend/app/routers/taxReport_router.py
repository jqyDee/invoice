from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm.session import Session

from ..schemas.taxReport_schema import TaxReportRow, TaxReportResponse
from ..services.taxReport_service import get_available_years, get_tax_report, get_tax_report_csv, get_travel_report, get_travel_report_csv
from ..utilities.database import get_db
from ..utilities.security import get_current_user

router = APIRouter(prefix="/tax-report", tags=["tax-report"], dependencies=[Depends(get_current_user)])


@router.get("/available-years", response_model=list[int])
def get_available_years_endpoint(db: Session = Depends(get_db)):
    return get_available_years(db)


@router.get("/{year}/amounts", response_model=TaxReportResponse)
def get_tax_report_endpoint(year: int, db: Session = Depends(get_db)):
    return get_tax_report(year, db)

@router.get("/{year}/travel", response_model=TaxReportResponse)
def get_travel_report_endpoint(year: int, db: Session = Depends(get_db)):
    return get_travel_report(year, db)


@router.get("/{year}/csv/amounts")
def get_tax_report_csv_endpoint(year: int, db: Session = Depends(get_db)):
    csv = get_tax_report_csv(year, db)
    return Response(
        content=csv,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=steuer_amounts_{year}.csv"},
    )

@router.get("/{year}/csv/travel")
def get_travel_report_csv_endpoint(year: int, db: Session = Depends(get_db)):
    csv = get_travel_report_csv(year, db)
    return Response(
        content=csv,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=steuer_travel_{year}.csv"},
    )
