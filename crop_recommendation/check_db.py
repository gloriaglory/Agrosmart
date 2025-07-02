#!/usr/bin/env python
import os
import sys
import django
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crop_recommendation.settings')
django.setup()

def check_tables():
    """Check if essential tables exist in the database"""
    print("Checking essential tables...")
    
    with connection.cursor() as cursor:
        # Check if django_session table exists
        cursor.execute("""
        SELECT EXISTS (
           SELECT FROM information_schema.tables 
           WHERE table_name = 'django_session'
        )
        """)
        session_exists = cursor.fetchone()[0]
        
        if session_exists:
            print('django_session table exists.')
        else:
            print('ERROR: django_session table does not exist!')
        
        # Check if django_site table exists
        cursor.execute("""
        SELECT EXISTS (
           SELECT FROM information_schema.tables 
           WHERE table_name = 'django_site'
        )
        """)
        site_exists = cursor.fetchone()[0]
        
        if site_exists:
            print('django_site table exists.')
        else:
            print('ERROR: django_site table does not exist!')
        
        # Check if authentication_user table exists
        cursor.execute("""
        SELECT EXISTS (
           SELECT FROM information_schema.tables 
           WHERE table_name = 'authentication_user'
        )
        """)
        user_exists = cursor.fetchone()[0]
        
        if user_exists:
            print('authentication_user table exists.')
        else:
            print('ERROR: authentication_user table does not exist!')
        
        # Check if authtoken_token table exists
        cursor.execute("""
        SELECT EXISTS (
           SELECT FROM information_schema.tables 
           WHERE table_name = 'authtoken_token'
        )
        """)
        token_exists = cursor.fetchone()[0]
        
        if token_exists:
            print('authtoken_token table exists.')
        else:
            print('ERROR: authtoken_token table does not exist!')

if __name__ == "__main__":
    check_tables()