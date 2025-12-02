from flask import Flask, request, jsonify, send_file
from io import BytesIO
from huffman.huffman import HuffmanCoder, build_frequency_table
import time
import gzip
import json

app = Flask(__name__, static_folder='static', static_url_path='/static')

MAX_FILE_SIZE = 750 * 1024 * 1024  # 750 MB


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/favicon.ico')
def favicon():
    return '', 204


@app.route('/api/analyze', methods=['POST'])
def analyze():
    f = request.files.get('file')
    if not f:
        return jsonify({'error': 'No file provided'}), 400
    
    data = f.read()
    
    if len(data) == 0:
        return jsonify({'error': 'File is empty'}), 400
    
    if len(data) > MAX_FILE_SIZE:
        return jsonify({'error': f'File too large (max {MAX_FILE_SIZE // (1024*1024)} MB)'}), 413
    
    try:
        freqs = build_frequency_table(data)
        coder = HuffmanCoder()
        tree = coder.build_tree_from_freq(freqs)
        entropy = coder.entropy_from_freq(freqs)
        tree_dict = coder.tree_to_dict(tree)
        
        codes = coder.tree_to_codes(tree)
        
        avg_code_length = coder.average_code_length(freqs, codes)
        
        efficiency = (entropy / avg_code_length * 100) if avg_code_length > 0 else 100.0
        
        codes_serializable = {str(k): v for k, v in codes.items()}
        
        return jsonify({
            'frequencies': freqs,
            'entropy': entropy,
            'tree': tree_dict,
            'original_size': len(data),
            'codes': codes_serializable,
            'avg_code_length': avg_code_length,
            'efficiency': efficiency
        })
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/api/compress', methods=['POST'])
def compress():
    f = request.files.get('file')
    if not f:
        return jsonify({'error': 'No file provided'}), 400
    
    data = f.read()
    
    if len(data) == 0:
        return jsonify({'error': 'File is empty'}), 400
    
    if len(data) > MAX_FILE_SIZE:
        return jsonify({'error': f'File too large (max {MAX_FILE_SIZE // (1024*1024)} MB)'}), 413
    
    coder = HuffmanCoder()
    start = time.time()
    
    try:
        compressed_bytes, meta = coder.compress_bytes(data)
        duration = time.time() - start
    except Exception as e:
        return jsonify({'error': f'Compression failed: {str(e)}'}), 500

    # Compute gzip size for comparison
    gz_buf = BytesIO()
    with gzip.GzipFile(fileobj=gz_buf, mode='wb') as gz:
        gz.write(data)
    gz_bytes = gz_buf.getvalue()

    bio = BytesIO(compressed_bytes)
    bio.seek(0)

    stats = {
        'original_size': len(data),
        'compressed_size': len(compressed_bytes),
        'gzip_size': len(gz_bytes),
        'duration_s': duration,
        'meta': meta
    }
    
    response = send_file(
        bio,
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name='compressed.huff',
        conditional=False
    )
    # Use compact JSON without newlines for the header
    response.headers['X-Comp-Stats'] = json.dumps(stats, separators=(',', ':'))
    return response


@app.route('/api/decompress', methods=['POST'])
def decompress():
    f = request.files.get('file')
    if not f:
        return jsonify({'error': 'No file provided'}), 400
    
    data = f.read()
    
    if len(data) == 0:
        return jsonify({'error': 'File is empty'}), 400
    
    if len(data) > MAX_FILE_SIZE:
        return jsonify({'error': f'File too large (max {MAX_FILE_SIZE // (1024*1024)} MB)'}), 413
    
    coder = HuffmanCoder()
    try:
        decompressed = coder.decompress_bytes(data)
    except ValueError as e:
        return jsonify({'error': f'Invalid file format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Decompression failed: {str(e)}'}), 500
    
    bio = BytesIO(decompressed)
    bio.seek(0)
    
    return send_file(
        bio,
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name='decompressed.bin',
        conditional=False
    )


if __name__ == '__main__':
    app.run(debug=True, port=8000)