import io
import json
import time
import threading
import logging
import socketserver
from http import server
from threading import Condition

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

from robot.state import sensor_data


# ===========================
#  HTML 
# ===========================
PAGE = """\
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>KPZ Robot Panel</title>
  <style>
    body { font-family: sans-serif; background: #111; color: #eee; text-align: center; }
    h1 { margin-top: 16px; }

    .wrap { display:flex; gap:20px; justify-content:center; align-items:flex-start; flex-wrap:wrap; margin: 16px; }
    .card { background:#1b1b1b; padding:16px; border-radius:12px; box-shadow: 0 6px 20px rgba(0,0,0,.35); }

    img { width:640px; max-width:95vw; border-radius:12px; border:2px solid #333; }
    .muted { color:#aaa; font-size: 12px; margin-top: 8px; }

    .grid { display:grid; grid-template-columns: 1fr; gap: 12px; min-width: 320px; }
    .section { background:#141414; border:1px solid #2a2a2a; border-radius:12px; padding:12px; text-align:left; }
    .section h3 { margin: 0 0 10px 0; font-size: 14px; color:#ddd; }

    .row { display:flex; justify-content:space-between; align-items:baseline; padding: 6px 0; border-bottom: 1px solid #222; }
    .row:last-child { border-bottom: none; }

    .label { color:#bbb; font-size: 13px; }
    .value { font-size: 20px; font-weight: 700; }
    .unit { font-size: 12px; color:#aaa; margin-left: 6px; font-weight: 500; }
  </style>
</head>
<body>
  <h1>KPZ Robot Panel</h1>

  <div class="wrap">
    <div class="card">
      <h2>Kamera</h2>
      <img src="/stream.mjpg" />
      <div class="muted">MJPEG stream</div>
    </div>

    <div class="card">
      <h2>Czujniki</h2>

      <div class="grid">
        <div class="section">
          <h3>Informacje ogólne</h3>
          <div class="row">
            <div class="label">Temperatura</div>
            <div><span class="value" id="temp">--</span><span class="unit">°C</span></div>
          </div>
          <div class="row">
            <div class="label">Wilgotność</div>
            <div><span class="value" id="hum">--</span><span class="unit">%</span></div>
          </div>
          <div class="row">
            <div class="label">Ciśnienie</div>
            <div><span class="value" id="pres">--</span><span class="unit">hPa</span></div>
          </div>
        </div>

        <div class="section">
          <h3>Jakość powietrza</h3>
          <div class="row">
            <div class="label">AQI</div>
            <div><span class="value" id="aqi">--</span></div>
          </div>
          <div class="row">
            <div class="label">TVOC</div>
            <div><span class="value" id="tvoc">--</span></div>
          </div>
          <div class="row">
            <div class="label">eCO2</div>
            <div><span class="value" id="eco2">--</span></div>
          </div>
        </div>

        <div class="muted" id="ts">Last update: --</div>
      </div>
    </div>
  </div>

<script>
function setText(id, v) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = (v === undefined || v === null) ? "--" : v;
}

async function refresh() {
  try {
    const r = await fetch("/api/sensors", { cache: "no-store" });
    const j = await r.json();

    const bme = j.bme280 || {};
    const ens = j.ens160 || {};

    setText("temp", bme.temperature_c);
    setText("hum",  bme.humidity_pct);
    setText("pres", bme.pressure_hpa);

    setText("aqi",  ens.aqi);
    setText("tvoc", ens.tvoc_ppb);
    setText("eco2", ens.eco2_ppm);

    if (j.ts) {
      const dt = new Date(j.ts * 1000);
      document.getElementById("ts").textContent = "Last update: " + dt.toLocaleString();
    }
  } catch (e) {
    // console.error(e);
  }
}

setInterval(refresh, 15000);
refresh();
</script>
</body>
</html>
"""


# ===========================
#  MJPEG backend
# ===========================
class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        super().__init__()
        self.frame = None
        self.condition = Condition()
        self.frame_count = 0
        self.last_time = time.time()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
 
        self.frame_count += 1
        now = time.time()
        if now - self.last_time >= 5:
            fps = self.frame_count / (now - self.last_time)
            print(f"[CAM] FPS ~ {fps:.1f}")
            self.frame_count = 0
            self.last_time = now


output = StreamingOutput()
picam2 = None


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            content = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
            return

        if self.path == "/api/sensors":
            body = json.dumps(sensor_data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == "/stream.mjpg":
            self.send_response(200)
            self.send_header("Age", 0)
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=FRAME")
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    if frame is None:
                        continue
                    self.wfile.write(b"--FRAME\r\n")
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Content-Length", len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
            except (BrokenPipeError, ConnectionResetError):
                return
            except Exception as e:
                logging.warning("Client disconnected %s: %s", self.client_address, str(e))
            return

        self.send_error(404)
        self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def start_panel(port: int = 7123):
    global picam2

    # Kamera
    picam2 = Picamera2()
    video_config = picam2.create_video_configuration(main={"size": (640, 480)})
    picam2.configure(video_config)

    try:
        picam2.set_controls({"FrameRate": 24})
    except Exception:
        pass

    picam2.start_recording(JpegEncoder(), FileOutput(output))

    # WEB
    address = ("", port)
    httpd = StreamingServer(address, StreamingHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    print(f"[WEB] Panel działa na porcie {port}")
    print(f"[WEB] Wejdź: http://<IP_RPI>:{port}")

    return httpd
























































































































