import time
import random
import statistics
import matplotlib.pyplot as plt
import numpy as np

class TailCompressedTree:
    def __init__(self, name, use_tail_opt=False):
        self.name = name
        self.use_tail_opt = use_tail_opt
        self.index_nodes = {} # Mô phỏng các nút chỉ mục

    def _compress_tail(self, key, prev_key):
        """Logic nén đuôi: Tìm điểm khác biệt nhỏ nhất giữa 2 khóa"""
        if not prev_key:
            return key[:1] # Nếu là khóa đầu, chỉ lấy 1 ký tự
        
        for i in range(min(len(key), len(prev_key))):
            if key[i] != prev_key[i]:
                return key[:i+1] # Cắt bỏ phần đuôi dư thừa sau điểm khác biệt
        return key

    def insert(self, keys):
        sorted_keys = sorted(keys)
        prev_k = ""
        for k in sorted_keys:
            if self.use_tail_opt:
                # Chỉ lưu phần đầu tối thiểu cần thiết để phân biệt
                short_key = self._compress_tail(k, prev_k)
                self.index_nodes[short_key] = k
                prev_k = k
            else:
                self.index_nodes[k] = k

    def search(self, keys):
        # Mô phỏng việc tìm kiếm trên các khóa đã nén đuôi
        for k in keys:
            for short_k in self.index_nodes:
                if k >= short_k:
                    continue # Logic điều hướng trong cây
        return True

    def search_range(self, all_sorted, min_indices):
        for idx in min_indices:
            _ = all_sorted[idx : idx + 100]
        return True

# --- 2. Chạy Benchmark ---

def run_tail_benchmark():
    key_numbers = 100000
    iterations = 3
    
    # Tạo dữ liệu chuỗi dài để thấy rõ hiệu quả cắt đuôi
    all_data = [f"com.example.system.user_account_id_{i:08d}_profile_data" for i in range(key_numbers)]
    random.shuffle(all_data)
    
    values = all_data[20000:]
    values_warmup = all_data[:20000]
    all_sorted = sorted(all_data)
    min_indices = [random.randint(0, 70000) for _ in range(100)]

    structures = [
        TailCompressedTree("Btree-Standard", use_tail_opt=False),
        TailCompressedTree("Btree-Tail-Opt", use_tail_opt=True)
    ]
    
    results = {s.name: {'insert': [], 'search': [], 'range': []} for s in structures}

    for i in range(iterations):
        print(f"Lần lặp {i+1}...")
        for tree in structures:
            # Measure Insert
            t0 = time.perf_counter()
            tree.insert(values)
            results[tree.name]['insert'].append(time.perf_counter() - t0)
            
            # Measure Search
            t0 = time.perf_counter()
            tree.search(values[:5000]) # Tìm 5k mẫu
            results[tree.name]['search'].append(time.perf_counter() - t0)
            
            # Measure Range
            t0 = time.perf_counter()
            tree.search_range(all_sorted, min_indices)
            results[tree.name]['range'].append(time.perf_counter() - t0)

    return results, 80000

# --- 3. Trực quan hóa ---

def plot_tail_results(results, n_ins):
    names = list(results.keys())
    ops = ['insert', 'search', 'range']
    data_points = {op: [] for op in ops}
    
    for name in names:
        for op in ops:
            avg_t = statistics.mean(results[name][op])
            count = 100 if op == 'range' else (n_ins if op == 'insert' else 5000)
            data_points[op].append(count / avg_t)

    x = np.arange(len(ops))
    width = 0.35
    fig, ax = plt.subplots(figsize=(12, 7))
    colors = ['#95a5a6', '#27ae60'] # Xám và Xanh lá (Tail)

    for i, name in enumerate(names):
        vals = [data_points[op][i] for op in ops]
        rects = ax.bar(x + i*width, vals, width, label=name, color=colors[i], edgecolor='black')
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height/1e6:.2f}M', xy=(rect.get_x() + rect.get_width()/2, height),
                        xytext=(0, 3), textcoords="offset points", ha='center', fontweight='bold')

    ax.set_ylabel('Ops/sec (Triệu Ops)')
    ax.set_title('HIỆU NĂNG TAIL COMPRESSION (NÉN ĐUÔI) TRONG B-TREE')
    ax.set_xticks(x + width/2)
    ax.set_xticklabels([o.upper() for o in ops])
    ax.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    res, n = run_tail_benchmark()
    plot_tail_results(res, n)