import hashlib
import json
import time
from uuid import uuid4

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash):
        """
        Represents a single block in the blockchain.

        Args:
            index (int): The index of the block in the chain.
            timestamp (float): The time the block was created.
            transactions (list): A list of transactions (certificate issuances) included in this block.
            previous_hash (str): The hash of the previous block in the chain.
        """
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """
        Calculates the SHA-256 hash of the block's contents.
        """
        # Ensure consistent ordering for reproducible hashes
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    def __init__(self):
        """
        Represents the blockchain itself.
        """
        self.chain = []  # Stores the sequence of blocks
        self.pending_transactions = []  # Transactions waiting to be included in a block
        self.create_genesis_block() # Create the first block

    def create_genesis_block(self):
        """
        Creates the very first block in the chain (the genesis block).
        """
        # The genesis block has no previous block, so its previous_hash is "0"
        self.new_block(previous_hash="0")

    def new_block(self, previous_hash=None):
        """
        Creates a new block and adds it to the chain.

        Args:
            previous_hash (str, optional): The hash of the previous block.
                                           If None, it takes the hash of the last block in the chain.

        Returns:
            Block: The newly created block.
        """
        # Take all pending transactions and include them in the new block
        block = Block(
            index=len(self.chain) + 1,
            timestamp=time.time(),
            transactions=self.pending_transactions,
            previous_hash=previous_hash or self.last_block.hash, # Use provided hash or the last block's hash
        )
        # Clear the pending transactions after they are added to a block
        self.pending_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, issuer_id, recipient_address, course_name, issue_date):
        """
        Creates a new transaction representing a certificate issuance.

        Args:
            issuer_id (str): The identifier of the issuing institution.
            recipient_address (str): The unique identifier of the student's wallet.
            course_name (str): The name of the course completed.
            issue_date (str): The date the certificate was issued (e.g., "YYYY-MM-DD").

        Returns:
            int: The index of the block that this transaction will be added to.
        """
        # Generate a unique ID for the certificate/SBT
        certificate_id = str(uuid4())

        transaction = {
            'issuer_id': issuer_id,
            'recipient_address': recipient_address,
            'course_name': course_name,
            'issue_date': issue_date,
            'certificate_id': certificate_id, # Unique identifier for this certificate
        }
        # Add the transaction to the list of pending transactions
        self.pending_transactions.append(transaction)
        # Return the index of the *next* block that will be created
        return self.last_block.index + 1

    @property
    def last_block(self):
        """
        Returns the last block in the blockchain.
        """
        return self.chain[-1]

    def get_certificates_for_student(self, student_address):
        """
        Retrieves all certificates (transactions) associated with a given student address.

        Args:
            student_address (str): The address of the student's wallet.

        Returns:
            list: A list of transaction dictionaries for the student.
        """
        certificates = []
        # Iterate through all blocks and their transactions
        for block in self.chain:
            for tx in block.transactions:
                # Check if the recipient address matches
                if tx.get('recipient_address') == student_address:
                    certificates.append(tx)
        return certificates

    def verify_certificate(self, certificate_id, recipient_address):
        """
        Verifies if a certificate exists on the blockchain and is tied to the given recipient address.

        Args:
            certificate_id (str): The unique ID of the certificate to verify.
            recipient_address (str): The expected recipient's wallet address.

        Returns:
            tuple: (bool, dict or None) - True and the certificate details if found and matches recipient,
                                          False and None otherwise.
        """
        # Iterate through all blocks and their transactions
        for block in self.chain:
            for tx in block.transactions:
                # Check if both the certificate ID and recipient address match
                if tx.get('certificate_id') == certificate_id and tx.get('recipient_address') == recipient_address:
                    return True, tx # Certificate found and recipient matches
        return False, None # Certificate not found or recipient doesn't match