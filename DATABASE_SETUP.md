# SQL Server Database Setup Script

## Database Creation
Create a new database in SQL Server:

```sql
CREATE DATABASE CarPortalDB;
GO

USE CarPortalDB;
GO
```

## User Creation (Optional - for security)
Create a dedicated database user:

```sql
CREATE LOGIN CarPortalUser WITH PASSWORD = 'StrongPassword123!';
GO

CREATE USER CarPortalUser FOR LOGIN CarPortalUser;
GO

ALTER ROLE db_owner ADD MEMBER CarPortalUser;
GO
```

## Connection String
Update the connection string in `.env`:

```
mssql+pyodbc://CarPortalUser:StrongPassword123!@localhost/CarPortalDB?driver=ODBC+Driver+17+for+SQL+Server
```

Or for Windows Authentication:
```
mssql+pyodbc:///?odbc_connect=DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=CarPortalDB;Trusted_Connection=yes
```

## Tables will be automatically created by SQLAlchemy when the Flask app runs for the first time.

## Data Backup
To backup the database:

```sql
BACKUP DATABASE CarPortalDB 
TO DISK = 'C:\Backups\CarPortalDB.bak';
GO
```

## Data Restore
To restore the database:

```sql
RESTORE DATABASE CarPortalDB 
FROM DISK = 'C:\Backups\CarPortalDB.bak';
GO
```

## SQL Server Express Download
- Download from: https://www.microsoft.com/en-us/sql-server/sql-server-editions-express
- ODBC Driver: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
