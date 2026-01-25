#!/usr/bin/env python3
"""
Simple API test script to verify Flask endpoints work.
Run with: python3 test_api.py
"""

import os
import sys
import tempfile
import json

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docker'))

# Import directly from the app module
import importlib.util
app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docker', 'app.py')
spec = importlib.util.spec_from_file_location("app", app_path)
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)

app = app_module.app
create_job = app_module.create_job
update_job = app_module.update_job
get_job = app_module.get_job

def test_job_registry():
    """Test job tracking system."""
    print("Testing job registry...")
    
    # Create a job
    job_id = create_job("TestProject")
    assert job_id, "Failed to create job"
    print(f"✓ Created job: {job_id}")
    
    # Get the job
    job = get_job(job_id)
    assert job is not None, "Failed to retrieve job"
    assert job['state'] == 'queued', "Job should start in 'queued' state"
    print(f"✓ Job state: {job['state']}")
    
    # Update the job
    update_job(job_id, state='processing', percent=50, message='Testing...')
    job = get_job(job_id)
    assert job['state'] == 'processing', "Job should be 'processing'"
    assert job['percent'] == 50, "Job percent should be 50"
    print(f"✓ Updated job: state={job['state']}, percent={job['percent']}")
    
    # Complete the job
    update_job(job_id, state='completed', percent=100, message='Done!')
    job = get_job(job_id)
    assert job['state'] == 'completed', "Job should be 'completed'"
    print(f"✓ Job completed")
    
    print("✅ Job registry tests passed!\n")


def test_flask_endpoints():
    """Test Flask endpoints with test client."""
    print("Testing Flask endpoints...")
    
    with app.test_client() as client:
        # Test /health
        print("  Testing GET /health...")
        response = client.get('/health')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = json.loads(response.data)
        assert data['status'] == 'healthy', "Should be healthy"
        print("  ✓ /health works")
        
        # Test /api/config
        print("  Testing GET /api/config...")
        response = client.get('/api/config')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = json.loads(response.data)
        assert 'defaults' in data, "Response should have 'defaults'"
        assert 'presets' in data, "Response should have 'presets'"
        print(f"  ✓ /api/config works (found {len(data['presets'])} presets)")
        
        # Test /api/process with missing file
        print("  Testing POST /api/process (missing file)...")
        response = client.post('/api/process', data={})
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("  ✓ /api/process validates file upload")
        
        # Test /api/status with fake job
        print("  Testing GET /api/status (nonexistent job)...")
        response = client.get('/api/status/fake-job-id')
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("  ✓ /api/status returns 404 for missing job")
    
    print("✅ Flask endpoint tests passed!\n")


if __name__ == '__main__':
    print("=" * 50)
    print("AlongGPX API Test Suite")
    print("=" * 50 + "\n")
    
    try:
        test_job_registry()
        test_flask_endpoints()
        
        print("=" * 50)
        print("✅ All tests passed!")
        print("=" * 50)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
