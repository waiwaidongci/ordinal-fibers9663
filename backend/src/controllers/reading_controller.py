from src.services import reading_service as service
def index(db,study_id):return service.list_readings(db,study_id)
def create(db,data):return service.create_reading(db,data)

def update(db,id,data):return service.update_reading(db,id,data)
