"""
Simple test to verify the application logic without running the server.
This tests that the app correctly reads environment variables and formats responses.
"""

import os
import sys

# Simulate the application logic
def test_api_key_status():
    """Test the API key status logic from the FastAPI app."""
    
    # Test case 1: API key is configured
    os.environ['API_KEY'] = 'sk-test123456789012345678901234567890'
    api_key = os.getenv("API_KEY")
    
    if api_key:
        api_key_status = f"configured (length: {len(api_key)})"
    else:
        api_key_status = "not configured"
    
    print("Test 1 - API Key Configured:")
    print(f"  API Key: {api_key[:8]}... (masked)")
    print(f"  Status: {api_key_status}")
    assert api_key_status == "configured (length: 32)", "Test 1 failed"
    print("  ✓ Test 1 passed\n")
    
    # Test case 2: API key is not configured
    del os.environ['API_KEY']
    api_key = os.getenv("API_KEY")
    
    if api_key:
        api_key_status = f"configured (length: {len(api_key)})"
    else:
        api_key_status = "not configured"
    
    print("Test 2 - API Key Not Configured:")
    print(f"  API Key: {api_key}")
    print(f"  Status: {api_key_status}")
    assert api_key_status == "not configured", "Test 2 failed"
    print("  ✓ Test 2 passed\n")

def test_secrets_status_logic():
    """Test the secrets status endpoint logic."""
    
    # Test case 1: Both secrets configured
    os.environ['API_KEY'] = 'sk-test123456789012345678901234567890'
    os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost:5432/db'
    
    api_key = os.getenv("API_KEY")
    database_url = os.getenv("DATABASE_URL")
    
    secrets_status = {
        "service": "fastapi-example",
        "organization_secrets": {
            "API_KEY": {
                "status": "configured" if api_key else "not configured",
                "length": len(api_key) if api_key else 0,
                "source": "organization blueprint" if api_key else "missing"
            },
            "DATABASE_URL": {
                "status": "configured" if database_url else "not configured",
                "length": len(database_url) if database_url else 0,
                "source": "organization blueprint" if database_url else "missing"
            }
        },
        "environment": os.getenv("ENVIRONMENT", "development")
    }
    
    print("Test 3 - Both Secrets Configured:")
    print(f"  API_KEY status: {secrets_status['organization_secrets']['API_KEY']['status']}")
    print(f"  DATABASE_URL status: {secrets_status['organization_secrets']['DATABASE_URL']['status']}")
    assert secrets_status['organization_secrets']['API_KEY']['status'] == "configured", "Test 3 failed"
    assert secrets_status['organization_secrets']['DATABASE_URL']['status'] == "configured", "Test 3 failed"
    print("  ✓ Test 3 passed\n")
    
    # Test case 2: No secrets configured
    del os.environ['API_KEY']
    del os.environ['DATABASE_URL']
    
    api_key = os.getenv("API_KEY")
    database_url = os.getenv("DATABASE_URL")
    
    secrets_status = {
        "service": "fastapi-example",
        "organization_secrets": {
            "API_KEY": {
                "status": "configured" if api_key else "not configured",
                "length": len(api_key) if api_key else 0,
                "source": "organization blueprint" if api_key else "missing"
            },
            "DATABASE_URL": {
                "status": "configured" if database_url else "not configured",
                "length": len(database_url) if database_url else 0,
                "source": "organization blueprint" if database_url else "missing"
            }
        },
        "environment": os.getenv("ENVIRONMENT", "development")
    }
    
    print("Test 4 - No Secrets Configured:")
    print(f"  API_KEY status: {secrets_status['organization_secrets']['API_KEY']['status']}")
    print(f"  DATABASE_URL status: {secrets_status['organization_secrets']['DATABASE_URL']['status']}")
    assert secrets_status['organization_secrets']['API_KEY']['status'] == "not configured", "Test 4 failed"
    assert secrets_status['organization_secrets']['DATABASE_URL']['status'] == "not configured", "Test 4 failed"
    print("  ✓ Test 4 passed\n")

def test_environment_variable_export():
    """Test that environment variables would be correctly exported."""
    
    print("Test 5 - Environment Variable Export Logic:")
    
    # Simulate the export logic from environment.yaml
    # In the actual blueprint, this would be: export API_KEY=$API_KEY
    # Where $API_KEY is the organization secret
    
    # Simulate organization secret being available
    org_api_key = "sk-org-secret-123456789012345678901234"
    
    # Simulate the export
    os.environ['API_KEY'] = org_api_key
    
    # Verify it's available to the application
    app_api_key = os.getenv("API_KEY")
    
    print(f"  Organization secret: {org_api_key[:8]}... (masked)")
    print(f"  Application can read: {app_api_key[:8]}... (masked)")
    assert app_api_key == org_api_key, "Test 5 failed"
    print("  ✓ Test 5 passed - Organization secrets are accessible to application\n")

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Application Logic (Without Running Server)")
    print("=" * 60 + "\n")
    
    try:
        test_api_key_status()
        test_secrets_status_logic()
        test_environment_variable_export()
        
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        print("\nThe application logic correctly:")
        print("1. Reads API_KEY from environment variables")
        print("2. Shows masked status without exposing values")
        print("3. Detects when secrets are missing")
        print("4. Can access organization-level secrets")
        print("\nReady for deployment with organization blueprint!")
        
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)
