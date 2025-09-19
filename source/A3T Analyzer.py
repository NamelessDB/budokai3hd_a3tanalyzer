import struct
from pathlib import Path

class A3TAnalyzer:
    def __init__(self):
        self.texture_types = {
            b'\x00\x00\x00\x21': "[T]",   # Compressed texture
            b'\x80\x00\x00\x01': "[S]",   # Simple texture
            b'\x00\x00\x00\x01': "[B]",   # Basic texture
            b'\x00\x00\x00\x22': "[T2]",  # Possible new variant(Unknown variant Maybe?
        }
    
    def hex_to_int_be(self, hti):
        """convert bytes to integer (big-endian)"""
        return int.from_bytes(hti, byteorder='big')
    
    def offset_fix_be(self, hti):
        """adjust offset for 4 bytes"""
        return b'\x00\x00' + hti
    
    def analyze_file(self, file_path):
        """analyze file and display information"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"Error: File {file_path} does not exist")
            return False
        
        try:
            with open(file_path, "rb") as f:
                # Read header
                f.seek(16)
                tex_am = self.hex_to_int_be(f.read(4))
                index_loc = self.hex_to_int_be(f.read(4))
                
                print(f"\n[+] Found {tex_am} textures\n")
                
                # Pre-calculate all texture offsets
                texture_offsets = []
                for num in range(tex_am):
                    f.seek(index_loc + (4 * num))
                    tex_offset = self.hex_to_int_be(f.read(4))
                    texture_offsets.append(tex_offset)
                
                # Process each texture
                for num, tex_offset in enumerate(texture_offsets):
                    self.process_texture(f, num, tex_offset)
                    
        except Exception as e:
            print(f"error while processing file: {str(e)}")
            return False
        
        print("\n[+] analysis finished")
        return True
    
    def process_texture(self, file_obj, num, tex_offset):
        """process individual texture and display info"""
        try:
            # Go to texture block
            file_obj.seek(tex_offset + 4)
            t_type = file_obj.read(4)
            t_type_str = self.texture_types.get(t_type, "[?]")
            
            # Read dimensions
            width_offset = file_obj.tell() + 8
            file_obj.seek(width_offset)
            width = self.hex_to_int_be(self.offset_fix_be(file_obj.read(2)))
            
            height_offset = file_obj.tell()
            height = self.hex_to_int_be(self.offset_fix_be(file_obj.read(2)))
            
            data_offset_offset = file_obj.tell()
            data_offset = self.hex_to_int_be(file_obj.read(4))
            
            # Calculate positions
            palette_pos = data_offset
            bitmap_pos = data_offset + 128
            
            # Show information
            print(f"\nTexture {num+1} {t_type_str}")
            print(f"  Texture offset: 0x{tex_offset:X}")
            print(f"  Width: {width} (at offset 0x{width_offset:X})")
            print(f"  Height: {height} (at offset 0x{height_offset:X})")
            print(f"  Data offset: 0x{data_offset:X} (file offset 0x{data_offset_offset:X})")
            print(f"  Palette offset: 0x{palette_pos:X}")
            print(f"  Bitmap offset: 0x{bitmap_pos:X}")
            
            # Attempt to calculate bitmap size
            file_obj.seek(bitmap_pos)
            bmp_size = width * height
            current_pos = file_obj.tell()
            file_obj.seek(0, 2)
            file_size = file_obj.tell()
            file_obj.seek(current_pos)
            available_data = file_size - bitmap_pos
            if available_data < bmp_size:
                print(f"  Warning: Only {available_data} bytes available, but {bmp_size} expected")
            
        except Exception as e:
            print(f"Error processing texture {num+1}: {str(e)}")


def main():
    print("=== A3T Analyzer (read-only mode) ===")
    print("Thanks to Nexus the Modder and Credits for his analysis code on A3T textures")
    print("Drag and drop your A3T or BIN file here, or type the path manually")
    
    analyzer = A3TAnalyzer()
    
    while True:
        try:
            file_path = input("").strip().replace("\"", "")
            
            if not file_path:
                print("Please enter a valid path")
                continue
                
            if file_path.lower() in ('exit', 'quit'):
                break
                
            if not (file_path.endswith(".a3t") or file_path.endswith(".bin")):
                print("File must have .a3t or .bin extension")
                continue
                
            analyzer.analyze_file(file_path)
                
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
