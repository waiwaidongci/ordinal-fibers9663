from src.services import treatment_service as service
def index(db,study_id):return service.list_treatments(db,study_id)
def create(db,data):return service.create_treatment(db,data)

def update(db,id,data):return service.update_treatment(db,id,data)
