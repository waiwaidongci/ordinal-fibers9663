from fastapi import APIRouter,Depends
from src.config.database import get_db
from src.utils.auth import current_user,editor,admin
from src.schemas.treatment import TreatmentInput,TreatmentOut
from src.controllers import treatment_controller as controller
router=APIRouter(prefix='/treatments',tags=['treatments'])
@router.get('',response_model=list[TreatmentOut])
def index(study_id:int,db=Depends(get_db),user=Depends(current_user)):return controller.index(db,study_id)
@router.post('',response_model=TreatmentOut,status_code=201)
def create(data:TreatmentInput,db=Depends(get_db),user=Depends(editor)):return controller.create(db,data)
@router.put('/{id}',response_model=TreatmentOut)
def update(id:int,data:TreatmentInput,db=Depends(get_db),user=Depends(editor)):return controller.update(db,id,data)
