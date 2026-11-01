# Query Options

## Option A: Fetching the booking by itself

Data we get, is from the `bookings` table alone.

```python
await session.get(Booking, 1)
```

```sql
SELECT *
FROM bookings
WHERE bookings.id = 1;
```

## Option B: Fetching the user and associated bookings (`selectin`)

This is ideal for 1:N association

Two queries will be triggered:
1. To fetch the user from the users table
2. To fetch the bookings associated with that user

```python
await session.get(User, 1, options=[selectinload(User.bookings)])
```

```sql
SELECT *
FROM users
WHERE user.id = 1;
```

```sql
SELECT *
FROM bookings
WHERE booking.id IN (1); -- booking.id is taken from the result set of first query
```

## Option C: Fetching the booking and associated room (`join`)

This is ideal for 1:1 association.

```python
await session.get(Booking, 1, options=[joinedload(Booking.room)])
```

```sql
SELECT
    bookings.id,
    bookings.user_id,
    bookings.room_id,
    bookings.check_in,
    bookings.check_out,
    rooms.name,
    rooms.price_per_night,
    rooms.bedrooms,
    rooms.bathrooms
FROM bookings
LEFT JOIN rooms ON bookings.room_id = room.id
WHERE bookings.id = 1;
```