#!/usr/bin/env python3
"""
CareerCraft AI Setup Script

This script initializes the CareerCraft AI system with secure configuration.
Run this script before first deployment to set up encrypted credentials.
"""

import os
import sys
import json
import secrets
import getpass
from pathlib import Path
from cryptography.fernet import Fernet
from typing import Dict, Any


class SecureSetup:
    """Secure setup manager for CareerCraft AI"""
    
    def __init__(self):
        self.config_dir = Path("config")
        self.config_dir.mkdir(exist_ok=True)
        self.key_file = self.config_dir / "encryption.key"
        self.config_file = self.config_dir / "config.enc"
        
    def generate_encryption_key(self) -> bytes:
        """Generate or load encryption key"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                key = f.read()
            print("✓ Using existing encryption key")
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            os.chmod(self.key_file, 0o600)  # Owner read/write only
            print("✓ Generated new encryption key")
        return key
    
    def collect_configuration(self) -> Dict[str, Any]:
        """Collect configuration from user"""
        print("\n🔧 CareerCraft AI Configuration Setup")
        print("=" * 50)
        
        config = {}
        
        # Claude API Configuration
        print("\n📡 Claude API Configuration")
        config['claude_api_key'] = getpass.getpass("Enter Claude API Key: ")
        
        # Database Configuration
        print("\n🗄️  Database Configuration")
        config['database_url'] = input("Database URL [sqlite:///./careercraft.db]: ") or "sqlite:///./careercraft.db"
        
        # Security Configuration
        print("\n🔒 Security Configuration")
        config['jwt_secret'] = secrets.token_urlsafe(32)
        config['api_key'] = secrets.token_urlsafe(16)
        config['api_secret'] = secrets.token_urlsafe(32)
        
        # Session Configuration
        print("\n⏰ Session Configuration")
        timeout = input("Session timeout in minutes [30]: ") or "30"
        config['session_timeout'] = int(timeout)
        
        # File Processing Configuration
        print("\n📄 File Processing Configuration")
        max_size = input("Maximum file size in MB [10]: ") or "10"
        config['max_file_size'] = int(max_size) * 1024 * 1024  # Convert to bytes
        
        # Rate Limiting Configuration
        print("\n🚦 Rate Limiting Configuration")
        rate_limit = input("API rate limit (requests per minute) [60]: ") or "60"
        config['rate_limit'] = int(rate_limit)
        
        print(f"\n✓ Generated API Key: {config['api_key']}")
        print(f"✓ Generated API Secret: {config['api_secret'][:8]}...")
        print(f"✓ Generated JWT Secret: {config['jwt_secret'][:8]}...")
        
        return config
    
    def encrypt_config(self, config: Dict[str, Any], key: bytes) -> None:
        """Encrypt and save configuration"""
        fernet = Fernet(key)
        config_json = json.dumps(config, indent=2)
        encrypted_config = fernet.encrypt(config_json.encode())
        
        with open(self.config_file, 'wb') as f:
            f.write(encrypted_config)
        os.chmod(self.config_file, 0o600)  # Owner read/write only
        print("✓ Configuration encrypted and saved")
    
    def verify_setup(self, key: bytes) -> bool:
        """Verify the setup by decrypting config"""
        try:
            fernet = Fernet(key)
            with open(self.config_file, 'rb') as f:
                encrypted_config = f.read()
            
            decrypted_config = fernet.decrypt(encrypted_config)
            config = json.loads(decrypted_config.decode())
            
            print("\n✅ Configuration verification successful!")
            print(f"   - Database: {config.get('database_url')}")
            print(f"   - Session timeout: {config.get('session_timeout')} minutes")
            print(f"   - Max file size: {config.get('max_file_size', 0) // (1024*1024)} MB")
            print(f"   - Rate limit: {config.get('rate_limit')} requests/minute")
            return True
            
        except Exception as e:
            print(f"❌ Configuration verification failed: {e}")
            return False
    
    def create_env_template(self) -> None:
        """Create environment template file"""
        env_template = """# CareerCraft AI Environment Configuration
# Copy this file to .env and configure as needed

# Development/Production mode
ENVIRONMENT=development

# Frontend URL for CORS
FRONTEND_URL=http://localhost:3000

# Server configuration
HOST=127.0.0.1
PORT=8000

# Logging configuration
LOG_LEVEL=INFO
LOG_FILE=logs/careercraft.log

# Optional: Override default file paths
# CONFIG_DIR=./config
# ENCRYPTION_KEY_FILE=./config/encryption.key
# CONFIG_FILE=./config/config.enc
"""
        
        with open(".env.template", "w") as f:
            f.write(env_template)
        print("✓ Created .env.template file")
    
    def run(self) -> None:
        """Run the complete setup process"""
        print("🚀 CareerCraft AI Secure Setup")
        print("=" * 50)
        
        # Check if already configured
        if self.config_file.exists():
            response = input("\n⚠️  Configuration already exists. Reconfigure? (y/N): ")
            if response.lower() != 'y':
                print("Setup cancelled.")
                return
        
        try:
            # Generate encryption key
            key = self.generate_encryption_key()
            
            # Collect configuration
            config = self.collect_configuration()
            
            # Encrypt and save
            self.encrypt_config(config, key)
            
            # Verify setup
            if self.verify_setup(key):
                self.create_env_template()
                print("\n🎉 Setup completed successfully!")
                print("\nNext steps:")
                print("1. Copy .env.template to .env and configure as needed")
                print("2. Install dependencies: pip install -r requirements.txt")
                print("3. Run the application: uvicorn main:app --reload")
                print(f"\n📋 Save these credentials for frontend configuration:")
                print(f"   API Key: {config['api_key']}")
                print(f"   API Secret: {config['api_secret']}")
            else:
                print("\n❌ Setup failed during verification!")
                sys.exit(1)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Setup cancelled by user.")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    setup = SecureSetup()
    setup.run()