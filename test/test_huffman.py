"""
Unit tests for Huffman compression implementation.

Tests cover basic functionality, edge cases, and error handling.
"""

import pytest
from huffman.huffman import HuffmanCoder, build_frequency_table, Node
from huffman.utils import BitWriter, BitReader, pack_metadata, unpack_metadata


class TestNode:
    """Test the Node class."""
    
    def test_leaf_node(self):
        """Test that leaf nodes are properly identified."""
        node = Node(freq=10, symbol=65)
        assert node.is_leaf() is True
        assert node.symbol == 65
        assert node.freq == 10
    
    def test_internal_node(self):
        """Test that internal nodes are properly identified."""
        left = Node(freq=5, symbol=65)
        right = Node(freq=10, symbol=66)
        node = Node(freq=15, left=left, right=right)
        assert node.is_leaf() is False
        assert node.symbol is None


class TestBitIO:
    """Test BitWriter and BitReader classes."""
    
    def test_write_read_single_bit(self):
        """Test writing and reading a single bit."""
        writer = BitWriter()
        writer.write_bit(1)
        writer.flush()
        data = writer.get_bytes()
        
        reader = BitReader(data)
        bit = reader.read_bit()
        assert bit == 1
    
    def test_write_read_multiple_bits(self):
        """Test writing and reading multiple bits."""
        writer = BitWriter()
        bits = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0]
        for b in bits:
            writer.write_bit(b)
        writer.flush()
        data = writer.get_bytes()
        
        reader = BitReader(data)
        read_bits = []
        for _ in range(len(bits)):
            b = reader.read_bit()
            if b is not None:
                read_bits.append(b)
        
        assert read_bits[:len(bits)] == bits
    
    def test_write_read_bytes(self):
        """Test writing and reading raw bytes."""
        writer = BitWriter()
        test_bytes = b'Hello, World!'
        writer.write_bytes(test_bytes)
        data = writer.get_bytes()
        
        reader = BitReader(data)
        read_bytes = reader.read_bytes(len(test_bytes))
        assert read_bytes == test_bytes


class TestMetadata:
    """Test metadata packing and unpacking."""
    
    def test_pack_unpack_metadata(self):
        """Test that metadata can be packed and unpacked correctly."""
        freqs = {65: 10, 66: 20, 67: 30}
        packed = pack_metadata(freqs)
        
        reader = BitReader(packed)
        unpacked, _ = unpack_metadata(reader)
        
        assert unpacked == freqs
    
    def test_empty_metadata(self):
        """Test packing empty frequency table."""
        freqs = {}
        packed = pack_metadata(freqs)
        assert len(packed) == 2  # Just the count


