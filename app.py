import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


DICTIONARY = {
    "good afternoon": "buenas tardes",
    "good evening": "buenas noches",
    "good night": "buenas noches",
    "how are you": "cómo estás",
    "how are you doing": "cómo te va",
    "what is your name": "cómo te llamas",
    "my name is": "me llamo",
    "nice to meet you": "encantado de conocerte",
    "see you later": "hasta luego",
    "you are welcome": "de nada",
    "i love you": "te quiero",
    "i am sorry": "lo siento",
    "excuse me": "disculpe",
    "good morning": "buenos días",
    "thank you very much": "muchas gracias",
    "where is": "dónde está",
    "how much": "cuánto",
    "a little": "un poco",
    "i don't know": "no lo sé",
    "i understand": "entiendo",
    "goodbye": "adiós",
    "hello": "hola",
    "hi": "hola",
    "please": "por favor",
    "thank you": "gracias",
    "thanks": "gracias",
    "yes": "sí",
    "no": "no",
    "water": "agua",
    "food": "comida",
    "friend": "amigo",
    "family": "familia",
    "house": "casa",
    "school": "escuela",
    "book": "libro",
    "beautiful": "hermoso",
    "happy": "feliz",
    "good": "bueno",
    "bad": "malo",
    "today": "hoy",
    "tomorrow": "mañana",
    "here": "aquí",
    "there": "allí",
    "love": "amor",
    "and": "y",
    "the": "el",
    "a": "un",
    "is": "es",
    "you": "tú",
    "i": "yo",
}

PHRASES = sorted(DICTIONARY, key=len, reverse=True)
TRANSLATION_PATTERN = re.compile(
    r"(?<!\w)("
    + "|".join(
        r"\s+".join(re.escape(word) for word in phrase.split())
        for phrase in PHRASES
    )
    + r")(?!\w)",
    re.IGNORECASE,
)


