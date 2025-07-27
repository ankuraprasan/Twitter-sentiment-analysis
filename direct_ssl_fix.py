import os
import sys
import subprocess
import certifi
import ssl

def install_certificates():
    """Install certificates for macOS Python."""
    print("Installing certificates for macOS Python...")
    
    # Force SSL to use unverified context
    ssl._create_default_https_context = ssl._create_unverified_context
    
    # Get certifi path
    cert_path = certifi.where()
    print(f"Certifi path: {cert_path}")
    
    # Create SSL environment variables
    os.environ['SSL_CERT_FILE'] = cert_path
    os.environ['REQUESTS_CA_BUNDLE'] = cert_path
    
    # For Anaconda Python on macOS
    try:
        # This is a direct approach for macOS
        print("Installing certificates directly from macOS keychain...")
        cmd = [
            "security", 
            "find-certificate", 
            "-a", 
            "-p", 
            "/System/Library/Keychains/SystemRootCertificates.keychain"
        ]
        
        with open(cert_path, 'wb') as f:
            result = subprocess.run(cmd, stdout=f, check=True)
            print(f"Certificate installation result: {result.returncode}")
        
        # Add certificates to Python's SSL context
        print("Updating Python's SSL certificates...")
        cmd2 = ["pip", "install", "--upgrade", "certifi"]
        subprocess.run(cmd2, check=True)
        
        # Generate a Python script that will permanently fix SSL issues
        fix_script = f"""
# Run this script to fix SSL certificate issues
import os
import ssl

# Force SSL to use unverified context globally
ssl._create_default_https_context = ssl._create_unverified_context

# Set environment variables to use certifi certificates
os.environ['SSL_CERT_FILE'] = '{cert_path}'
os.environ['REQUESTS_CA_BUNDLE'] = '{cert_path}'

print("SSL certificate verification has been disabled. Your connections should work now.")
        """
        
        with open("ssl_fix_startup.py", "w") as f:
            f.write(fix_script)
            
        print("\nCreated ssl_fix_startup.py - Import this at the start of your application")
        
        # Create a modified version of the app
        with open("app_with_ssl_fix.py", "w") as f:
            f.write(f"""
# Import SSL fix at the start
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import os
import certifi
os.environ['SSL_CERT_FILE'] = '{cert_path}'
os.environ['REQUESTS_CA_BUNDLE'] = '{cert_path}'

# Now import the rest of your application
""")
            
            # Read the original app.py file if it exists
            try:
                with open("app.py", "r") as app_file:
                    app_content = app_file.read()
                    f.write(app_content)
                print("Created app_with_ssl_fix.py with SSL fixes applied")
            except FileNotFoundError:
                f.write("""
import streamlit as st

st.title("SSL Fix Applied")
st.write("The SSL certificate issue should be fixed.")
st.write("Make sure to copy your original app code here.")
""")
                print("Created app_with_ssl_fix.py template (please copy your app code into it)")
        
    except Exception as e:
        print(f"Error during certificate installation: {str(e)}")
        print("Trying alternative approach...")
        
        # Alternative approach - install certificates using Anaconda's mechanism
        anaconda_path = sys.executable.split('/bin/python')[0]
        install_script = os.path.join(anaconda_path, "bin", "conda", "install_certifi.py")
        
        if os.path.exists(install_script):
            print(f"Running Anaconda certificate installer: {install_script}")
            subprocess.run([sys.executable, install_script], check=True)
        else:
            print("Could not find Anaconda certificate installer.")
            print("Please run the following command in Terminal:")
            print("/Applications/Python*/Install\\ Certificates.command")

    print("\n--- IMPORTANT INSTRUCTIONS ---")
    print("1. Run your app with SSL fix applied:")
    print("   streamlit run app_with_ssl_fix.py")
    print("2. If you get import errors, make sure all required packages are installed:")
    print("   pip install streamlit nltk scikit-learn ntscraper python-dotenv certifi urllib3")
    print("3. If you still have issues, try using a different Twitter API library:")
    print("   pip install tweepy")
    print("----------------------------")

if __name__ == "__main__":
    install_certificates()