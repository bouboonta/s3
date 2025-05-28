from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все домены (для разработки)
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все HTTP-методы
    allow_headers=["*"],  # Разрешаем все заголовки
)

# Модели данных
class Volunteer(BaseModel):
    name: str
    email: str
    phone: str

class VolunteerResponse(Volunteer):
    id: str

class Event(BaseModel):
    title: str
    description: str
    date: str  # Формат: "YYYY-MM-DD"
    location: str
    max_participants: int

class EventResponse(Event):
    id: str

class Participation(BaseModel):
    volunteer_id: str
    event_id: str

class ParticipationResponse(Participation):
    id: str
    registration_date: str

# "База данных" в памяти
db_volunteers = []
db_events = []
db_participations = []

# ========== ВОЛОНТЕРЫ ==========
@app.post("/volunteers", response_model=VolunteerResponse)
def create_volunteer(volunteer: Volunteer):
    """Создание нового волонтера"""
    volunteer_dict = volunteer.dict()
    volunteer_dict["id"] = str(uuid.uuid4())
    db_volunteers.append(volunteer_dict)
    return volunteer_dict

@app.get("/volunteers", response_model=List[VolunteerResponse])
def get_volunteers():
    """Получение списка всех волонтеров"""
    return db_volunteers

@app.get("/volunteers/{volunteer_id}", response_model=VolunteerResponse)
def get_volunteer(volunteer_id: str):
    """Получение волонтера по ID"""
    for volunteer in db_volunteers:
        if volunteer["id"] == volunteer_id:
            return volunteer
    raise HTTPException(status_code=404, detail="Volunteer not found")

@app.put("/volunteers/{volunteer_id}", response_model=VolunteerResponse)
def update_volunteer(volunteer_id: str, updated_volunteer: Volunteer):
    """Обновление данных волонтера"""
    for volunteer in db_volunteers:
        if volunteer["id"] == volunteer_id:
            volunteer.update(updated_volunteer.dict())
            return volunteer
    raise HTTPException(status_code=404, detail="Volunteer not found")

@app.delete("/volunteers/{volunteer_id}")
def delete_volunteer(volunteer_id: str):
    """Удаление волонтера"""
    global db_volunteers
    db_volunteers = [v for v in db_volunteers if v["id"] != volunteer_id]
    return {"message": "Volunteer deleted"}

# ========== МЕРОПРИЯТИЯ ==========
@app.post("/events", response_model=EventResponse)
def create_event(event: Event):
    """Создание нового мероприятия"""
    event_dict = event.dict()
    event_dict["id"] = str(uuid.uuid4())
    db_events.append(event_dict)
    return event_dict

@app.get("/events", response_model=List[EventResponse])
def get_events():
    """Получение списка всех мероприятий"""
    return db_events

@app.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: str):
    """Получение мероприятия по ID"""
    for event in db_events:
        if event["id"] == event_id:
            return event
    raise HTTPException(status_code=404, detail="Event not found")

@app.put("/events/{event_id}", response_model=EventResponse)
def update_event(event_id: str, updated_event: Event):
    """Обновление данных мероприятия"""
    for event in db_events:
        if event["id"] == event_id:
            event.update(updated_event.dict())
            return event
    raise HTTPException(status_code=404, detail="Event not found")

@app.delete("/events/{event_id}")
def delete_event(event_id: str):
    """Удаление мероприятия"""
    global db_events
    db_events = [e for e in db_events if e["id"] != event_id]
    return {"message": "Event deleted"}

# ========== УЧАСТИЕ ==========
@app.post("/participations", response_model=ParticipationResponse)
def create_participation(participation: Participation):
    """Регистрация волонтера на мероприятие"""
    # Проверка существования волонтера и мероприятия
    volunteer_exists = any(v["id"] == participation.volunteer_id for v in db_volunteers)
    event_exists = any(e["id"] == participation.event_id for e in db_events)
    
    if not volunteer_exists or not event_exists:
        raise HTTPException(
            status_code=404,
            detail="Volunteer or Event not found"
        )
    
    # Проверка дублирования регистрации
    existing_participation = any(
        p["volunteer_id"] == participation.volunteer_id and 
        p["event_id"] == participation.event_id
        for p in db_participations
    )
    if existing_participation:
        raise HTTPException(
            status_code=400,
            detail="Volunteer already registered for this event"
        )
    
    participation_dict = participation.dict()
    participation_dict["id"] = str(uuid.uuid4())
    participation_dict["registration_date"] = datetime.now().isoformat()
    db_participations.append(participation_dict)
    return participation_dict

@app.get("/participations", response_model=List[ParticipationResponse])
def get_participations():
    """Получение списка всех регистраций"""
    return db_participations

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)