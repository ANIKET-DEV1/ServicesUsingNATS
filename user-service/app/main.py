from fastapi import FastAPI
import uvicorn
app = FastAPI()


@app.get("/")
def start():
    return {"message": "User_service On"}


if __name__ == "__main__":
    

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        reload=False
    )