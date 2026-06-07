import os
import sys
import time
sys.path.insert(0, 'C:\\AI Study Assistant\\backend')
from utils.llm import GeminiLLM

def extract():
    client = GeminiLLM._get_client()
    # Create a dummy PDF (or just a text file, Gemini accepts text files too)
    with open('dummy.pdf', 'wb') as f:
        # just write some basic PDF bytes
        f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 21 >>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000219 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n289\n%%EOF\n")
    
    print("Uploading file...")
    gemini_file = client.files.upload(file='dummy.pdf')
    print("File uploaded:", gemini_file.name)
    
    while True:
        file_info = client.files.get(name=gemini_file.name)
        state = getattr(file_info, 'state', None)
        print("State:", state)
        if str(state) == 'ACTIVE' or str(state) == 'State.ACTIVE':
            break
        elif str(state) == 'FAILED' or str(state) == 'State.FAILED':
            print("Failed")
            break
        time.sleep(2)
        
    print("Generating...")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[gemini_file, "Extract all text"]
    )
    print("Response:", response.text)
    client.files.delete(name=gemini_file.name)

extract()
