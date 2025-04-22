from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain import Blockchain # Import the Blockchain class from blockchain.py

# Instantiate the Flask App
app = Flask(__name__)

# Generate a unique node identifier (optional for this simplified model)
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    """
    Endpoint to "mine" a new block.
    In this simplified model, mining just means adding pending transactions to a new block.
    """
    # Create the new Block by adding pending transactions
    last_block = blockchain.last_block
    previous_hash = last_block.hash # Get the hash of the last block

    block = blockchain.new_block(previous_hash) # Create the new block

    response = {
        'message': "New Block Forged",
        'index': block.index,
        'transactions': block.transactions,
        'previous_hash': block.previous_hash,
        'hash': block.hash,
    }
    return jsonify(response), 200

@app.route('/issue', methods=['POST'])
def issue_certificate():
    """
    Endpoint for institutions to issue a new certificate.
    Expects JSON data with issuer_id, recipient_address, course_name, and issue_date.
    """
    values = request.get_json() # Get the JSON data from the request body

    # Check that the required fields are in the POST'ed data
    required = ['issuer_id', 'recipient_address', 'course_name', 'issue_date']
    if not all(key in values for key in required):
        return jsonify({'error': 'Missing required values'}), 400

    # Create a new Transaction (certificate issuance)
    # The certificate_id is generated within new_transaction
    index_of_block_to_contain = blockchain.new_transaction(
        values['issuer_id'],
        values['recipient_address'],
        values['course_name'],
        values['issue_date']
    )

    response = {'message': f'Certificate issuance transaction added to pending. It will be included in Block {index_of_block_to_contain}.'}
    return jsonify(response), 201 # 201 Created

@app.route('/chain', methods=['GET'])
def full_chain():
    """
    Endpoint to view the full blockchain.
    """
    response = {
        # Convert Block objects to dictionaries for JSON serialization
        'chain': [block.__dict__ for block in blockchain.chain],
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/certificates/<string:student_address>', methods=['GET'])
def get_student_certificates(student_address):
    """
    Endpoint for students (or anyone) to view certificates associated with a specific address.
    """
    certificates = blockchain.get_certificates_for_student(student_address)
    response = {
        'student_address': student_address,
        'certificates': certificates,
        'count': len(certificates)
    }
    return jsonify(response), 200

@app.route('/verify', methods=['POST'])
def verify_certificate_route():
    """
    Endpoint for third parties (like employers) to verify a certificate.
    Expects JSON data with certificate_id and recipient_address.
    """
    values = request.get_json()

    required = ['certificate_id', 'recipient_address']
    if not all(key in values for key in required):
        return jsonify({'error': 'Missing required values'}), 400

    # Verify the certificate using the blockchain logic
    is_valid, certificate_details = blockchain.verify_certificate(
        values['certificate_id'],
        values['recipient_address']
    )

    if is_valid:
        response = {
            'message': 'Certificate is valid and matches the recipient.',
            'certificate_details': certificate_details
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Certificate not found or recipient does not match.'
        }
        return jsonify(response), 404 # 404 Not Found or 400 Bad Request depending on interpretation

if __name__ == '__main__':
    # Run the Flask app
    # debug=True allows for automatic reloading and better error messages during development
    app.run(host='0.0.0.0', port=5000, debug=True)