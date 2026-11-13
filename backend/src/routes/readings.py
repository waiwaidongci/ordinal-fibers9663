from fastapi import APIRouter,Depends
from src.config.database import get_db
from src.utils.auth import current_user,editor,admin
from src.schemas.reading import ReadingInput,ReadingOut
from src.controllers import reading_controller as controller
router=APIRouter(prefix='/readings',tags=['readings'])
@router.get('',response_model=list[ReadingOut])
def index(study_id:int,db=Depends(get_db),user=Depends(current_user)):return controller.index(db,study_id)
@router.post('',response_model=ReadingOut,status_code=201)
def create(data:ReadingInput,db=Depends(get_db),user=Depends(editor)):return controller.create(db,data)
@router.put('/{id}',response_model=ReadingOut)
def update(id:int,data:ReadingInput,db=Depends(get_db),user=Depends(editor)):return controller.update(db,id,data)
