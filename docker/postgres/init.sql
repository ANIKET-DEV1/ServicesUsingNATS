
SELECT 'CREATE DATABASE user_service'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'user_service')\gexec

