import os
import json
import hashlib
import requests
import re
import time
from markdownify import markdownify as md
from dotenv import load_dotenv
from google import genai

# Load bien moi truong (API Key)
load_dotenv()
client = genai.Client()

API_URL = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json?per_page=50"
MD_DIR = "articles_md"
STATE_FILE = "sync_state.json" # File luu tru lich su hash de check file cu/moi

def get_hash(text):
    """Tao ma bam MD5 de so sanh noi dung."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip('-')

def main():
    print("=== BAT DAU JOB DONG BO DATA ===")
    os.makedirs(MD_DIR, exist_ok=True)
    
    # 1. Doc trang thai dong bo cu
    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)

    # 2. Cao du lieu tu Zendesk
    print("[1] Dang lay du lieu tu Zendesk...")
    resp = requests.get(API_URL)
    if resp.status_code != 200:
        print(f"[LOI] Khong the goi API Zendesk. Ma loi: {resp.status_code}")
        return

    articles = resp.json().get("articles", [])
    
    added_count = 0
    updated_count = 0
    skipped_count = 0
    files_to_upload = []

    print(f"Tim thay {len(articles)} bai viet. Dang kiem tra thay doi (Delta)...")
    
    # 3. Xu ly Delta Update (Chi lay file moi hoac file bi sua)
    for art in articles:
        if not art.get("body"): continue
        
        art_id = str(art['id'])
        title = art.get('title', 'Untitled')
        url = art.get('html_url', '')
        
        content_md = md(art.get('body'), heading_style="ATX")
        final_md = f"# {title}\n\nArticle URL: {url}\n\n{content_md}"
        
        current_hash = get_hash(final_md)
        
        # Neu bai viet khong co gi thay doi so voi lan chay truoc -> Bo qua
        if art_id in state and state[art_id] == current_hash:
            skipped_count += 1
            continue
            
        # Phan loai la Them Moi hay Cap Nhat
        if art_id not in state:
            added_count += 1
        else:
            updated_count += 1
            
        # Luu file ra may
        filename = f"{art_id}-{slugify(title)}.md"
        filepath = os.path.join(MD_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(final_md)
            
        # Dua vao danh sach can upload len AI
        files_to_upload.append({'id': art_id, 'hash': current_hash, 'path': filepath})

    print(f"\n[THONG KE DELTA] Moi: {added_count} | Cap nhat: {updated_count} | Bo qua (Khong doi): {skipped_count}")
    
    # 4. Upload Delta len Google Gemini
    if not files_to_upload:
        print("=> Khong co du lieu moi. Ket thuc Job hom nay!")
        return
        
    print(f"\n[2] Dang upload {len(files_to_upload)} file moi/cap nhat len Gemini...")
    for item in files_to_upload:
        try:
            client.files.upload(file=item['path'], config={'mime_type': 'text/plain'})
            print(f"  [OK] Uploaded: {os.path.basename(item['path'])}")
            
            # Chi ghi nhan hash thanh cong vao state khi da up thanh cong len AI
            state[item['id']] = item['hash']
            time.sleep(2) # Tranh rate limit
        except Exception as e:
            print(f"  [LOI] Khong the up {os.path.basename(item['path'])}: {e}")
            
    # Luu lai trang thai de ngay mai chay tiep
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)
        
    print("\n=== HOAN THANH JOB DONG BO ===")

if __name__ == "__main__":
    main()