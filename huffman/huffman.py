"""
Huffman Coding Implementation

This module provides a complete implementation of Huffman coding for data compression.
It includes tree construction, encoding, decoding, and entropy calculation.
"""

import heapq
from collections import Counter
from math import log2
from huffman.utils import BitWriter, BitReader, pack_metadata, unpack_metadata


class Node:
    """
    Represents a node in the Huffman tree.
    
    Attributes:
        freq (int): Frequency/weight of this node
        symbol (int|None): Byte value (0-255) for leaf nodes, None for internal nodes
        left (Node|None): Left child node
        right (Node|None): Right child node
    """
    def __init__(self, freq, symbol=None, left=None, right=None):
        self.freq = freq
        self.symbol = symbol
        self.left = left
        self.right = right

    def is_leaf(self):
        """Check if this node is a leaf (has a symbol)."""
        return self.symbol is not None
    
    def __lt__(self, other):
        """Compare nodes by frequency for heapq operations."""
        return self.freq < other.freq

class HuffmanCoder:
    """
    Huffman coding encoder/decoder.
    
    Provides methods for building Huffman trees, generating codes,
    compressing and decompressing data, and calculating entropy.
    """
    
    def build_tree_from_freq(self, freq_dict):
        """
        Build a Huffman tree from a frequency dictionary.
        
        Args:
            freq_dict (dict): Dictionary mapping symbols (bytes) to their frequencies
            
        Returns:
            Node: Root node of the Huffman tree, or None if freq_dict is empty
        """
        heap = []
        for sym, f in freq_dict.items():
            heapq.heappush(heap, Node(f, symbol=sym))
        if not heap:
            return None
        while len(heap) > 1:
            n1 = heapq.heappop(heap)
            n2 = heapq.heappop(heap)
            merged = Node(n1.freq + n2.freq, None, n1, n2)
            heapq.heappush(heap, merged)
        return heapq.heappop(heap)

    def tree_to_codes(self, root):
        """
        Generate Huffman codes from a tree.
        
        Args:
            root (Node): Root of the Huffman tree
            
        Returns:
            dict: Dictionary mapping symbols to their binary codes (as strings)
        """
        codes = {}
        if root is None:
            return codes
        def walk(node, prefix=''):
            if node.is_leaf():
                codes[node.symbol] = prefix or '0'
                return
            walk(node.left, prefix + '0')
            walk(node.right, prefix + '1')
        walk(root)
        return codes

    def tree_to_dict(self, node):
        """
        Convert Huffman tree to a dictionary for JSON serialization.
        
        Args:
            node (Node): Node to convert
            
        Returns:
            dict: Dictionary representation of the tree
        """
        if node is None:
            return None
        return {
            'freq': node.freq,
            'symbol': node.symbol,
            'left': self.tree_to_dict(node.left),
            'right': self.tree_to_dict(node.right)
        }

    def entropy_from_freq(self, freq_dict):
        """
        Calculate Shannon entropy from frequency distribution.
        
        Args:
            freq_dict (dict): Dictionary mapping symbols to frequencies
            
        Returns:
            float: Entropy in bits per symbol
        """
        total = sum(freq_dict.values())
        if total == 0:
            return 0.0
        H = 0.0
        for f in freq_dict.values():
            p = f / total
            H -= p * log2(p)
        return H

    def average_code_length(self, freq_dict, codes):
        """
        Calculate average code length from frequency distribution and codes.
        
        Args:
            freq_dict (dict): Dictionary mapping symbols to frequencies
            codes (dict): Dictionary mapping symbols to their binary codes (as strings)
            
        Returns:
            float: Average code length in bits per symbol
        """
        total = sum(freq_dict.values())
        if total == 0:
            return 0.0
        
        weighted_sum = 0.0
        for symbol, freq in freq_dict.items():
            if symbol in codes:
                code_length = len(codes[symbol])
                weighted_sum += freq * code_length
        
        return weighted_sum / total

    def compress_bytes(self, data: bytes):
        """
        Compress byte data using Huffman coding.
        
        Args:
            data (bytes): Data to compress
            
        Returns:
            tuple: (compressed_bytes, metadata_dict)
                compressed_bytes includes frequency table and encoded data
                metadata_dict contains compression statistics
                
        Raises:
            ValueError: If data is empty
        """
        if not data:
            raise ValueError("Cannot compress empty data")
            
        freqs = Counter(data)
        
        # Handle single symbol case
        if len(freqs) == 1:
            # Just store the symbol and count
            symbol = list(freqs.keys())[0]
            count = freqs[symbol]
            bw = BitWriter()
            meta = pack_metadata(freqs)
            bw.write_bytes(meta)
            bw.flush()
            return bw.get_bytes(), {'freq_count': 1, 'single_symbol': True}
        
        root = self.build_tree_from_freq(freqs)
        codes = self.tree_to_codes(root)
        bw = BitWriter()
        
        # write metadata
        meta = pack_metadata(freqs)
        bw.write_bytes(meta)
        
        # write bits
        for b in data:
            code = codes[b]
            for ch in code:
                bw.write_bit(1 if ch == '1' else 0)
        bw.flush()
        return bw.get_bytes(), {'freq_count': len(freqs)}

    def decompress_bytes(self, data: bytes):
        """
        Decompress Huffman-encoded data.
        
        Args:
            data (bytes): Compressed data (must include metadata)
            
        Returns:
            bytes: Decompressed original data
            
        Raises:
            ValueError: If data is invalid or corrupted
        """
        if not data:
            raise ValueError("Cannot decompress empty data")
            
        br = BitReader(data)
        freqs, _ = unpack_metadata(br)
        
        if not freqs:
            raise ValueError("Invalid compressed data: no frequency table found")
        
        # Handle single symbol case
        if len(freqs) == 1:
            symbol, count = list(freqs.items())[0]
            return bytes([symbol] * count)
        
        root = self.build_tree_from_freq(freqs)
        if root is None:
            return b''
            
        # Calculate expected output size
        expected_size = sum(freqs.values())
        
        out = bytearray()
        node = root
        while len(out) < expected_size:
            bit = br.read_bit()
            if bit is None:
                break
            node = node.right if bit == 1 else node.left
            if node.is_leaf():
                out.append(node.symbol)
                node = root
        return bytes(out)

def build_frequency_table(data: bytes):
    """
    Build a frequency table from byte data.
    
    Args:
        data (bytes): Input data
        
    Returns:
        dict: Dictionary mapping byte values to their frequencies
    """
    return dict(Counter(data))
