from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class ScrapingProgress:
    total_found: int = 0
    processed: int = 0
    saved: int = 0
    errors: int = 0
    skipped: int = 0
    current_page: int = 1
    current_status: str = ""
    error_details: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    last_saved_title: str = ""
    last_error: str = ""
    template_name: str = ""
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                
    def add_error(self, error: str):
        self.errors += 1
        self.error_details.append(error)
        self.last_error = error
        
    def add_success(self, title: str):
        self.saved += 1
        self.last_saved_title = title
        
    def to_dict(self) -> Dict:
        elapsed_time = datetime.now() - self.start_time
        success_rate = (self.saved / self.processed * 100) if self.processed > 0 else 0
        error_rate = (self.errors / self.processed * 100) if self.processed > 0 else 0
        
        return {
            'total_found': self.total_found,
            'processed': self.processed,
            'saved': self.saved,
            'errors': self.errors,
            'skipped': self.skipped,
            'current_page': self.current_page,
            'current_status': self.current_status,
            'error_details': self.error_details[-5:],  # últimos 5 errores
            'elapsed_time': str(elapsed_time).split('.')[0],
            'percent_complete': round((self.processed / self.total_found * 100) if self.total_found > 0 else 0, 2),
            'success_rate': round(success_rate, 2),
            'error_rate': round(error_rate, 2),
            'last_saved': self.last_saved_title,
            'last_error': self.last_error,
            'template_name': self.template_name,
            'items_per_minute': round((self.processed / elapsed_time.total_seconds() * 60) if elapsed_time.total_seconds() > 0 else 0, 2)
        }
