#!/usr/bin/env python
import os
import sys
import subprocess
import django
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crop_recommendation.settings')
django.setup()

def run_migrations():
    """Run Django migrations"""
    print("Running migrations...")
    try:
        # Try to run migrations normally
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
        print("Migrations completed successfully.")
        return True
    except subprocess.CalledProcessError:
        print("Migration command failed. Will try direct table creation.")
        return False

def create_tables_directly():
    """Create essential tables directly if migrations fail"""
    print("Creating tables directly...")
    with connection.cursor() as cursor:
        # Create django_session table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS django_session (
            session_key VARCHAR(40) NOT NULL PRIMARY KEY, 
            session_data TEXT NOT NULL, 
            expire_date TIMESTAMP WITH TIME ZONE NOT NULL
        )
        ''')
        print("Created django_session table.")
        
        # Create django_site table if needed
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS django_site (
            id SERIAL PRIMARY KEY, 
            domain VARCHAR(100) NOT NULL, 
            name VARCHAR(50) NOT NULL
        )
        ''')
        
        # Insert default site if not exists
        cursor.execute('''
        INSERT INTO django_site (id, domain, name) 
        VALUES (1, 'example.com', 'example') 
        ON CONFLICT DO NOTHING
        ''')
        print("Created django_site table and inserted default site.")

def main():
    """Main function to fix migrations"""
    print("Starting migration fix...")
    
    # First try running migrations normally
    if not run_migrations():
        # If migrations fail, create tables directly
        create_tables_directly()
    
    print("Migration fix completed.")

if __name__ == "__main__":
    main()