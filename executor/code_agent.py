import os
import subprocess
import socket
import requests
import config.settings as cfg
import webbrowser
WORKSPACE = r"D:/MajorProject/Testing"
os.makedirs(WORKSPACE, exist_ok=True)


def internet_available():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False


def open_vscode():
    subprocess.Popen(["code", WORKSPACE], shell=True)
    return "VS Code opened in workspace."

def close_vscode():
    subprocess.run(
        ["taskkill", "/IM", "Code.exe", "/F"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return "VS Code closed."

# for files creation
def create_file(slots):
    filename = slots.get("filename")
    language = slots.get("language", "text").lower()

    if not filename:
        return "File name not provided."

    ext_map = {
        "python": ".py",
        "java": ".java",
        "html": ".html",
        "css": ".css",
        "javascript": ".js",
        "text": ".txt",
        "c": ".c",
        "cpp": ".cpp"
    }

    ext = ext_map.get(language, ".txt")
    path = os.path.join(WORKSPACE, filename + ext)

    if os.path.exists(path):
        return f"File {filename}{ext} already exists."

    with open(path, "w", encoding="utf-8") as f:
        f.write("")

# code geeration
def write_code(slots):
    filename = slots.get("filename")
    instruction = slots.get("instruction")
    language = slots.get("language", "python").lower()

    if not filename or not instruction:
        return "Missing filename or instruction."

    ext_map = {
        "python": ".py",
        "html": ".html",
        "css": ".css",
        "javascript": ".js"
    }

    ext = ext_map.get(language, ".txt")
    path = os.path.join(WORKSPACE, filename + ext)

    if not os.path.exists(path):
        return "File does not exist."

    code = generate_code_with_llm(instruction, language)

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return f"Code written to {filename}{ext}"

def generate_code_with_llm(instruction, language):
    prompt = (
        f"You are a professional software developer.\n"
        f"Write clean and correct {language} code for:\n"
        f"{instruction}\n"
        f"Return ONLY code."
    )

    # code generation using groq
    if internet_available():
        try:
            headers = {
                "Authorization": f"Bearer {cfg.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": cfg.GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }

            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )

            return r.json()["choices"][0]["message"]["content"]

        except Exception as e:
            print("Groq failed, switching to local LLM:", e)

    # try with local ollama
    try:
        result = subprocess.run(
            ["ollama", "run", cfg.OLLAMA_MODEL],
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return result.stdout.decode()

    except Exception as e:
        return f"# Code generation failed: {e}"

# code execution
def run_code(slots):
    filename = slots.get("filename")
    language = slots.get("language", "").lower()

    if not filename:
        return "⚠️ Filename missing."

    # ---------- PYTHON ----------
    if language == "python":
        path = os.path.join(WORKSPACE, filename + ".py")

        if not os.path.exists(path):
            return "❌ Python file not found."

        try:
            result = subprocess.run(
                ["python", path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )

            if result.stderr:
                return f"❌ Error:\n{result.stderr.strip()}"

            if result.stdout.strip():
                return f"🖥️ Output:\n{result.stdout.strip()}"

            return "✅ Python file executed successfully (no output)."

        except subprocess.TimeoutExpired:
            return "⚠️ Execution timed out."

    # ---------- HTML / CSS / JS ----------
    elif language in ("html", "css", "javascript", "js"):
        ext_map = {
            "html": ".html",
            "css": ".css",
            "javascript": ".js",
            "js": ".js"
        }

        path = os.path.join(WORKSPACE, filename + ext_map[language])

        if not os.path.exists(path):
            return "❌ File not found."

        webbrowser.open(f"file:///{path}")
        return f"🌐 Opened {filename}{ext_map[language]} in browser."

    # ---------- UNSUPPORTED ----------
    return "⚠️ Run not supported for this file type."


