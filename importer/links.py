import requests, pymongo, os
from dotenv import load_dotenv

load_dotenv()
myclient = pymongo.MongoClient(os.getenv("MONGODB_URI"))
APIURL = "https://links.yaria.top/api"
groups = requests.get(f"{APIURL}/getGroups").json()["groups"]
res = []
for group in groups:
    group_data = {
        "name": group["name"],
        "description": group["descr"],
        "links": []
    }
    links = requests.get(f"{APIURL}/getLinks/?group={group['id']}").json()["links"]
    for link in links:
        if not link.get("color") or len(link.get("color")) not in [4, 7]:
            tc = "#888888bb"
        elif len(link.get("color")) == 4:
            tc = f"#{''.join([ch*2 for ch in link.get('color')[1:]])}bb"
        elif len(link.get("color")) == 7:
            tc = link.get("color") + "bb"
        group_data["links"].append({
            "name": link["name"],
            "description": link["descr"],
            "url": link["link"],
            "avatar": link["avatar"].replace("cdn.afdelivr.top", "gcore.jsdelivr.net"),
            "color": tc
        })
    res.append(group_data)

collection = myclient["AriaBlogNext"]["FLinks"]
collection.delete_many({})  # Delete all existing documents
collection.insert_many(res)  # Insert the new documents
