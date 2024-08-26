from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import products

app = FastAPI(title="AlongX.Subscription.Api",description="AlongX.Subscription.Api",version="V0.01")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    products.router,
    prefix="/Products",
    tags=["Products"]
)