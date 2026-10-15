import json
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


PROJECT_DIRECTORY = Path(__file__).resolve().parent
MAX_MESSAGE_LENGTH = 300


def get_reply(message):
    question = message.casefold()

    if re.search(r"\b(learn|learning|topic|topics|study)\b", question):
        return (
            "The project notes cover Python classes and objects, inheritance, "
            "constructors, and method overriding. Choose a topic in the "
            "What we're learning section to explore more."
        )

    if re.search(r"\b(inherit|inheritance|parent|child|super)\b", question):
        return (
            "Inheritance lets one class reuse or extend another class's behavior. "
            "The notes include single, multiple, multilevel, and hierarchical "
            "inheritance examples."
        )

    if re.search(r"\b(class|classes|object|objects|constructor|method|python)\b|__init__", question):
        return (
            "A class defines behavior and data; an object is an instance of that "
            "class. In Python, __init__ is commonly used to initialize a new object."
        )

    if re.search(r"\b(project|about|who are you)\b|my ai", question):
        return (
            "My AI Project is a growing space for learning programming, keeping "
            "useful notes, and understanding concepts through practical examples."
        )

    if re.search(r"\b(hello|hi|hey)\b", question):
        return (
            "Hi! I can tell you about the project, Python classes, or inheritance. "
            "What would you like to know?"
        )

    return (
        "I'm a scripted demo, so I can answer questions about this project and its "
        "Python learning topics. Try asking about classes or inheritance."
    )


class ProjectRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_DIRECTORY), **kwargs)

    def send_json(self, status, payload, headers=None):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self.path = "/about.html"

        if self.path == "/api/chat":
            self.send_json(
                405,
                {"error": "Use POST to send a chat message."},
                {"Allow": "POST"},
            )
            return

        super().do_GET()

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_json(404, {"error": "Not found."})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_json(400, {"error": "Invalid request length."})
            return

        if content_length <= 0 or content_length > 4096:
            self.send_json(413, {"error": "Request must contain a message under 300 characters."})
            return

        try:
            payload = json.loads(self.rfile.read(content_length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(400, {"error": "Request body must be valid JSON."})
            return

        if not isinstance(payload, dict) or not isinstance(payload.get("message"), str):
            self.send_json(400, {"error": "Provide a message as text."})
            return

        message = payload["message"].strip()
        if not message or len(message) > MAX_MESSAGE_LENGTH:
            self.send_json(400, {"error": "Message must contain 1 to 300 characters."})
            return

        self.send_json(200, {"reply": get_reply(message)})


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), ProjectRequestHandler)
    print("My AI Project is running at http://127.0.0.1:8000")
    print("Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping My AI Project server.")
    finally:
        server.server_close()
