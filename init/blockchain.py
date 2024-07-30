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

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
        }

        self.chain.append(block)

        return block

    def get_previous_block(self):
        return self.chain[-1]

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