def translate_text(text):
    """Translate dictionary matches while leaving unknown words unchanged."""

    def replace_match(match):
        source = match.group(0)
        translated = DICTIONARY[" ".join(source.lower().split())]
        if source.isupper():
            return translated.upper()
        if source[:1].isupper():
            return translated[:1].upper() + translated[1:]
        return translated

    return TRANSLATION_PATTERN.sub(replace_match, text)


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#f3f6f5">
  <title>Lingo — English to Spanish</title>
  <style>
    :root { color-scheme: light; --ink:#173b3a; --muted:#718280; --green:#167d70; --dark:#11665c; --mint:#e2f2ee; --line:#e5ece9; }
    * { box-sizing:border-box; }
    body { margin:0; min-height:100vh; background:#f3f6f5; color:var(--ink); font:15px/1.5 "Segoe UI",system-ui,sans-serif; }
    .shell { max-width:1020px; margin:auto; padding:26px 30px 22px; }
    header { display:flex; align-items:center; justify-content:space-between; color:var(--muted); font-size:13px; }
    .brand { display:flex; align-items:center; gap:10px; color:var(--ink); font-weight:750; letter-spacing:.12em; }
    .spark { color:var(--green); font-size:24px; }
    main { padding-top:58px; }
    h1 { margin:0; font-size:clamp(34px,6vw,48px); line-height:1.15; letter-spacing:-.04em; }
    .intro { margin:10px 0 25px; color:var(--muted); }
    .workspace { display:grid; grid-template-columns:1fr 1fr; overflow:hidden; background:white; border:1px solid var(--line); border-radius:14px; box-shadow:0 12px 40px #173b3a0b; }
    .panel { min-width:0; padding:20px 22px 10px; }
    .panel + .panel { border-left:1px solid var(--line); background:#fbfcfc; }
    .label-row { display:flex; justify-content:space-between; align-items:center; }
    .language { color:var(--green); font-size:12px; font-weight:750; letter-spacing:.08em; }
    .dot { color:var(--green); font-size:11px; }
    .hint { margin-top:4px; color:var(--muted); font-size:12px; }
    textarea, .result { width:100%; min-height:235px; margin-top:14px; padding:4px 0; resize:vertical; border:0; outline:0; background:transparent; color:var(--ink); font:16px/1.7 inherit; }
    textarea::placeholder { color:#9aa8a6; }
    .result { overflow-wrap:anywhere; white-space:pre-wrap; }
    .toolbar { grid-column:1/-1; display:flex; align-items:center; justify-content:space-between; gap:12px; padding:13px 20px; border-top:1px solid var(--line); }
    .count,.status { color:var(--muted); font-size:12px; }
    button { border:0; border-radius:8px; cursor:pointer; font:600 13px "Segoe UI",system-ui,sans-serif; transition:background .15s,transform .15s; }
    button:active { transform:translateY(1px); }
    .translate { padding:11px 18px; background:var(--green); color:white; }
    .translate:hover { background:var(--dark); }
    .examples,.actions { display:flex; align-items:center; gap:9px; margin-top:17px; }
    .try { margin-right:2px; color:var(--muted); font-size:11px; font-weight:750; letter-spacing:.06em; }
    .chip { padding:7px 11px; background:var(--mint); color:var(--dark); font-size:12px; }
    .chip:hover { background:#d2eae4; }
    .actions { justify-content:flex-end; margin-top:12px; }
    .actions .status { margin-right:auto; }
    .text-button { padding:6px 0; background:transparent; color:var(--muted); }
    .text-button:hover { color:var(--dark); }
    footer { padding-top:46px; color:var(--muted); text-align:center; font-size:12px; }
    @media (max-width:640px) {
      .shell { padding:19px 17px; } header .tagline { display:none; } main { padding-top:40px; }
      .workspace { grid-template-columns:1fr; } .panel + .panel { border-left:0; border-top:1px solid var(--line); }
      textarea,.result { min-height:130px; } .toolbar { grid-column:1; }
      .examples { flex-wrap:wrap; } footer { padding-top:32px; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <div class="brand"><span class="spark">✦</span> LINGO</div>
      <span class="tagline">A little language goes a long way.</span>
    </header>
    <main>
      <h1>Say it in Spanish.</h1>
      <p class="intro">A simple English-to-Spanish translator, right at your fingertips.</p>
      <section class="workspace" aria-label="Translator">
        <div class="panel">
          <div class="label-row"><span class="language">ENGLISH</span><span class="dot">●</span></div>
          <div class="hint">Type or paste your text</div>
          <textarea id="source" placeholder="Write something in English..." aria-label="English text"></textarea>
        </div>
        <div class="panel">
          <div class="label-row"><span class="language">SPANISH</span><span class="dot">●</span></div>
          <div class="hint">Your translation appears here</div>
          <div class="result" id="result" aria-live="polite"></div>
        </div>
        <div class="toolbar">
          <span class="count" id="count">0 characters</span>
          <button class="translate" id="translate">Translate &nbsp;→</button>
        </div>
      </section>
      <div class="examples">
        <span class="try">TRY:</span>
        <button class="chip" data-example="Hello!">Hello!</button>
        <button class="chip" data-example="Thank you">Thank you</button>
        <button class="chip" data-example="How are you?">How are you?</button>
      </div>
      <div class="actions">
        <span class="status" id="status"></span>
        <button class="text-button" id="clear">Clear</button>
        <button class="text-button" id="copy">Copy translation</button>
      </div>
    </main>
    <footer>Built with a little dictionary and a lot of cariño.</footer>
  </div>
  <script>
    const source = document.querySelector("#source");
    const result = document.querySelector("#result");
    const status = document.querySelector("#status");
    const count = document.querySelector("#count");
    function updateCount() {
      const length = source.value.length;
      count.textContent = `${length} character${length === 1 ? "" : "s"}`;
    }
    async function translate() {
      const text = source.value.trim();
      if (!text) {
        status.textContent = "Type something to translate.";
        source.focus();
        return;
      }
      status.textContent = "";
      try {
        const response = await fetch("/translate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text })
        });
        if (!response.ok) throw new Error("Translation request failed.");
        const data = await response.json();
        result.textContent = data.translation;
        status.textContent = "Done — unknown words are kept as written.";
      } catch (error) {
        status.textContent = "Could not translate. Please try again.";
      }
    }
    document.querySelector("#translate").addEventListener("click", translate);
    source.addEventListener("input", updateCount);
    source.addEventListener("keydown", event => {
      if ((event.ctrlKey || event.metaKey) && event.key === "Enter") translate();
    });
    document.querySelectorAll("[data-example]").forEach(button => {
      button.addEventListener("click", () => {
        source.value = button.dataset.example;
        updateCount();
        translate();
      });
    });
    document.querySelector("#clear").addEventListener("click", () => {
      source.value = "";
      result.textContent = "";
      status.textContent = "";
      updateCount();
      source.focus();
    });
    document.querySelector("#copy").addEventListener("click", async () => {
      if (!result.textContent) {
        status.textContent = "Translate some text first.";
        return;
      }
      try {
        await navigator.clipboard.writeText(result.textContent);
        status.textContent = "Translation copied to clipboard.";
      } catch (error) {
        status.textContent = "Clipboard access is unavailable in this browser.";
      }
    });
  </script>
</body>
</html>
"""


class TranslatorHandler(BaseHTTPRequestHandler):
    def _send(self, status_code, content_type, body):
        encoded = body.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        if self.path != "/":
            self._send(404, "text/plain; charset=utf-8", "Not found")
            return
        self._send(200, "text/html; charset=utf-8", PAGE)

    def do_POST(self):
        if self.path != "/translate":
            self._send(404, "application/json; charset=utf-8", '{"error":"Not found"}')
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 100_000:
                raise ValueError("Request body must be between 1 and 100000 bytes.")
            payload = json.loads(self.rfile.read(length))
            text = payload.get("text") if isinstance(payload, dict) else None
            if not isinstance(text, str):
                raise ValueError("The text field must be a string.")
        except (ValueError, json.JSONDecodeError) as error:
            response = json.dumps({"error": str(error)})
            self._send(400, "application/json; charset=utf-8", response)
            return

        response = json.dumps(
            {"translation": translate_text(text)},
            ensure_ascii=False,
        )
        self._send(200, "application/json; charset=utf-8", response)

    def log_message(self, format_string, *args):
        print(f"{self.address_string()} - {format_string % args}")


def main():
    address = ("127.0.0.1", 8000)
    server = ThreadingHTTPServer(address, TranslatorHandler)
    print(f"Lingo is running at http://{address[0]}:{address[1]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Lingo.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
