import uvicorn
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from ML.AgeGang_ML import update_ApeGang_pred_price
from ML.all_collection_best_value import calc_best_listing


from api import endpoints, sales
from opensea.opensea_collections import (
    all_collection_names,
)

app = FastAPI()

app.include_router(sales.router, prefix="/api/sales")
app.include_router(endpoints.router, prefix="/api")


@app.on_event("startup")
@repeat_every(seconds=60 * 60 * 6)  # repeat every 6 hours
def update_price_pred():
    print("updating ApeGang Predicted price")
    update_ApeGang_pred_price()


@app.on_event("startup")
@repeat_every(seconds=60 * 10)  # repeat 10 mins
def update_events():
    all_collections = all_collection_names()

    for collection in all_collections:
        calc_best_listing(collection=collection, update_listings=True)


if __name__ == "__main__":
    uvicorn.run(
        app,
    )