class TestHuffmanCoder:
    """Test the HuffmanCoder class."""
    
    def test_build_frequency_table(self):
        """Test building frequency table from data."""
        data = b'ABRACADABRA'
        freqs = build_frequency_table(data)
        
        assert freqs[ord('A')] == 5
        assert freqs[ord('B')] == 2
        assert freqs[ord('R')] == 2
        assert freqs[ord('C')] == 1
        assert freqs[ord('D')] == 1
    
    def test_build_tree(self):
        """Test building Huffman tree."""
        coder = HuffmanCoder()
        freqs = {65: 5, 66: 2, 67: 1}
        tree = coder.build_tree_from_freq(freqs)
        
        assert tree is not None
        assert tree.freq == 8
        assert tree.is_leaf() is False
    
    def test_tree_to_codes(self):
        """Test generating codes from tree."""
        coder = HuffmanCoder()
        freqs = {65: 5, 66: 2, 67: 1}
        tree = coder.build_tree_from_freq(freqs)
        codes = coder.tree_to_codes(tree)
        
        assert len(codes) == 3
        assert all(isinstance(code, str) for code in codes.values())
        assert all(set(code).issubset({'0', '1'}) for code in codes.values())
    
    def test_entropy_calculation(self):
        """Test Shannon entropy calculation."""
        coder = HuffmanCoder()
        # Uniform distribution should have maximum entropy
        freqs = {0: 1, 1: 1, 2: 1, 3: 1}
        entropy = coder.entropy_from_freq(freqs)
        assert 1.9 < entropy < 2.1  # Should be 2.0 for 4 symbols
        
        # Single symbol should have 0 entropy
        freqs = {0: 100}
        entropy = coder.entropy_from_freq(freqs)
        assert entropy == 0.0
    
    def test_compress_decompress_basic(self):
        """Test basic compression and decompression."""
        coder = HuffmanCoder()
        original = b'Hello, World! This is a test message.'
        
        compressed, meta = coder.compress_bytes(original)
        decompressed = coder.decompress_bytes(compressed)
        
        assert decompressed == original
    
    def test_compress_decompress_repeated_chars(self):
        """Test compression with highly repetitive data."""
        coder = HuffmanCoder()
        original = b'AAAAAAAAAA BBBB CC D'
        
        compressed, meta = coder.compress_bytes(original)
        decompressed = coder.decompress_bytes(compressed)
        
        assert decompressed == original
        # Compression should be effective for repetitive data
        assert len(compressed) < len(original)
    
    def test_compress_decompress_single_char(self):
        """Test compression with single repeated character."""
        coder = HuffmanCoder()
        original = b'AAAAAAAAAA'
        
        compressed, meta = coder.compress_bytes(original)
        decompressed = coder.decompress_bytes(compressed)
        
        assert decompressed == original
    
    def test_compress_decompress_binary(self):
        """Test compression with binary data."""
        coder = HuffmanCoder()
        original = bytes(range(256))
        
        compressed, meta = coder.compress_bytes(original)
        decompressed = coder.decompress_bytes(compressed)
        
        assert decompressed == original
    
    def test_compress_empty_raises_error(self):
        """Test that compressing empty data raises an error."""
        coder = HuffmanCoder()
        with pytest.raises(ValueError, match="Cannot compress empty data"):
            coder.compress_bytes(b'')
    
    def test_decompress_empty_raises_error(self):
        """Test that decompressing empty data raises an error."""
        coder = HuffmanCoder()
        with pytest.raises(ValueError, match="Cannot decompress empty data"):
            coder.decompress_bytes(b'')
    
    def test_decompress_invalid_data(self):
        """Test that decompressing invalid data raises an error."""
        coder = HuffmanCoder()
        with pytest.raises(ValueError):
            coder.decompress_bytes(b'invalid data')
    
    def test_tree_to_dict(self):
        """Test converting tree to dictionary."""
        coder = HuffmanCoder()
        freqs = {65: 5, 66: 2}
        tree = coder.build_tree_from_freq(freqs)
        tree_dict = coder.tree_to_dict(tree)
        
        assert isinstance(tree_dict, dict)
        assert 'freq' in tree_dict
        assert 'symbol' in tree_dict
        assert 'left' in tree_dict
        assert 'right' in tree_dict


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_unicode_text(self):
        """Test with UTF-8 encoded text."""
        coder = HuffmanCoder()
        original = 'Hola, mundo! 🌍'.encode('utf-8')
        
        compressed, meta = coder.compress_bytes(original)
        decompressed = coder.decompress_bytes(compressed)
        
        assert decompressed == original
        assert decompressed.decode('utf-8') == 'Hola, mundo! 🌍'
    
    def test_large_data(self):
        """Test with larger data."""
        coder = HuffmanCoder()
        # Create 1MB of somewhat random but compressible data
        original = (b'ABCD' * 10000 + b'XYZ' * 5000 + b'123' * 3000)
        
        compressed, meta = coder.compress_bytes(original)
        decompressed = coder.decompress_bytes(compressed)
        
        assert decompressed == original
    
    def test_compression_ratio(self):
        """Test that compression actually reduces size for repetitive data."""
        coder = HuffmanCoder()
        original = b'A' * 1000 + b'B' * 100 + b'C' * 10
        
        compressed, meta = coder.compress_bytes(original)
        
        # Should achieve significant compression
        ratio = len(compressed) / len(original)
        assert ratio < 0.5  # At least 50% compression


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
