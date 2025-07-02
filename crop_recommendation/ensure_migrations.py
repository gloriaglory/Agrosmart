#!/usr/bin/env python
import os
import sys
import subprocess
import django
from django.db import connection, DatabaseError

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crop_recommendation.settings')
django.setup()

def run_command(command):
    """Run a shell command and return True if successful, False otherwise"""
    print(f"Running command: {' '.join(command)}")
    try:
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"Command failed: {' '.join(command)}")
        return False

def run_migrations():
    """Run Django migrations"""
    print("Running migrations...")

    # First, try to make migrations
    if not run_command([sys.executable, 'manage.py', 'makemigrations', '--noinput']):
        print("Making migrations failed, but continuing...")

    # Try to run migrations normally
    if run_command([sys.executable, 'manage.py', 'migrate', '--noinput']):
        print("Migrations completed successfully.")
        return True

    # If normal migrations fail, try fixing common issues
    print("Migration failed, attempting to fix common issues...")

    # Fix conflicting migrations by faking them
    print("Fixing conflicting migrations...")
    run_command([sys.executable, 'manage.py', 'migrate', 'market_place', '0003_marketplaceitem_image', '--fake'])

    # Try migrations again
    if run_command([sys.executable, 'manage.py', 'migrate', '--noinput']):
        print("Migrations completed successfully after fixing conflicts.")
        return True

    print("Migrations still failing after fixing conflicts.")
    return False

def create_tables_directly():
    """Create essential tables directly if migrations fail"""
    print("Creating tables directly...")
    try:
        with connection.cursor() as cursor:
            # First check if django_session table exists
            cursor.execute("""
            SELECT EXISTS (
               SELECT FROM information_schema.tables 
               WHERE table_name = 'django_session'
            )
            """)
            session_exists = cursor.fetchone()[0]

            if session_exists:
                print("django_session table already exists.")
            else:
                # Create django_session table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS django_session (
                    session_key VARCHAR(40) NOT NULL PRIMARY KEY, 
                    session_data TEXT NOT NULL, 
                    expire_date TIMESTAMP WITH TIME ZONE NOT NULL
                )
                ''')
                print("Created django_session table.")

                # Verify the table was created
                cursor.execute("""
                SELECT EXISTS (
                   SELECT FROM information_schema.tables 
                   WHERE table_name = 'django_session'
                )
                """)
                session_created = cursor.fetchone()[0]
                if not session_created:
                    print("ERROR: Failed to create django_session table!")
                    return False

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

            # Create authentication_user table with phone_number field
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS authentication_user (
                id SERIAL PRIMARY KEY, 
                password VARCHAR(128) NOT NULL, 
                last_login TIMESTAMP WITH TIME ZONE NULL, 
                is_superuser BOOLEAN NOT NULL, 
                username VARCHAR(150) NOT NULL UNIQUE, 
                email VARCHAR(254) NOT NULL, 
                is_staff BOOLEAN NOT NULL, 
                is_active BOOLEAN NOT NULL, 
                date_joined TIMESTAMP WITH TIME ZONE NOT NULL, 
                first_name VARCHAR(150) NOT NULL, 
                last_name VARCHAR(150) NOT NULL, 
                phone_number VARCHAR(20) NULL, 
                id_number VARCHAR(50) NULL
            )
            ''')
            print("Created authentication_user table.")

            # Create authtoken_token table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS authtoken_token (
                key VARCHAR(40) NOT NULL PRIMARY KEY, 
                created TIMESTAMP WITH TIME ZONE NOT NULL, 
                user_id INTEGER NOT NULL UNIQUE
            )
            ''')
            print("Created authtoken_token table.")

            return True
    except DatabaseError as e:
        print(f"Error creating tables directly: {e}")
        return False

def verify_tables():
    """Verify that essential tables exist"""
    print("Verifying essential tables...")
    try:
        with connection.cursor() as cursor:
            # Check if django_session table exists
            cursor.execute("""
            SELECT EXISTS (
               SELECT FROM information_schema.tables 
               WHERE table_name = 'django_session'
            )
            """)
            session_exists = cursor.fetchone()[0]

            if not session_exists:
                print('django_session table does not exist!')
                return False

            # Check if django_site table exists
            cursor.execute("""
            SELECT EXISTS (
               SELECT FROM information_schema.tables 
               WHERE table_name = 'django_site'
            )
            """)
            site_exists = cursor.fetchone()[0]

            if not site_exists:
                print('django_site table does not exist!')
                return False

            print("All essential tables exist.")
            return True
    except DatabaseError as e:
        print(f"Error verifying tables: {e}")
        return False

def main():
    """Main function to ensure migrations are applied"""
    print("Starting migration process...")

    # First try running migrations normally
    if not run_migrations():
        # If migrations fail, create tables directly
        if not create_tables_directly():
            print("Failed to create tables directly.")
            sys.exit(1)

    # Verify that essential tables exist
    if not verify_tables():
        print("Essential tables are missing even after migration attempts.")
        sys.exit(1)

    print("Migration process completed successfully.")

if __name__ == "__main__":
    main()
