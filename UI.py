from flask import Flask, render_template, request, jsonify
import pymysql
import sys
import matplotlib.pyplot as plt
import time
import numpy as np

app = Flask(__name__)
sys.setrecursionlimit(10000)

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='coklat_db',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    results_iterative = []
    results_recursive = []
    target_score = None
    analysis_data = {}
    performance_data = []
    message = None
    
    if request.method == 'POST':
        target_score = request.form.get('score', type=float)
        connection = get_db_connection()
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM coklat ORDER BY id")
                all_data = cursor.fetchall()
                
                step_size = max(1, len(all_data) // 50)
                
                for i in range(step_size, len(all_data) + 1, step_size):
                    current_data = all_data[:i]
                    
                    start_time = time.perf_counter()
                    iterative_search(current_data, target_score)
                    iterative_time = time.perf_counter() - start_time
                    
                    start_time = time.perf_counter()
                    recursive_search(current_data, target_score)
                    recursive_time = time.perf_counter() - start_time
                    
                    performance_data.append({
                        'ukuran_data': i,
                        'waktu_iteratif': iterative_time,
                        'waktu_rekursif': recursive_time
                    })
                
                # Simpan hasil pencarian final
                results_iterative = iterative_search(all_data, target_score)
                if not results_iterative:
                    message = f"Data dengan skor {target_score} tidak ditemukan"
                
                results_recursive = recursive_search(all_data, target_score)
                
                # Simpan data analisis jika ada hasil
                if results_iterative:
                    analysis_data = {
                        'iterative_time': performance_data[-1]['waktu_iteratif'],
                        'recursive_time': performance_data[-1]['waktu_rekursif'],
                        'total_data': len(all_data),
                        'performance_data': performance_data
                    }
                    
                    plt.figure(figsize=(12, 6))
                    plt.plot([d['ukuran_data'] for d in performance_data],
                            [d['waktu_iteratif'] for d in performance_data],
                            'b-', label='Pencarian Iteratif', linewidth=2)
                    plt.plot([d['ukuran_data'] for d in performance_data],
                            [d['waktu_rekursif'] for d in performance_data],
                            'r-', label='Pencarian Rekursif', linewidth=2)
                    plt.grid(True, linestyle='--', alpha=0.7)
                    plt.xlabel('Ukuran Data')
                    plt.ylabel('Waktu (detik)')
                    plt.title('Perbandingan Performa Algoritma Pencarian')
                    plt.legend()
                    plt.tight_layout()
                    plt.savefig('static/performance_plot.png', dpi=300, bbox_inches='tight')
                    plt.close()
                
        finally:
            connection.close()
    
    return render_template('index.html',
                         results_iterative=results_iterative,
                         results_recursive=results_recursive,
                         target_score=target_score,
                         analysis_data=analysis_data,
                         message=message)

def iterative_search(data, score):
    result = []
    for i in range(len(data)):
        if data[i]['skor'] == score:
            result.append(data[i])
    if len(result) == 0:
        return None
    return result

def recursive_search(data, score, index=0, result=None):
    if result is None:
        result = []
    if index >= len(data):
        return None if len(result) == 0 else result
    if data[index]['skor'] == score:
        result.append(data[index])
    return recursive_search(data, score, index + 1, result)


if __name__ == '__main__':
    app.run(debug=True)