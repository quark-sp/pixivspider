import requests
from datetime import datetime
import time
import os
import json
from utils import create_dir


class Downloader:
    def __init__(self, session,config_path="config.json"):
        self.session = session
        self.img_dir, self.json_dir = create_dir()
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def fetch_ranking_data(self,page=0):

        headers = self.config["headers"]
        mode = self.config["ranking"]["mode"]
        content = self.config["ranking"]["content"]
        if page == 0:
            page = self.config["ranking"]["pages"]

        url = 'https://www.pixiv.net/ranking.php'
        params = {
            'mode': mode,
            'content': content,
            'p': page,
            'format': 'json'
        }
        
        illusts = []

        for each in range(1, page + 1):

            response = self.session.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                illusts.append(data.get('contents', []))
            else:
                print(f"failed to fetch page {each},status code: {response.status_code}")
            time.sleep(1)    
        return illusts

    def download_image(self,page=0):

        headers = self.config["headers"].copy()
        illusts = self.fetch_ranking_data(page)

        for illust in illusts:

            for item in illust:
                illust_id = item.get('illust_id')
                print(f"processing ID: {illust_id}")

                illust_url = f"https://www.pixiv.net/ajax/illust/{illust_id}"
                response = self.session.get(illust_url, headers=headers)
                if response.status_code != 200:
                    print(f"Failed to get detail for {illust_id}")
                    continue
                body=response.json().get('body')
                author_id = body.get('userId')
                author_name = body.get('userName')
                title = body.get('title')
                upload_date = body.get('uploadDate')
                tags = [tag['tag'] for tag in body.get('tags', {}).get('tags', [])]
                original_url = body.get('urls', {}).get('original')
 
                # 保存元数据 JSON
                meta = {
                    'id': illust_id,
                    'title': title,
                    'author_id': author_id,
                    'author_name': author_name,
                    'tags': tags,
                    'original_url': original_url,
                    'upload_date': upload_date
                }
                with open(os.path.join(self.json_dir, f"{illust_id}.json"), 'w', encoding='utf-8') as f:
                    json.dump(meta, f, ensure_ascii=False, indent=2)
                print(f"Saved metadata for {illust_id}")

                # 保存图片
                if original_url:
                    ext_name = os.path.splitext(original_url)[-1]
                    try:
                        response = self.session.get(original_url, headers=headers)
                        if response.status_code == 200:
                            with open(os.path.join(self.img_dir, f"{illust_id}{ext_name}"), 'wb') as f:
                                f.write(response.content)
                        else:
                            print(f"Failed to download image: {original_url}")
                    except Exception as e:
                        print(f"Error downloading {original_url}: {e}")
                time.sleep(1)
           