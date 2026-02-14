"""
Cron Job Management Utility

Quick commands for managing monitoring jobs:
- List all jobs
- Clean up orphaned jobs
- Check system health
"""
import asyncio
import sys
from app.core.firebase import get_db
from app.services.cron_service import CronService
from app.services.monitoring_service import monitoring_service
from app.services.notification_service import notification_service


async def list_jobs():
    """List all monitoring jobs and their status."""
    db = get_db()
    
    print("\n" + "="*80)
    print("MONITORING JOBS STATUS")
    print("="*80)
    
    # Get all configs
    configs = db.collection('monitoring_configs').where('status', 'in', ['active', 'paused']).get()
    
    for config in configs:
        config_data = config.to_dict()
        job_id = config_data.get('apscheduler_job_id')
        
        print(f"\n📋 Config: {config.id}")
        print(f"   Competitor: {config_data.get('competitor')}")
        print(f"   Status: {config_data.get('status')}")
        print(f"   Frequency: {config_data.get('frequency_label')}")
        print(f"   Job ID: {job_id}")
        
        # Check if job exists in cron_jobs
        if job_id:
            job_doc = db.collection('cron_jobs').document(job_id).get()
            if job_doc.exists:
                job_data = job_doc.to_dict()
                print(f"   Job Status: {job_data.get('status')}")
                print(f"   Last Execution: {job_data.get('last_execution')}")
                print(f"   Error Count: {job_data.get('error_count', 0)}")
            else:
                print(f"   ⚠️  Job not found in cron_jobs collection")
        
        # Check for orphaned jobs
        orphaned = db.collection('cron_jobs').where('config_id', '==', config.id).get()
        orphaned_list = [j.id for j in orphaned if j.id != job_id]
        if orphaned_list:
            print(f"   ⚠️  Orphaned jobs: {', '.join(orphaned_list)}")
    
    print("\n" + "="*80)


async def cleanup():
    """Clean up orphaned jobs."""
    db = get_db()
    cron_service = CronService(db, monitoring_service, notification_service)
    await cron_service.start()
    
    print("\n🧹 Cleaning up orphaned jobs...")
    await cron_service._cleanup_all_orphaned_jobs()
    print("✅ Cleanup complete")
    
    cron_service.shutdown()


async def health_check():
    """Check system health."""
    db = get_db()
    
    print("\n" + "="*80)
    print("SYSTEM HEALTH CHECK")
    print("="*80)
    
    # Count configs
    all_configs = db.collection('monitoring_configs').stream()
    config_count = len(list(all_configs))
    
    active_configs = db.collection('monitoring_configs').where('status', '==', 'active').get()
    active_count = len(list(active_configs))
    
    paused_configs = db.collection('monitoring_configs').where('status', '==', 'paused').get()
    paused_count = len(list(paused_configs))
    
    # Count jobs
    all_jobs = db.collection('cron_jobs').stream()
    job_count = len(list(all_jobs))
    
    print(f"\n📊 Statistics:")
    print(f"   Total Configs: {config_count}")
    print(f"   Active Configs: {active_count}")
    print(f"   Paused Configs: {paused_count}")
    print(f"   Total Jobs: {job_count}")
    
    # Check for issues
    print(f"\n🔍 Issues:")
    
    # Check for orphaned jobs
    configs = db.collection('monitoring_configs').where('status', 'in', ['active', 'paused']).get()
    valid_job_ids = set()
    for config in configs:
        job_id = config.to_dict().get('apscheduler_job_id')
        if job_id:
            valid_job_ids.add(job_id)
    
    all_jobs = db.collection('cron_jobs').stream()
    orphaned = [j.id for j in all_jobs if j.id not in valid_job_ids]
    
    if orphaned:
        print(f"   ⚠️  {len(orphaned)} orphaned jobs found")
        print(f"      Run with 'cleanup' to remove them")
    else:
        print(f"   ✅ No orphaned jobs")
    
    # Check for duplicates
    configs = db.collection('monitoring_configs').where('status', 'in', ['active', 'paused']).get()
    for config in configs:
        config_id = config.id
        jobs = db.collection('cron_jobs').where('config_id', '==', config_id).get()
        job_count = len(list(jobs))
        if job_count > 1:
            print(f"   ⚠️  Config {config_id} has {job_count} jobs (should be 1)")
    
    if job_count == len(valid_job_ids):
        print(f"   ✅ No duplicate jobs")
    
    print("\n" + "="*80)


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_cron.py list     - List all jobs")
        print("  python manage_cron.py cleanup  - Clean up orphaned jobs")
        print("  python manage_cron.py health   - Check system health")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        await list_jobs()
    elif command == "cleanup":
        await cleanup()
    elif command == "health":
        await health_check()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    asyncio.run(main())
