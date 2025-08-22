import requests, pymongo, os
from dotenv import load_dotenv

requests.adapters.DEFAULT_RETRIES = 5
load_dotenv()
myclient = pymongo.MongoClient(os.getenv("MONGODB_URI"))
APIURL = "https://links.yaria.top/api"
groups = requests.get(f"{APIURL}/getGroups", verify=False).json()["groups"]
res = []
for group in groups:
    group_data = {"name": group["name"], "description": group["descr"], "links": []}
    links = requests.get(
        f"{APIURL}/getLinks/?group={group['id']}", verify=False
    ).json()["links"]
    for link in links:
        if not link.get("color") or len(link.get("color")) not in [4, 7]:
            tc = "#888888"
        elif len(link.get("color")) == 5:
            tc = link.get("color")[:-1]
        elif len(link.get("color")) == 9:
            tc = link.get("color")[:-2]
        else:
            tc = link.get("color")
        group_data["links"].append(
            {
                "name": link["name"],
                "description": link["descr"],
                "url": link["link"],
                "avatar": link["avatar"].replace(
                    "cdn.afdelivr.top", "gcore.jsdelivr.net"
                ),
                "color": tc,
                "id": link["oid"],
            }
        )
    res.append(group_data)

collection = myclient[os.getenv("DB_NAME") or "AriaBlogNext"]["FLinks"]
collection.delete_many({})  # Delete all existing documents
collection.insert_many(res)  # Insert the new documents
