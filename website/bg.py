# website/bg.py
from flask import Blueprint, request, jsonify, current_app, session, redirect, url_for, flash, send_file
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
from rembg import remove, new_session
from PIL import Image
import io
import base64
import uuid
import threading

bg = Blueprint('bg', __name__)

# Create a rembg session once
RMBG_SESSION = new_session("u2net")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Temporary storage for processed images
# image_id : {"bytes": ..., "used": False}
processed_images = {}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS




@bg.route("/process", methods=["POST"])
def process_image():
    if "image" not in request.files:
        return jsonify({"ok": False, "error": "No file part"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"ok": False, "error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"ok": False, "error": "Unsupported file type"}), 400

    try:
        img = Image.open(file.stream).convert("RGBA")
        result = remove(img, session=RMBG_SESSION)

        if result.mode != "RGBA":
            result = result.convert("RGBA")

        # -----------------------------------------
        # 🔹 Generate HD version (full resolution)
        # -----------------------------------------
        full_buf = io.BytesIO()
        result.save(full_buf, format="PNG")
        full_buf.seek(0)
        image_bytes = full_buf.getvalue()

        # -----------------------------------------
        # 🔹 Generate preview version (reduced size)
        # -----------------------------------------
        preview = result.copy()
        preview.thumbnail((result.width // 2, result.height // 2))   # half resolution

        preview_buf = io.BytesIO()
        preview.save(preview_buf, format="PNG")
        preview_buf.seek(0)

        # base64 preview to show in frontend
        b64_preview = base64.b64encode(preview_buf.getvalue()).decode("ascii")
        preview_url = f"data:image/png;base64,{b64_preview}"

        # -----------------------------------------
        # 🔹 Save both versions in memory
        # -----------------------------------------
        image_id = str(uuid.uuid4())
        processed_images[image_id] = {
            "preview": preview_buf.getvalue(),
            "hd": image_bytes,
            "used": False,
        }

        # 🔹 Schedule automatic deletion after 5 minutes (300 seconds)
        def delete_image():
            processed_images.pop(image_id, None)
            current_app.logger.info(f"Deleted image {image_id} after 5 minutes")

        threading.Timer(300, delete_image).start()  # 5 minutes

        is_logged_in = "user" in session

        return jsonify({
            "ok": True,
            "result": preview_url,     # only preview goes to front end
            "image_id": image_id,
            "is_logged_in": is_logged_in
        })

    except Exception as e:
        current_app.logger.exception("Failed to process image")
        return jsonify({"ok": False, "error": "Processing failed"}), 500


@bg.route("/download/preview/<image_id>")
def download_preview(image_id):
    if image_id not in processed_images:
        return "Image not found", 404

    return send_file(
        io.BytesIO(processed_images[image_id]["preview"]),
        download_name="preview.png",
        as_attachment=True
    )

# -----------------------------------------------------------
# 🔒 DOWNLOAD ROUTE (Login required)
# -----------------------------------------------------------

@bg.route("/download/hd/<image_id>")
def download_hd(image_id):
    # Require login
    if "user" not in session:
        flash("Login required to download.")
        return redirect(url_for("auth.login"))

    # Validate image
    if image_id not in processed_images:
        return "Image not found or expired", 404

    entry = processed_images[image_id]

    # Optional: Prevent multiple downloads (one-time unlock)
    if entry["used"]:
        return "Download expired. Please process again.", 410

    # Mark as downloaded
    entry["used"] = True

    # Return file
    return send_file(
        io.BytesIO(entry["hd"]),
        download_name="bg_removed.png",
        as_attachment=True
    )



