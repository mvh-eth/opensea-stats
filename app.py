import uvicorn
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from ML.AgeGang_ML import update_ApeGang_pred_price
from ML.all_collection_best_value import calc_best_listing


import time


from api import endpoints, sales
from opensea.cryto_prices import update_eth_usd
from opensea.opensea_collections import all_collection_names
from server_jobs import to_pdf, best_dashboard, send_tweets


app = FastAPI()

app.include_router(sales.router, prefix="/api/sales")
app.include_router(endpoints.router, prefix="/api")


@repeat_every(seconds=60 * 60 * 6)  # repeat every 6 hours
def update_price_pred():
    print(1)


@app.on_event("startup")
@repeat_every(seconds=60 * 15)  # repeat 15 mins
def update_events():
    # make sure eth-usd is up-to-date
    update_eth_usd()

    # start stopwatch
    start = time.time()
    all_collections = all_collection_names()

    for collection in all_collections:
        try:
            calc_best_listing(collection=collection, update_listings=False)
        except Exception as e:
            print(f"error in {collection} {e}")

    # end stopwatch
    end = time.time()

    print(f"Time taken to update all collections: {end - start}")

    best_dashboard.run_best_dashboard_job()

    # to_pdf.get_images()
    # send_tweets.send_all_tweets()


if __name__ == "__main__":
    uvicorn.run(
        app,
        port=6969,
    )
