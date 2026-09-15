from flask import Flask, abort, request
import tempfile
import tarfile
import gzip
import os

app = Flask(__name__)

@app.route("/")
def index():
    return """<!DOCTYPE html>
<html>
<head><title>Ruby Gems Viewer</title></head>
<body>
<h1>Ruby Gems Metadata Viewer</h1>
<form method='POST' action='/upload' enctype='multipart/form-data'>
<input type='file' name='file' accept='.gem'/>
<input type='submit' value='Upload'/>
</form>
</body>
</html>"""

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        abort(400, description="No file part in the request")

    file = request.files['file']

    if file.filename == '':
        abort(400, description="No selected file")

    try:
        # .gem files are tar archives containing metadata.gz and data.tar.gz
        with tarfile.open(fileobj=file, mode='r:*') as gem_tar:
            with tempfile.TemporaryDirectory() as temp_dir:
                gem_tar.extractall(path=temp_dir,)

                metadata_path = os.path.join(temp_dir, 'metadata.gz')
                if os.path.exists(metadata_path):
                    try:
                        with gzip.open(metadata_path, 'rt') as gz:
                            metadata_content = gz.read()
                    except OSError:
                        raw_data = open(metadata_path, 'rb').read()
                        abort(400, description="Failed to decompress metadata.gz. The raw data is: " + repr(raw_data))
                    return f"""<!DOCTYPE html>
<html>
<head><title>Gem Metadata</title></head>
<body>
<h1>Gem Metadata</h1>
<pre>{metadata_content}</pre>
<a href="/">Back</a>
</body>
</html>"""

                return "No metadata.gz found in gem file"
    except tarfile.TarError as e:
        abort(400, description="Invalid gem file: " + str(e))
