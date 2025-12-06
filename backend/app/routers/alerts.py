from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models, database, auth, crud

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)

@router.get("/", response_model=List[schemas.Alert])
def read_alerts(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.get_alerts(db, user_id=current_user.id)

@router.post("/", response_model=schemas.Alert)
def create_alert(
    alert: schemas.AlertCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verify stock exists
    db_stock = crud.get_stock(db, stock_id=alert.stock_id)
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
        
    return crud.create_alert(db, alert=alert, user_id=current_user.id)

@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    alert_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_alert = db.query(models.Alert).filter(
        models.Alert.id == alert_id,
        models.Alert.user_id == current_user.id
    ).first()
    
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(db_alert)
    db.commit()
    return None
