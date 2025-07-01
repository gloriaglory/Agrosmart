from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Creates the necessary tables for the education app'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check if the tables already exist
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'education_content'
                );
            """)
            content_table_exists = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'education_comment'
                );
            """)
            comment_table_exists = cursor.fetchone()[0]
            
            # Create the tables if they don't exist
            if not content_table_exists:
                self.stdout.write('Creating education_content table...')
                cursor.execute("""
                    CREATE TABLE education_content (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        type VARCHAR(10) NOT NULL,
                        url_or_text TEXT NOT NULL,
                        thumbnail VARCHAR(100) NULL,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                    );
                """)
                self.stdout.write(self.style.SUCCESS('Successfully created education_content table'))
            else:
                self.stdout.write('education_content table already exists')
            
            if not comment_table_exists:
                self.stdout.write('Creating education_comment table...')
                cursor.execute("""
                    CREATE TABLE education_comment (
                        id SERIAL PRIMARY KEY,
                        text TEXT NOT NULL,
                        parent_id INTEGER NULL REFERENCES education_comment(id) ON DELETE CASCADE,
                        content_id INTEGER NOT NULL REFERENCES education_content(id) ON DELETE CASCADE,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                    );
                """)
                self.stdout.write(self.style.SUCCESS('Successfully created education_comment table'))
            else:
                self.stdout.write('education_comment table already exists')