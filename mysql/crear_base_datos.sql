-- Crea la base de datos y el usuario de MySQL para TechStore INACAP.
-- Ejecutar una sola vez como root:
--   mysql -u root -p -e "source mysql/crear_base_datos.sql"

CREATE DATABASE IF NOT EXISTS techstore_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'techstore_user'@'localhost' IDENTIFIED BY 'Techstore_2026';

GRANT ALL PRIVILEGES ON techstore_db.* TO 'techstore_user'@'localhost';

-- Base de datos temporal que crea "python manage.py test"
GRANT ALL PRIVILEGES ON test_techstore_db.* TO 'techstore_user'@'localhost';

FLUSH PRIVILEGES;
