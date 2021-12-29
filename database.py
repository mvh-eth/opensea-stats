import pandas as pd
from pymongo import MongoClient
import pymongo
import ssl

database_name = "mvh"


def write_mongo(collection, data, overwrite=False, database_name="mvh"):
    """Wrapper for the mongoDB .insert_many() function to add to the database

    Args:
        collection ([str]): name of the mongoDB collection
        data ([dataframe or list of dict]): [description]
        overwrite (bool, optional): [description]. Defaults to False.
    """
    url = "mongodb+srv://ape-gang:SW68cArWhOdB4Fhx@cluster0.sryj9.mongodb.net/ape_gang?retryWrites=true&w=majority"
    my_client = MongoClient(url, ssl_cert_reqs=ssl.CERT_NONE)
    my_db = my_client[database_name]
    my_collection = my_db[collection]

    #
    if overwrite:
        n_docs = my_collection.count_documents({})
        print(f"deleting {n_docs} from {collection} mongoDB collection.")
        my_collection.delete_many({})  # delete all data

    if isinstance(data, pd.DataFrame):
        # convert dataframe back to list of dictionaries
        data = data.to_dict("records")

    # write data to collection
    if len(data) > 1 and isinstance(data, list):
        try:
            my_collection.insert_many(data, ordered=False)

            print(f"updating {collection} with {len(data)} documents.")

            my_collection.create_index("asset_id")
            return "inserted"

        except pymongo.errors.BulkWriteError as e:
            panic = list(filter(lambda x: x["code"] != 11000, e.details["writeErrors"]))

            if len(panic) > 0:
                raise e

            inserted_no = len(data) - len(e.details["writeErrors"])
            # only return duplicate is no rows inserted
            if inserted_no == 0:
                return "duplicate"

            print(f"updating {collection} with {inserted_no}")

            return "inserted"
        except Exception as e:
            return "duplicate"


def read_mongo(
    collection,
    query_filter={},
    query_projection=[],
    query_sort=[],
    query_limit=None,
    database_name="mvh",
    return_df=False,
):
    url = "mongodb+srv://ape-gang:SW68cArWhOdB4Fhx@cluster0.sryj9.mongodb.net/ape_gang?retryWrites=true&w=majority"
    my_client = MongoClient(url, ssl_cert_reqs=ssl.CERT_NONE)
    my_db = my_client[database_name]
    if collection not in my_db.list_collection_names():
        print(
            f"Collection '{collection}' doesn't exist.\nPlease select one of the following; {my_db.list_collection_names()}"
        )
        return None
    my_collection = my_db[collection]

    # if no projection input, defult to all columns
    if len(query_projection) < 1:
        query_projection = my_collection.find_one().keys()

    # if no limit input, set to all documents
    if query_limit is None:
        query_limit = my_collection.count_documents({})

    # Make a query to the specific DB and Collection
    data = list(
        my_collection.find(
            filter=query_filter,
            projection=query_projection,
            sort=query_sort,
            limit=query_limit,
        )
    )

    if len(data) > 0:
        if return_df:
            data = pd.DataFrame(data)
        return data
    else:  # return None if no data found
        print(f"No data found for {collection} with specific query - {query_filter}")
        return None


def get_latest_DB_update(collection):

    projection = {"time": 1, "_id": 0}
    sorting = [("time", -1)]
    recent_updates = []
    for event in ["sales", "transfers", "listings", "cancellations"]:
        recent_update = read_mongo(
            collection=f"{collection}_{event}",
            query_projection=projection,
            query_sort=sorting,
            query_limit=1,
        )
        if recent_update is not None:
            recent_updates.append(recent_update[0]["time"])

    if len(recent_updates) > 0:
        return min(recent_updates)
    else:
        return None
