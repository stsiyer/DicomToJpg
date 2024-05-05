from flask import Flask, request, send_file
from PIL import Image
import io
import pydicom

app = Flask(__name__)

def convert_multiframe_dicom_to_jpg(dicom_file):
    ds = pydicom.dcmread(dicom_file)

    frame = ds.pixel_array[0]

    img = Image.fromarray(frame)

    img_byte_array = io.BytesIO()
    img.save(img_byte_array, format='JPEG')
    img_byte_array.seek(0)

    return img_byte_array

@app.route('/convert', methods=['POST'])
def convert_dicom_to_jpg():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    if file and file.filename.lower().endswith('.dcm'):
        try:
            jpg_bytes = convert_multiframe_dicom_to_jpg(file)
            return send_file(jpg_bytes, mimetype='image/jpeg')
        except Exception as e:
            return f'An error occurred: {str(e)}'
    else:
        return 'Invalid file format. Please upload a DICOM file.'

if __name__ == "__main__":
    app.run(debug=True)
