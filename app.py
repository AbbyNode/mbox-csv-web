import os
import mailbox
import csv
import io
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from email.utils import parsedate_to_datetime
from email.header import decode_header
import tempfile

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

ALLOWED_EXTENSIONS = {'mbox'}


def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def decode_mime_words(s):
    """Decode MIME encoded words in headers."""
    if s is None:
        return ''
    decoded_fragments = decode_header(s)
    return ''.join(
        str(fragment, encoding or 'utf-8') if isinstance(fragment, bytes) else str(fragment)
        for fragment, encoding in decoded_fragments
    )


def extract_email_address(header):
    """Extract email address from a header field."""
    if not header:
        return ''
    # Remove angle brackets and extract email
    if '<' in header and '>' in header:
        start = header.index('<') + 1
        end = header.index('>')
        return header[start:end]
    return header


def get_message_body(message):
    """Extract the body content from an email message."""
    body = ''
    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition', ''))
            
            # Skip attachments
            if 'attachment' in content_disposition:
                continue
                
            if content_type == 'text/plain':
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')
                        break
                except Exception:
                    pass
    else:
        try:
            payload = message.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='ignore')
        except Exception:
            pass
    
    return body.strip()


def convert_mbox_to_csv(mbox_path):
    """Convert an mbox file to CSV format."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header row
    writer.writerow(['From', 'To', 'Cc', 'Subject', 'Date', 'Body'])
    
    # Open and parse the mbox file
    mbox = mailbox.mbox(mbox_path)
    
    for message in mbox:
        try:
            # Extract and decode headers
            from_header = decode_mime_words(message.get('From', ''))
            to_header = decode_mime_words(message.get('To', ''))
            cc_header = decode_mime_words(message.get('Cc', ''))
            subject = decode_mime_words(message.get('Subject', ''))
            
            # Parse date
            date_str = ''
            date_header = message.get('Date')
            if date_header:
                try:
                    date_obj = parsedate_to_datetime(date_header)
                    date_str = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    date_str = str(date_header)
            
            # Get message body
            body = get_message_body(message)
            
            # Write row to CSV
            writer.writerow([
                from_header,
                to_header,
                cc_header,
                subject,
                date_str,
                body
            ])
        except Exception as e:
            # Log error but continue processing other messages
            print(f"Error processing message: {e}")
            continue
    
    output.seek(0)
    return output


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    """Handle file upload and conversion."""
    # Check if file was uploaded
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    # Check if filename is empty
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    # Check if file has allowed extension
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload an .mbox file', 'error')
        return redirect(url_for('index'))
    
    try:
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        # Convert mbox to CSV
        csv_output = convert_mbox_to_csv(temp_path)
        
        # Clean up temporary file
        os.remove(temp_path)
        
        # Prepare CSV file for download
        csv_bytes = io.BytesIO(csv_output.getvalue().encode('utf-8'))
        csv_bytes.seek(0)
        
        # Generate output filename
        output_filename = filename.rsplit('.', 1)[0] + '.csv'
        
        return send_file(
            csv_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=output_filename
        )
    
    except Exception as e:
        flash(f'Error converting file: {str(e)}', 'error')
        # Clean up temporary file if it exists
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
