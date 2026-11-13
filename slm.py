from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
current_dir = os.path.dirname(os.path.abspath(__file__))

def summarize_local_file(file_path: str, summary_length: int = 100):    
    file_path = os.path.join(current_dir, "outputs", file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        local_file_content = file.read()

    llm = OllamaLLM(model="qwen2.5:1.5b")

    prompt_template = """Bạn là một trợ lý AI chuyên tóm tắt tài liệu. 
    Nhiệm vụ của bạn là đọc nội dung đầu vào, lọc bỏ các thông tin nhiễu, 
    và viết lại thành MỘT ĐOẠN VĂN DUY NHẤT có độ dài xấp xỉ {L} từ tóm tắt cốt lõi của tài liệu.

    Nội dung đầu vào:
    {input_text}

    Đoạn văn tóm tắt ({L} từ):"""

    prompt = PromptTemplate(input_variables=["L", "input_text"], template=prompt_template)
    chain = prompt | llm

    result = chain.invoke({
        "L": summary_length, 
        "input_text": local_file_content
    })

    file_path = os.path.join(current_dir, "output.txt")
    with open(file_path, "w", encoding="utf-8") as output_file:
        w = result.split()
        for i in range(0, len(w), 20):
            output_file.write(" ".join(w[i:i+20]) + "\n")

summarize_local_file("truong-giang.md", summary_length=100)