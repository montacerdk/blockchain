#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 18:45:15 2024

@author: montacer.dkhilali@gmail.com
"""

import datetime
import hashlib
import json

from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


# Part 1 - Building a Blockchain

# Adding a transaction to the Blockchain
# Making a consensus algorithm to make sure that all nodes have the same chain

class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()

    # Create a block.
    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions,
        }

        self.transactions = []
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

    # Add a transaction to the list of transactions.
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount,
        })
        previous_block = self.get_last_block()

        return previous_block['index'] + 1

    # Add a node to the list of nodes.
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    # Replace the chain with the longest chain if needed.
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)

        for node in network:
            response = requests.get(f'http://{node}/get-chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True

        return False

# creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')

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
    blockchain.add_transaction(sender = node_address, receiver = 'Jo', amount = 1)

    response = {
        'message': 'Congrats, you just mined a block!',
        'index': new_block['index'],
        'timestamp': new_block['timestamp'],
        'proof': new_block['proof'],
        'previous_hash': new_block['previous_hash'],
        'transactions': new_block['transactions'],
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

# Add a transaction to the Blockchain.
@app.route('/add-transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']

    if not all(key in json for key in transaction_keys):
        return 'Bad Request - Some elements of the transaction are missing.', 400

    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}

    return jsonify(response), 201

# Connect new nodes.
@app.route('/connect-node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')

    if nodes is None:
        return 'Bad Request - No node was provided.', 400

    for node in nodes:
        blockchain.add_node(node)

    response = {
        'message': 'All the nodes are now connected. The Montacoin Blockchain now contains the following nodes:',
        'total_nodes': list(blockchain.nodes),
    }

    return jsonify(response), 201

# Replace the chain by the longest chain if needed.
@app.route('/replace-chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()

    if is_chain_replaced:
        response = {
            'message': 'The nodes had different chains so the chain was replaced by the longest one.',
            'new_chain': blockchain.chain,
        }
    else:
        response = {
            'message': 'All good. The chain is the largest one.',
            'actual_chain': blockchain.chain,
        }

    return jsonify(response), 200

# Run the app.
app.run(host = '0.0.0.0', port = 5002)
