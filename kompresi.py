import heapq 
from collections import Counter 
import math 

# 1. ANALISIS METRIK SEBELUM KOMPRESI
def analisis_sebelum_kompresi(text):
    total_len = len(text) 
    freq = Counter(text) 
    unique_chars = len(freq) 
    ascii_bits = total_len * 8 
    
    # Menghitung jumlah bit minimal per karakter (Fixed-Length) berdasarkan jumlah karakter unik
    bits_per_fixed = (
        math.ceil(math.log2(unique_chars)) if unique_chars > 1 else 1
    ) 
    fixed_bits = total_len * bits_per_fixed 

    print("\n" + "=" * 70)
    print("ANALISIS METRIK SEBELUM KOMPRESI")
    print("=" * 70)
    print(f"1. String Input               : '{text}'")
    print(f"2. Total Panjang String       : {total_len} karakter")
    print(
        f"3. Jumlah Karakter Unik       : {unique_chars} karakter"
        f" ({', '.join(sorted(freq.keys()))})"
    )
    print(f"4. Ukuran Standard ASCII (8-bit): {ascii_bits} bit ({total_len} byte)")
    print(
        f"5. Ukuran Fixed-Length Minimal: {fixed_bits} bit ({bits_per_fixed}"
        " bit/karakter)"
    )
    print("-" * 70)
    print("Tabel Distribusi Frekuensi & Biner ASCII Karakter:")
    print(
        f"{'Karakter':<10} | {'Frekuensi':<10} | {'Probabilitas (%)':<18} | "
        f"{'Biner ASCII (8-bit)'}"
    )
    print("-" * 70)
    
    # Looping karakter yang diurutkan dari frekuensi tertinggi ke terendah
    for char, f in sorted(freq.items(), key=lambda x: x[1], reverse=True): 
        prob = (f / total_len) * 100 
        ascii_code = f"{ord(char):08b} (Desimal {ord(char)})" 
        print(f"'{char}'{' ':<7} | {f:<10} | {prob:<17.2f}% | {ascii_code}") 
    
    print("=" * 70 + "\n")
    return ascii_bits, fixed_bits 

# 2. IMPLEMENTASI HUFFMAN CODING
class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char 
        self.freq = freq 
        self.left = None 
        self.right = None 

    def __lt__(self, other):
        if self.freq == other.freq: 
            return (self.char or "") < (other.char or "") 
        return self.freq < other.freq 

def run_huffman(text):
    freq = Counter(text) 
    heap = [HuffmanNode(char, f) for char, f in freq.items()] 
    heapq.heapify(heap) 

    while len(heap) > 1: 
        left = heapq.heappop(heap) 
        right = heapq.heappop(heap) 
        merged = HuffmanNode(None, left.freq + right.freq) 
        merged.left, merged.right = left, right 
        heapq.heappush(heap, merged) 

    root = heap[0] 
    codes = {} 

    def build_codes(node, current_code=""): 
        if node is None: 
            return
        if node.char is not None: 
            codes[node.char] = current_code 
            return
        build_codes(node.left, current_code + "0") 
        build_codes(node.right, current_code + "1") 

    build_codes(root) 
    encoded = "".join(codes[char] for char in text) 

    # Menampilkan hasil kompresi Huffman
    print("\n--- HASIL KOMPRESI HUFFMAN CODING ---")
    print("Tabel Kode Huffman :", codes)
    print("Bitstream Terkompresi:", encoded)
    print(f"Total Ukuran Bit     : {len(encoded)} bit")
    print(
        "Penghematan vs ASCII :"
        f" {((len(text)*8 - len(encoded)) / (len(text)*8)) * 100:.2f}%\n"
    )
    return codes, encoded 

# 3. IMPLEMENTASI SHANNON-FANO CODING
def run_shannon_fano(text):
    freq = Counter(text) 
    sorted_items = sorted(freq.items(), key=lambda x: x[1], reverse=True) 
    codes = {char: "" for char, _ in sorted_items} 

    def divide(items, prefix=""): 
        if len(items) <= 1: 
            if len(items) == 1: 
                codes[items[0][0]] = prefix 
            return
        
        total = sum(f for _, f in items) 
        acc = 0 
        split_idx = 0 
        min_diff = float("inf") 
        
        for i in range(len(items)): 
            acc += items[i][1] 
            diff = abs(2 * acc - total) 
            if diff < min_diff: 
                min_diff = diff 
                split_idx = i + 1 
                
        left = items[:split_idx] 
        right = items[split_idx:] 
        divide(left, prefix + "0") 
        divide(right, prefix + "1") 

    divide(sorted_items) 
    encoded = "".join(codes[char] for char in text) 

    # Menampilkan hasil kompresi Shannon-Fano
    print("\n--- HASIL KOMPRESI SHANNON-FANO CODING ---")
    print("Tabel Kode Shannon-Fano:", codes)
    print("Bitstream Terkompresi   :", encoded)
    print(f"Total Ukuran Bit        : {len(encoded)} bit")
    print(
        "Penghematan vs ASCII   :"
        f" {((len(text)*8 - len(encoded)) / (len(text)*8)) * 100:.2f}%\n"
    )
    return codes, encoded

