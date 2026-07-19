import io
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
from rembg import remove, new_session

app = Flask(__name__)
# Vercel-dan keladigan so'rovlarni bloklamasligi uchun CORS-ni to'liq ochamiz
CORS(app, resources={r"/*": {"origins": "*"}})

# RAMni tejash uchun eng yengil AI model sessiyasini global e'lon qilamiz (~4 MB)
session = new_session("u2netp")

@app.route('/api/remove-bg', methods=['POST'])
def remove_bg():
    try:
        # Frontend-dan kelgan JSON ma'lumotni qabul qilish
        data = request.get_json()
        if not data or 'image_base64' not in data:
            return jsonify({'success': False, 'error': 'JSON so\'rovda image_base64 topilmadi!'}), 400
        
        # Base64 satrni rasm baytlariga o'tkazish
        image_bytes = base64.b64decode(data['image_base64'])
        input_image = Image.open(io.BytesIO(image_bytes))
        
        # Fonni o'chirish
        output_image = remove(input_image, session=session)
        
        # Agar rasm shaffof (RGBA) bo'lsa, uni oq fonga silliq birlashtiramiz
        if output_image.mode in ('RGBA', 'LA'):
            white_bg = Image.new("RGBA", output_image.size, "WHITE")
            white_bg.paste(output_image, (0, 0), output_image)
            final_image = white_bg.convert("RGB")
        else:
            final_image = output_image.convert("RGB")
            
        # Rasmni JPEG formatida xotiraga saqlash
        img_io = io.BytesIO()
        final_image.save(img_io, 'JPEG', quality=95)
        img_io.seek(0)
        
        # Qayta base64 formatiga o'tkazish
        base64_result = base64.b64encode(img_io.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': f"data:image/jpeg;base64,{base64_result}"
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)