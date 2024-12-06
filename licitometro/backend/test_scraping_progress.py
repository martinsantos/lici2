import asyncio
import time
from datetime import datetime
from core.database import SessionLocal
from recon_service.models import ScrapingJob, ScrapingTemplate, ScrapingStatus
from recon_service.tasks import run_scraping_task

def create_test_template() -> int:
    db = SessionLocal()
    try:
        template = ScrapingTemplate(
            name='Test Mock Scraper',
            url='mock://test',
            fields={
                'title': '.title',
                'date': '.date',
                'organism': '.organism'
            },
            is_active=True,
            scraper_type='mock'  # Add mock scraper type
        )
        db.add(template)
        db.commit()
        print(f"Created template with ID: {template.id}")
        return template.id
    finally:
        db.close()

def create_test_job(template_id: int) -> int:
    db = SessionLocal()
    try:
        job = ScrapingJob(
            template_id=template_id,
            status=ScrapingStatus.PENDING
        )
        db.add(job)
        db.commit()
        return job.id
    finally:
        db.close()

def monitor_job_progress(job_id: int, interval: float = 1.0):
    db = SessionLocal()
    try:
        while True:
            job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
            if not job:
                print(f"Job {job_id} not found")
                break
                
            # Print progress message if it has changed
            if hasattr(monitor_job_progress, 'last_message') and monitor_job_progress.last_message == job.progress_message:
                if job.status in [ScrapingStatus.COMPLETED, ScrapingStatus.FAILED]:
                    break
                time.sleep(interval)
                continue
                
            # Update last message and print current status
            monitor_job_progress.last_message = job.progress_message
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"[{current_time}] Status: {job.status}")
            if job.progress_message:
                print(f"Progress: {job.progress_message}")
            print("-" * 80)
            
            if job.status in [ScrapingStatus.COMPLETED, ScrapingStatus.FAILED]:
                if job.result:
                    print("Final Results:", job.result)
                if job.error_message:
                    print("Error:", job.error_message)
                break
                
            time.sleep(interval)
    finally:
        db.close()

if __name__ == "__main__":
    # Create template and job
    template_id = create_test_template()
    job_id = create_test_job(template_id)
    print(f"Created job with ID: {job_id}")
    
    # Start the job
    run_scraping_task(job_id)
    
    # Monitor progress
    monitor_job_progress(job_id)
