from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.report import Report
from app.schemas.report import Report as ReportSchema, ReportCreate, ReportUpdate

router = APIRouter(tags=["reports"])

# GET - Sab reports
@router.get("/")
def get_all_reports(db: Session = Depends(get_db)):
    reports = db.query(Report).all()
    return reports

# GET - Report by type
@router.get("/type/{report_type}")
def get_reports_by_type(report_type: str, db: Session = Depends(get_db)):
    reports = db.query(Report).filter(Report.report_type == report_type).all()
    return reports

# GET - Single report
@router.get("/{report_id}", response_model=ReportSchema)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

# POST - Report create karo
@router.post("/", response_model=ReportSchema)
def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    db_report = Report(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

# PUT - Report update karo
@router.put("/{report_id}", response_model=ReportSchema)
def update_report(report_id: int, report: ReportUpdate, db: Session = Depends(get_db)):
    db_report = db.query(Report).filter(Report.id == report_id).first()
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    update_data = report.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_report, field, value)
    
    db.commit()
    db.refresh(db_report)
    return db_report

# DELETE - Report delete karo
@router.delete("/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    db_report = db.query(Report).filter(Report.id == report_id).first()
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    db.delete(db_report)
    db.commit()
    return {"message": "Report deleted"}