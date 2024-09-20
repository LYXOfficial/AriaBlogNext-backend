import yaml,sys,io
import os,re
import pymongo
from dotenv import load_dotenv
load_dotenv()
myclient = pymongo.MongoClient(os.getenv("MONGODB_URI"))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030') 
res=[]
def clean_markdown(text):
    # 移除Markdown语法中的符号
    cleaned_text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)  # 粗体 **text** 或 __text__
    cleaned_text = re.sub(r'(\*|_)(.*?)\1', r'\2', cleaned_text)  # 斜体 *text* 或 _text_
    cleaned_text = re.sub(r'(~~)(.*?)\1', r'\2', cleaned_text)  # 删除线 ~~text~~
    cleaned_text = re.sub(r'`{1,2}(.*?)`{1,2}', r'\1', cleaned_text)  # 行内代码 `code`
    cleaned_text = re.sub(r'```[\s\S]*?```', '', cleaned_text)  # 代码块 ```code```
    cleaned_text = re.sub(r'!\[.*?\]\(.*?\)', '', cleaned_text)  # 图片 ![alt](url)
    cleaned_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', cleaned_text)  # 链接 [text](url)
    cleaned_text = re.sub(r'^\s{0,3}>\s?', '', cleaned_text, flags=re.M)  # 引用 >
    cleaned_text = re.sub(r'^\s{0,3}[-*+]\s', '', cleaned_text, flags=re.M)  # 无序列表 - * +
    cleaned_text = re.sub(r'^\s{0,3}\d+\.\s', '', cleaned_text, flags=re.M)  # 有序列表 1. 2. 3.
    cleaned_text = re.sub(r'^#{1,6}\s?', '', cleaned_text, flags=re.M)  # 标题 # ## ### 等
    cleaned_text = re.sub(r'^\s*\|.*?\|\s*$', '', cleaned_text, flags=re.M)  # 表格 | col1 | col2 |
    cleaned_text = re.sub(r'^-{3,}$', '', cleaned_text, flags=re.M)  # 分隔线 ---
    cleaned_text = re.sub(r'\n{2,}', '\n', cleaned_text)  # 多余的换行

    # 去除文本开头和结尾的多余换行
    return cleaned_text.strip()

for i in os.listdir("importer/posts"):
    with open("importer/posts/"+i,"r",encoding="utf-8") as f:
        textContent=f.read()
        data=yaml.safe_load(textContent.split("---")[1])
        print(data["title"])
        plainContent=("---".join(textContent.split("---")[2:])).strip()
        plainContent=clean_markdown(plainContent).replace("\n"," ")
        wordCount=len(re.findall(r'\b\w+\b',"---".join(textContent.split("---")[2:]))+re.findall(r'[\u4e00-\u9fff]',"---".join(textContent.split("---")[2:])))
        plainContent=plainContent[:201]
        res.append({
            "title": data.get("title"),
            "description": data.get("description"),
            "mdContent": "---".join(textContent.split("---")[2:]),
            "tags": data.get("tags",[]) if type(data.get("tags",[]))==list else [data.get("tags")],
            "category": data.get("categories",[""])[0] if type(data.get("categories",[""]))==list else data.get("categories"),
            "publishTime": data.get("date").timestamp(),
            "lastUpdatedTime": data.get("updated").timestamp(),
            "slug": data.get("abbrlink"),
            "bannerImg": data.get("cover"),
            "plainContent": plainContent,
            "wordCount": wordCount,
            "coverFit": data.get("cover-fit"),
        })
myclient["AriaBlogNext"]["Posts"].delete_many({})
myclient["AriaBlogNext"]["Posts"].insert_many(res)