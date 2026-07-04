import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load cấu hình từ file .env
load_dotenv()

# Khởi tạo client theo chuẩn SDK mới nhất
client = genai.Client()

MD_DIR = "articles_md"

def setup_gemini_assistant():
    print("\n[BUOC 2] NAP DU LIEU LEN GOOGLE GEMINI 3.1 FLASH-LITE...")

    file_paths = [os.path.join(MD_DIR, f) for f in os.listdir(MD_DIR) if f.endswith(".md")]
    
    if not file_paths:
        print("[LOI] Khong tim thay file .md nao trong thu muc!")
        return

    print(f"Dang upload {len(file_paths)} files len he thong cua Google...")
    uploaded_files = []
    failed_count = 0
    
    for path in file_paths:
        try:
            uploaded_file = client.files.upload(file=path)
            uploaded_files.append(uploaded_file)
            print(f"   [OK] Da tai len: {os.path.basename(path)}")
            time.sleep(2) 
        except Exception as e:
            print(f"   [LOI] Khong the tai {os.path.basename(path)}: {e}")
            failed_count += 1
            
    print(f"[HOAN THANH] Upload xong! Thanh cong: {len(uploaded_files)} files | That bai: {failed_count} files.")

    print("\n[DANG XU LY] Cau hinh OptiBot Assistant...")
    system_prompt = """You are OptiBot, the customer-support bot for OptiSigns.com.
• Tone: helpful, factual, concise.
• Only answer using the uploaded docs.
• Max 5 bullet points; else link to the doc.
• Cite up to 3 "Article URL:" lines per reply."""

    print("\n[KIEM TRA TU DONG] Cau hoi: 'How do I add a YouTube video?'")
    print("Vui long doi AI doc tai lieu va suy nghi...\n")
    
    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=[*uploaded_files, "How do I add a YouTube video?"],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1 
            )
        )
        
        print("================ CAU TRA LOI CUA OPTIBOT ==================")
        print(response.text)
        print("==========================================================")
        
    except Exception as e:
        print(f"[LOI] Test hoi dap that bai: {e}")

if __name__ == "__main__":
    setup_gemini_assistant()