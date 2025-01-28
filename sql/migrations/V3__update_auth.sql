-- Update authentication configuration
ALTER SYSTEM SET password_encryption = 'md5';

-- Reload configuration
SELECT pg_reload_conf(); 