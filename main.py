from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import products,plans,subscribers,subscriptions,subcrption_history

app = FastAPI(title="AlongX.Subscription.Api",description="AlongX.Subscription.Api",version="V0.01")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(
    plans.router,
    prefix="/Plans",
    tags=["Plans"]
)
app.include_router(
    products.router,
    prefix="/Products",                                            
    tags=["Products"]
)
app.include_router(
    subcrption_history.router,
    prefix="/SubcrptionHistory",                                             
    tags=["SubcrptionHistory"]
)
app.include_router(
    subscribers.router,
    prefix="/Subscribers",
    tags=["Subscribers"]
)
app.include_router(
    subscriptions.router,
    prefix="/Subscriptions",
    tags=["Subscriptions"]
)