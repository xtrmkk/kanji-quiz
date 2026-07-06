from flask import Flask, render_template, send_file
import io
from datetime import datetime
from kanji_quiz_gen import generate_pdf

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    pdf_bytes = generate_pdf()
    filename = f'漢字テスト_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename,
    )


if __name__ == '__main__':
    app.run(debug=False)
