from dataclasses import dataclass
from typing import Optional


@dataclass
class UserProfile:
  id: int
  remote_preference: bool
  hybrid_preference: bool
  in_person_preference: bool
  age_range: Optional[str] = None
  hours_per_week: Optional[int] = None
  location: Optional[str] = None
  accommodations: Optional[list[str]] = None
  educational_background: Optional[list[str]] = None

  @classmethod
  def from_supabase_dict(cls, data: dict):
    return cls(
      id=int(data.get('id', 0)),
      remote_preference=data.get('remote_preference', False),
      hybrid_preference=data.get('hybrid_preference', False),
      in_person_preference=data.get('in_person_preference', False),
      age_range=data.get('age_range'),
      hours_per_week=data.get('hours_per_week'),
      location=data.get('location'),
      accommodations=data.get('accommodations', []),
      educational_background=data.get('educational_background', [])
    )