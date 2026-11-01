from rent_a_room.models.booking import BookingPublic
from rent_a_room.models.room import RoomPublic
from rent_a_room.models.user import UserPublic


class BookingWithDetails(BookingPublic):
    user: UserPublic
    room: RoomPublic | None


class RoomWithBookingCount(RoomPublic):
    booking_count: int
