from fastapi import FastAPI, status

app = FastAPI(
    title="Rent a Room API",
    description="Book a stay in a house or room",
    version="1.0.0",
)


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Welcome to rent a room"}
