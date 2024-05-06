from flask import Flask, request, send_file
from PIL import Image
import io
import pydicom
import numpy as np

app = Flask(__name__)

def find_average_frame(ds):
    non_black_counts = []
    for i in range(ds.NumberOfFrames):
        frame = ds.pixel_array[i]
        non_black_pixels = np.count_nonzero(frame)
        non_black_counts.append(non_black_pixels)

    average_non_black_pixels = np.mean(non_black_counts)
    # Find the index of the frame closest to the average
    closest_index = np.argmin(np.abs(non_black_counts - average_non_black_pixels))
    return closest_index

def convert_dicom_to_jpg(dicom_file):
    ds = pydicom.dcmread(dicom_file)

    if 'NumberOfFrames' in ds and ds.NumberOfFrames > 1:
        # Find the frame with an average amount of non-black pixels
        average_frame_index = find_average_frame(ds)

        # Convert the average frame to a JPEG image
        frame = ds.pixel_array[average_frame_index]
        scaled_frame = frame * 255.0 / frame.max()
        scaled_frame = scaled_frame.astype(np.uint8)
        img = Image.fromarray(scaled_frame)

        img_byte_array = io.BytesIO()
        img.save(img_byte_array, format='JPEG')
        img_byte_array.seek(0)

        return img_byte_array

    else:
        # Convert single-frame DICOM to a JPEG file
        frame = ds.pixel_array
        scaled_frame = frame * 255.0 / frame.max()
        scaled_frame = scaled_frame.astype(np.uint8)
        img = Image.fromarray(scaled_frame)

        img_byte_array = io.BytesIO()
        img.save(img_byte_array, format='JPEG')
        img_byte_array.seek(0)

        return img_byte_array

@app.route('/convert', methods=['POST'])
def convert_dicom_to_jpg_endpoint():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    if file and file.filename.lower().endswith('.dcm'):
        try:
            jpg_bytes = convert_dicom_to_jpg(file)
            return send_file(jpg_bytes, mimetype='image/jpeg')
        except Exception as e:
            return f'An error occurred: {str(e)}'
    else:
        return 'Invalid file format. Please upload a DICOM file.'

if __name__ == "__main__":
    app.run(debug=True)
