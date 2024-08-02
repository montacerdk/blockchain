#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 18:45:15 2024

@author: montacerdk
"""

import datetime
import hashlib
import json

from flask import Flask, jsonify


class Blockchain:

    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, previous_hash = '0')

    # Create a block.
    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
        }

        self.chain.append(block)

        return block

    # Get the last block of the chain.
    def get_last_block(self):
        return self.chain[-1]

    # Resolve the proof of work.
    def resolve_proof_of_work(self, previous_proof):
        new_proof = 1
        is_valid_proof = False

        while is_valid_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()

            if hash_operation[:4] == '0000':
                is_valid_proof = True
            else:
                new_proof += 1

        return new_proof

    # Hash a block.
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()

        return hashlib.sha256(encoded_block).hexdigest()

    # Check if the hole Blockchain is valid.
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        current_block_index = 1

        while current_block_index < len(chain):
            current_block = chain[current_block_index]

            # First, we verify if the previous hash is equal to the hash of the current block.
            if current_block['previous_hash'] != self.hash(previous_block):
                return False

            # Second, we verify that the proof of the current block respects our proof of work.
            previous_proof = previous_block['proof']
            current_proof = current_block['proof']

            hash_operation = hashlib.sha256(str(current_proof**2 - previous_proof**2).encode()).hexdigest()


            if hash_operation[:4] != '0000':
                return False

            previous_block = current_block
            current_block_index += 1

        return True


# Web app to serve our Blockchain.
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Create a Blockchain.
blockchain = Blockchain()


# Mine a block.
@app.route('/mine-block', methods = ['GET'])
def mine_block():
    last_block = blockchain.get_last_block()
    previous_proof = last_block['proof']
    proof = blockchain.resolve_proof_of_work(previous_proof)
    previous_hash = blockchain.hash(last_block)
    new_block = blockchain.create_block(proof, previous_hash)

    response = {
        'message': 'Congrats, you just mined a block!',
        'index': new_block['index'],
        'timestamp': new_block['timestamp'],
        'proof': new_block['proof'],
        'previous_hash': new_block['previous_hash'],
    }

    return jsonify(response), 200


# Get the full Blockchain.
@app.route('/get-chain', methods = ['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }

    return jsonify(response), 200


# Check if the Blockchain is valid.
@app.route('/is-chain-valid', methods = ['GET'])
def is_chain_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)

    if is_valid:
        response = {
            'message': 'The Blockchain is valid.',
        }
    else:
        response = {
            'message': 'The Blockchain is not valid.',
        }

    return jsonify(response), 200


# Run the app.
app.run(host = '0.0.0.0', port = 5000)
