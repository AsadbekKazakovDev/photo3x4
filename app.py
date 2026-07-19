import io
import base64
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from rembg import remove
from PIL import Image, ImageOps

app = Flask(__name__)
# Frontend boshqa port yoki serverda tursa muammo bo'lmasligi uchun CORS yoqamiz
CORS(app)

@app.route('/api/remove-bg', methods=['POST'])
def remove_background():
    try:
        data = request.json
        if not data or 'image_base64' not in data:
            return jsonify({'error': 'Rasm maʼlumotlari yuborilmadi!'}), 400

        # Front-enddan kelgan Base64 matnni rasmga aylantirish
        image_bytes = base64.b64decode(data['image_base64'])
        input_image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

        # 1. AI Model orqali fonni shaffof (transparent) qilish
        output_image = remove(input_image)

        # 2. Shaffof rasmni toza oq fonga joylashtirish (3x4 uchun oq fon shart)
        white_background = Image.new("RGBA", output_image.size, "WHITE")
        final_image = Image.alpha_composite(white_background, output_image).convert("RGB")

        # Natijani xotirada (Buffer) saqlash
        img_io = io.BytesIO()
        final_image.save(img_io, 'JPEG', quality=95)
        img_io.seek(0)

        return send_file(img_io, mimetype='image/jpeg')

    except Exception as e:
        print(f"Xatolik: {str(e)}")
        return jsonify({'error': f'Server xatoligi: {str(e)}'}), 500

if __name__ == '__main__':
    # Mahalliy tarmoqda ham ishlatish uchun 0.0.0.0 va 5000-portda ishga tushiramiz
    app.run(host='0.0.0.0', port=5000, debug=True)