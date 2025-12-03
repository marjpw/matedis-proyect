import pytest
from huffman.huffman import HuffmanCoder, build_frequency_table, Node
from huffman.utils import BitWriter, BitReader, pack_metadata, unpack_metadata


class TestNode:
    """Test de la clase Node."""
    
    def test_leaf_node(self):
        """Test que los nodos hoja se identifican correctamente."""
        node = Node(freq=10, symbol=65)
        assert node.is_leaf() is True
        assert node.symbol == 65
        assert node.freq == 10
    
    def test_internal_node(self):
        """Test que los nodos internos se identifican correctamente."""
        left = Node(freq=5, symbol=65)
        right = Node(freq=10, symbol=66)
        node = Node(freq=15, left=left, right=right)
        assert node.is_leaf() is False
        assert node.symbol is None


class TestBitIO:
    """Test de las clases BitWriter y BitReader."""
    
    def test_write_read_single_bit(self):
        """Test de escritura y lectura de un solo bit."""
        writer = BitWriter()
        writer.write_bit(1)
        writer.flush()
        data = writer.get_bytes()
        
        reader = BitReader(data)
        bit = reader.read_bit()
        assert bit == 1
    
    def test_write_read_multiple_bits(self):
        """Test de escritura y lectura de múltiples bits."""
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
        """Test de escritura y lectura de bytes."""
        writer = BitWriter()
        test_bytes = b'Hello, World!'
        writer.write_bytes(test_bytes)
        data = writer.get_bytes()
        
        reader = BitReader(data)
        read_bytes = reader.read_bytes(len(test_bytes))
        assert read_bytes == test_bytes


class TestMetadata:
    """Test de la metadata."""
    
    def test_pack_unpack_metadata(self):
        """Test de empaquetado y desempaquetado de la metadata."""
        freqs = {65: 10, 66: 20, 67: 30}
        packed = pack_metadata(freqs)
        
        reader = BitReader(packed)
        unpacked, _ = unpack_metadata(reader)
        
        assert unpacked == freqs
    
    def test_empty_metadata(self):
        """Test de empaquetado de una tabla de frecuencias vacía."""
        freqs = {}
        packed = pack_metadata(freqs)
        assert len(packed) == 2  # Just the count


class TestHuffmanCoder:
    """Test de la clase HuffmanCoder."""
    
    def test_build_frequency_table(self):
        """Test de construcción de la tabla de frecuencias."""
        data = b'ABRACADABRA'
        freqs = build_frequency_table(data)
        
        assert freqs[ord('A')] == 5
        assert freqs[ord('B')] == 2
        assert freqs[ord('R')] == 2
        assert freqs[ord('C')] == 1
        assert freqs[ord('D')] == 1
    
    def test_build_tree(self):
        """Test de construcción del árbol de Huffman."""
        coder = HuffmanCoder()
        freqs = {65: 5, 66: 2, 67: 1}
        tree = coder.build_tree_from_freq(freqs)
        
        assert tree is not None
        assert tree.freq == 8
        assert tree.is_leaf() is False
    
    def test_tree_to_codes(self):
        """Test de generación de códigos desde el árbol."""  
        coder = HuffmanCoder()
        freqs = {65: 5, 66: 2, 67: 1}
        tree = coder.build_tree_from_freq(freqs)
        codes = coder.tree_to_codes(tree)
        
        assert len(codes) == 3
        assert all(isinstance(code, str) for code in codes.values())
        assert all(set(code).issubset({'0', '1'}) for code in codes.values())
    
    def test_entropy_calculation(self):
        """Test de cálculo de entropía de Shannon."""
        coder = HuffmanCoder()
        freqs = {0: 1, 1: 1, 2: 1, 3: 1}
        entropy = coder.entropy_from_freq(freqs)
        assert 1.9 < entropy < 2.1
        
        freqs = {0: 100}
        entropy = coder.entropy_from_freq(freqs)
        assert entropy == 0.0
    
    def test_compress_decompress_basic(self):
        """Test de compresión y descompresión básica."""
        coder = HuffmanCoder()
        original = b'Hello, World! This is a test message.'
        
        compressed, meta = coder.compress_bytes(original)
        decompressed = coder.decompress_bytes(compressed)
        
        assert decompressed == original
    
    def test_compress_decompress_repeated_chars(self):
        """Test de compresión y descompresión con datos repetitivos."""
        coder = HuffmanCoder()
        original = b'AAAAAAAAAA BBBB CC D'
        
        compressed, meta = coder.compress_bytes(original)
        decompressed = coder.decompress_bytes(compressed)
        
        assert decompressed == original
    
    def test_compress_decompress_single_char(self):
        """Test compresión y descompresión con un solo carácter repetido."""  
        coder = HuffmanCoder()
        original = b'AAAAAAAAAA'
        
        compressed, meta = coder.compress_bytes(original)
        decompressed = coder.decompress_bytes(compressed)
        
        assert decompressed == original
    
    def test_compress_decompress_binary(self):
        """Test de compresión y descompresión con datos binarios."""    
        coder = HuffmanCoder()
        original = bytes(range(256))
        
        compressed, meta = coder.compress_bytes(original)
        decompressed = coder.decompress_bytes(compressed)
        
        assert decompressed == original
    
    def test_compress_empty_raises_error(self):
        """Test que al comprimir datos vacíos sale un error."""  
        coder = HuffmanCoder()
        with pytest.raises(ValueError, match="Cannot compress empty data"):
            coder.compress_bytes(b'')
    
    def test_decompress_empty_raises_error(self):
        """Test que al descomprimir datos vacíos sale un error."""
        coder = HuffmanCoder()
        with pytest.raises(ValueError, match="Cannot decompress empty data"):
            coder.decompress_bytes(b'')
    
    def test_decompress_invalid_data(self):
        """Test que al descomprimir datos inválidos sale un error."""  
        coder = HuffmanCoder()
        with pytest.raises(ValueError):
            coder.decompress_bytes(b'invalid data')
    
    def test_tree_to_dict(self):
        """Test de convertir el árbol a un diccionario."""
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
    """Test de casos extremos y escenarios especiales."""
    
    def test_unicode_text(self):
        """Test de compresión y descompresión con texto Unicode."""
        coder = HuffmanCoder()
        original = 'Hola, mundo! 🌍'.encode('utf-8')
        
        compressed, meta = coder.compress_bytes(original)
        decompressed = coder.decompress_bytes(compressed)
        
        assert decompressed == original
        assert decompressed.decode('utf-8') == 'Hola, mundo! 🌍'
    
    def test_large_data(self):
        """Test con datos grandes."""
        coder = HuffmanCoder()
        # Create 1MB of somewhat random but compressible data
        original = (b'ABCD' * 10000 + b'XYZ' * 5000 + b'123' * 3000)
        
        compressed, meta = coder.compress_bytes(original)
        decompressed = coder.decompress_bytes(compressed)
        
        assert decompressed == original
    
    def test_compression_ratio(self):
        """Test que la compresión reduce el tamaño para datos repetitivos."""
        coder = HuffmanCoder()
        original = b'A' * 1000 + b'B' * 100 + b'C' * 10
        
        compressed, meta = coder.compress_bytes(original)
        
        # Should achieve significant compression
        ratio = len(compressed) / len(original)
        assert ratio < 0.5  # At least 50% compression


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
