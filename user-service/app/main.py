from fastapi import FastAPI
import uvicorn
app = FastAPI()


@app.get("/")
def start():
    return {"message": "User_service On"}

@app.post("/register")
async def register():
    pass

@app.post("/login")
async def login():
    pass

@app.post("/logout")
async def logout():
    pass

@app.post("/verify-email")
async def verify():
    pass

if __name__ == "__main__":
    

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        reload=False
    )