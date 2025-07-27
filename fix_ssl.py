import os
import ssl
import certifi
import urllib3
import sys

def fix_ssl_certificates():
    """Fix SSL certificate verification issues in Python."""
    print("Fixing SSL certificate verification issues...")
    
    # Set environment variables for certificate verification
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
    
    # Disable SSL warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Print certificate information
    print(f"Certificate path: {certifi.where()}")
    print(f"Default SSL context: {ssl.get_default_verify_paths()}")
    
    # Create a new default SSL context
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        print("Created unverified SSL context as default")
    except AttributeError:
        print("Could not set unverified SSL context")
    
    # For macOS specific issues
    if sys.platform == 'darwin':
        print("\nMacOS detected. You may need additional steps:")
        print("1. Run the following command in Terminal:")
        print("   /Applications/Python*/Install\\ Certificates.command")
        print("2. Or run the bash script provided (ssl_fix_script.sh)")
    
    print("\nSSL certificate setup complete!")

if __name__ == "__main__":
    fix_ssl_certificates()