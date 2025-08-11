import json
import pymongo
import os,re,time
import pymongo
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
myclient = pymongo.MongoClient(os.getenv("MONGODB_URI"))[os.getenv("DB_NAME") or "AriaBlogNext"]["Speaks"]
myclient.delete_many({})
def iso_to_unix(iso_string):
    dt = datetime.strptime(iso_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    unix_timestamp = int(time.mktime(dt.timetuple()))
    return unix_timestamp
def replace_and_remove_tags(text):
    # Replace <a> tags with [链接]
    text = re.sub(r'<a\s+[^>]*>.*?<\/a>', '[链接]', text)   

    # Replace <img> tags with [图片]
    text = re.sub(r'<img\s+[^>]*>', '[图片]', text)     

    # Replace URLs starting with http or https and ending with common image extensions with [图片]
    text = re.sub(r'https?:\/\/\S+\.(?:png|jpg|jpeg|gif|webp|avif)', '[图片]', text)
    
    # Replace remaining URLs starting with http or https with [链接]
    text = re.sub(r'https?:\/\/\S+', '[链接]', text)

    text=re.sub('<.*?>', '', text)

    return text
def replace_links_and_images(text):
    # 步骤 1: 临时替换 <img> 标签中的链接，以避免被错误替换
    img_placeholder_pattern = re.compile(r'<img\s+src="([^"]+)"[^>]*>')
    placeholders = {}

    def replace_img_tag(match):
        index = len(placeholders)
        placeholders[f'__IMG_TAG__{index}__'] = match.group(1)
        return f'__IMG_TAG__{index}__'

    # 替换 <img> 标签中的链接为占位符
    text = img_placeholder_pattern.sub(replace_img_tag, text)

    # 步骤 2: 将其他 http 和 https 链接替换为 <a> 标签，内容为“链接”
    # 排除以图片后缀结尾的链接
    def replace_link(match):
        url = match.group(0)
        # 检查链接是否以图片格式结尾
        if re.search(r'\.(png|jpg|jpeg|gif|webp|avif)$', url):
            return url  # 保留图片链接
        return f'<a href="{url}">链接</a>'

    # 替换链接
    text = re.sub(r'https?:\/\/[^\s<]+', replace_link, text)

    text = re.sub(r'https?:\/\/[^\s<]+?\.(?:png|jpg|jpeg|gif|webp|avif)', r'<img src="\g<0>"/>', text)

    return text
 
with open("importer/bb.json",encoding="utf-8") as f:
    data = json.load(f)
    for item in data:
        myclient.insert_one(
            {
                "content": replace_links_and_images(item["content"]),
                "plainContent": replace_and_remove_tags(item["content"]).replace("\n"," "),
                "time": iso_to_unix(item["createdAt"]),
            }
        )