-- Update PostgreSQL configuration
ALTER SYSTEM SET listen_addresses = '*';
ALTER SYSTEM SET max_connections = '100';

-- Reload configuration
SELECT pg_reload_conf(); 