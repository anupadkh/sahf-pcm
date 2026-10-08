from datetime import date
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from .config import COUNTRIES, TAXONOMY

class Project(BaseModel):
    title: str = Field(min_length=3, max_length=500)
    import_issues: str = Field(default='', max_length=50000)
    description: str = Field(default='', max_length=5000)
    external_id: str = Field(default='', max_length=200)
    implementing_partner: str = Field(default='', max_length=500)
    funding_partner: str = Field(min_length=1, max_length=300)
    country: str
    project_status: Literal['Planned', 'Ongoing', 'Completed'] = 'Ongoing'
    start_date: date | None = None
    end_date: date | None = None
    commitment_usd: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    pillars: list[int] = Field(default_factory=list)
    ibf_relevance: Literal['Yes', 'No', 'Partial'] = 'No'
    hazard: str = 'Flood'
    sector: str = 'DRR'
    multi_sector: bool = False
    notes: str = Field(default='', max_length=5000)
    confidence: Literal['High', 'Medium', 'Low'] = 'Medium'

    @model_validator(mode='after')
    def valid(self):
        if self.country not in COUNTRIES or self.hazard not in TAXONOMY['hazards'] or self.sector not in TAXONOMY['sectors']:
            raise ValueError('Country, hazard and sector must use the reference taxonomy')
        if any(p not in [1, 2, 3, 4] for p in self.pillars) or len(set(self.pillars)) != len(self.pillars):
            raise ValueError('Pillars must be unique values from 1 to 4')
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError('End date must follow start date')
        return self

class Login(BaseModel):
    email: str
    password: str

class Transition(BaseModel):
    action: Literal['submit', 'publish', 'return', 'approve_delete', 'reject_delete']
    note: str = Field(default='', max_length=3000)
    expected_updated:str|None=None

class Settings(BaseModel):
    enforce_pillars: bool
    require_ibf: Literal[True] = True

class Moderation(BaseModel):
    existing_id:str
    action:Literal['replace_existing','update_existing']
    changes:Project|None=None
    note:str=Field(min_length=1,max_length=3000)

class NewUser(BaseModel):
    email: str = Field(min_length=5, max_length=200)
    name: str = Field(min_length=2)
    password: str = Field(min_length=12)
    role: Literal['contributor', 'technical_manager', 'administrator']
    org: str = Field(min_length=2)
    country: str

class Deletion(BaseModel):
    note: str = Field(min_length=1,max_length=3000)
    expected_updated: str | None = None

class UserUpdate(BaseModel):
    name: str = Field(min_length=2,max_length=200)
    role: Literal['contributor','technical_manager','administrator']
    org: str = Field(min_length=2,max_length=300)
    country: str
    password: str | None = Field(default=None,min_length=12)
    active: bool = True

class ScreenColumn(BaseModel):
    key: str
    hidden_public: bool
    show_table: bool

class ScreenOptions(BaseModel):
    columns: list[ScreenColumn]
