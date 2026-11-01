# Delete Options
 
Foreign key constraint prohibits deletion of a row that is referenced by another row.

## Option A: Cascade Delete

Permanently deletes all linked records

## Option B: Soft Delete

Add a status column and whenever deleting, change status to archived

Fetching available records excludes archived records.

## Option C: Set NULL on Delete