# 4. IMPLEMENTASI LZW COMPRESSION
def run_lzw(text):
    dictionary = {chr(i): i for i in range(256)} 
    dict_size = 256 
    p = "" 
    compressed_codes = [] 
    steps = [] 

    for c in text: 
        pc = p + c 
        if pc in dictionary: 
            p = pc 
        else: 
            compressed_codes.append(dictionary[p]) 
            steps.append((p, dictionary[p], pc, dict_size))
            dictionary[pc] = dict_size 
            dict_size += 1 
            p = c 

    if p: 
        compressed_codes.append(dictionary[p]) 
        steps.append((p, dictionary[p], "-", "-")) 

    # Menampilkan hasil kompresi LZW
    print("\n--- HASIL KOMPRESI LZW (LEMPEL-ZIV-WELCH) ---")
    print("Output Kode Angka LZW:", compressed_codes)
    print("\nLangkah Pembentukan Kamus Dinamis LZW:")
    print(
        f"{'Input (P)':<10} | {'Output Code':<12} | {'Kamus Baru (P+C)':<18} | {'Indeks Baru':<12}"
    )
    print("-" * 60)
    for p_val, out_code, new_str, new_code in steps: 
        print(
            f"{p_val:<10} | {out_code:<12} | {new_str:<18} |"
            f" {new_code:<12}"
        )
    print(f"\nJumlah Simbol Awal : {len(text)} karakter")
    print(f"Jumlah Kode Output : {len(compressed_codes)} kode angka\n")
    return compressed_codes

def main():
    print("=" * 70)
    print("   PROGRAM KOMPRESI DATA (SEBELUM VS SESUDAH KOMPRESI)   ")
    print("=" * 70)

    # Meminta input pengguna
    user_str = input(
        "Masukkan kata/string [Tekan Enter untuk 'dont say no']: "
    ).strip()
    if not user_str: 
        user_str = "dont say no" 

    ascii_bits, fixed_bits = analisis_sebelum_kompresi(user_str) 
    while True: 
        print("--- PILIH ALGORITMA KOMPRESI ---")
        print("1. Huffman Coding")
        print("2. Shannon-Fano Coding")
        print("3. LZW (Lempel-Ziv-Welch) Compression")
        print("4. Jalankan Semua Algoritma & Perbandingan Lengkap")
        print("5. Analisis Ulang String Sebelum Kompresi")
        print("6. Keluar")

        choice = input("Pilihan Anda (1-6): ").strip() 

        if choice == "1":
            run_huffman(user_str) 
        elif choice == "2":
            run_shannon_fano(user_str) 
        elif choice == "3":
            run_lzw(user_str) 
        elif choice == "4":
            h_codes, h_stream = run_huffman(user_str)
            sf_codes, sf_stream = run_shannon_fano(user_str)
            lzw_codes = run_lzw(user_str)

            print("=" * 70)
            print("        RINGKASAN PERBANDINGAN SEBELUM VS SESUDAH KOMPRESI        ")
            print("=" * 70)
            print(f" String Input                    : '{user_str}'")
            print(
                f" Ukuran Asli ASCII (8-bit)       : {ascii_bits} bit"
                f" ({len(user_str)} byte)"
            )
            print(f" Ukuran Fixed-Length (Minimal)   : {fixed_bits} bit")
            print("-" * 70)
            print(
                f" [1] Huffman Coding             : {len(h_stream)} bit (Hemat"
                f" {((ascii_bits-len(h_stream))/ascii_bits)*100:.2f}%)"
            )
            print(
                f" [2] Shannon-Fano Coding         : {len(sf_stream)} bit (Hemat"
                f" {((ascii_bits-len(sf_stream))/ascii_bits)*100:.2f}%)"
            )
            print(
                f" [3] LZW Compression             : {len(lzw_codes)} kode angka"
                f" (dari {len(user_str)} karakter)"
            )
            print("=" * 70 + "\n")
        elif choice == "5":
            analisis_sebelum_kompresi(user_str) 
        elif choice == "6":
            print("Program selesai.")
            break 
        else:
            print("Pilihan tidak valid, silakan coba lagi!\n")

if __name__ == "__main__":
    main()