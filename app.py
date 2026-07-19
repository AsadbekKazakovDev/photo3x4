import io
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
from rembg import remove, new_session

app = Flask(__name__)
# Vercel-dan so'rovlar muammosiz kelishi uchun CORS to'liq yoqildi
CORS(app, resources={r"/*": {"origins": "*"}})

# RAMni tejash uchun eng yengil AI model sessiyasini global e'lon qilamiz (~4 MB)
session = new_session("u2netp")

@app.route('/api/remove-bg', methods=['POST'])
def remove_bg():
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'Rasm yuklanmadi!'}), 400
        
        file = request.files['image']
        image_bytes = file.read()
        
        # Rasmni o'qish va fonini o'chirish
        input_image = Image.open(io.BytesIO(image_bytes))
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
        
        # Frontend o'qiy olishi uchun base64 formatiga o'tkazish
        base64_image = base64.b64encode(img_io.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': f"data:image/jpeg;base64,{base64_image}"
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)