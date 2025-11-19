import os

def create_binary_file(filename, size_bytes):
    with open(filename, 'wb') as f:
        chunk_size = 1024 * 64
        
        remaining = size_bytes
        while remaining > 0:
            current_chunk = min(chunk_size, remaining)
            data = os.urandom(current_chunk)
            f.write(data)
            remaining -= current_chunk
    
    print(f"Create file successfully")

create_binary_file("test_file.bin", 1024 * 1024)