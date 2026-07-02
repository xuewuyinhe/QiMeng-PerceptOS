import chromadb
import os
import hashlib
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
from tqdm import tqdm
import time
import threading

class UltraLargeFileProcessor:
    def __init__(self, persist_directory: str = "./chroma_db_optimized"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection("knowledge-documents")
        self._lock = threading.Lock() 
        
    def process_large_file(self, file_path: str, max_workers: int = None):
        if not os.path.exists(file_path):
            print(f"no file: {file_path}")
            return
        
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        print(f"📁 Processing large file: {filename}")
        print(f"📊 File size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
        print(f"🔢 Estimated characters: {file_size} chars")
        
        start_time = time.time()
        
     
        if max_workers is None:
            max_workers = min(multiprocessing.cpu_count(), 25)
        
        print(f"🖥️  Using {max_workers} threads for parallel processing")
        
       
        print("⏳ Splitting large file...")
        temp_files = self._split_large_file(file_path, max_workers)
        
        print(f"📂 File split into {len(temp_files)} parts")
        
        total_chunks = 0
   
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_part = {
                executor.submit(self._process_file_part_thread_safe, temp_file, i, filename): i 
                for i, temp_file in enumerate(temp_files)
            }
            
        with tqdm(total=len(temp_files), desc="Processing file parts") as pbar:
                for future in as_completed(future_to_part):
                    part_index = future_to_part[future]
                    
                    try:
                        chunks_data = future.result()
                        if chunks_data:
                            chunks_count = self._add_chunks_batch_thread_safe(chunks_data)
                            total_chunks += chunks_count
                            pbar.set_description(f"Part {part_index+1} -> {chunks_count} chunks")
                        else:
                            pbar.set_description(f"Part {part_index+1} no content")
                    except Exception as e:
                        print(f"❌ Failed to process file part {part_index}: {e}")
                    
                    pbar.update(1)
        
       
        self._cleanup_temp_files(temp_files)
        
        processing_time = time.time() - start_time
        minutes = int(processing_time // 60)
        seconds = int(processing_time % 60)
        
        print(f"\n🎉 Large file processing completed!")
        print(f"✅ Total processing time: {minutes} min {seconds} sec")
        print(f"✅ Number of document chunks generated: {total_chunks}")
        print(f"✅ Average processing speed: {file_size/processing_time/1024/1024:.2f} MB/sec")
    
    def _split_large_file(self, file_path: str, num_parts: int) -> List[str]:     
        temp_files = []
        
      
        print("正在计算文件行数...")
        with open(file_path, 'r', encoding='utf-8') as f:
            total_lines = sum(1 for _ in f)
        
        lines_per_part = total_lines // num_parts + 1
        print(f"总行数: {total_lines}, 每部分行数: {lines_per_part}")
        
        with open(file_path, 'r', encoding='utf-8') as source_file:
            for i in range(num_parts):
                temp_filename = f"temp_part_{i}_{os.path.basename(file_path)}"
                temp_filepath = os.path.join(os.path.dirname(file_path), temp_filename)
                
                with open(temp_filepath, 'w', encoding='utf-8') as temp_file:
                    lines_written = 0
                    for line in source_file:
                        temp_file.write(line)
                        lines_written += 1
                        if lines_written >= lines_per_part:
                            break
                
       
                file_size = os.path.getsize(temp_filepath)
                if file_size > 0:
                    temp_files.append(temp_filepath)
                 
                else:
                    os.remove(temp_filepath)
        
        return temp_files
    
    def _process_file_part_thread_safe(self, file_path: str, part_index: int, original_filename: str) -> List[Dict[str, Any]]:
        try:          
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                
                if not content:
                    return []
                
                domain = original_filename.replace(".txt", "").split('_')[-1] if '_' in original_filename else original_filename.replace(".txt", "")
                
                
                file_size = len(content)
                chunk_size = self._calculate_chunk_size_for_large_file(file_size)
                
                print(f"File part size: {file_size} chars, using chunk size: {chunk_size}")
                
             
                chunks = self._split_text_into_chunks_optimized(content, domain, chunk_size=chunk_size)
                
                if not chunks:
                    return []
                
             
                chunks_data = []
                for i, chunk in enumerate(chunks):
                    if len(chunk.strip()) < 50: 
                        continue
                    
                    chunk_id = f"{domain}_part{part_index}_{i}_{hashlib.md5(chunk.encode()).hexdigest()[:8]}"
                    
                    chunks_data.append({
                        "document": chunk,
                        "metadata": {
                            "domain": domain,
                            "source": "UltraDomain_txt",
                            "chunk_index": i,
                            "part_index": part_index,
                            "file": original_filename,
                            "chunk_size": len(chunk),
                            "file_size": file_size
                        },
                        "id": chunk_id
                    })
                
                print(f"File part {part_index} generated {len(chunks_data)} chunks")
                return chunks_data
                
        except Exception as e:
            print(f"error {file_path}: {e}")
            return []
    
    def _calculate_chunk_size_for_large_file(self, file_size: int) -> int:
        if file_size > 50000000:  # > 50MB
            return 3000
        elif file_size > 20000000:  # 20-50MB
            return 2500
        elif file_size > 5000000:   # 5-20MB
            return 2000
        else:  # < 5MB
            return 1000
    
    def _split_text_into_chunks_optimized(self, text: str, domain: str, chunk_size: int = 2000, overlap: int = 100) -> List[str]:

        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 100]
        
        if not paragraphs:
      
            paragraphs = [line.strip() for line in text.split('\n') if len(line.strip()) > 50]
        
        chunks = []
        current_chunk = ""
        current_length = 0
        
        for paragraph in paragraphs:
            paragraph_length = len(paragraph)
            
           
            if paragraph_length >= chunk_size * 0.8:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                    current_length = 0
                
             
                if paragraph_length > chunk_size:
                    sub_chunks = self._split_long_paragraph(paragraph, chunk_size, overlap)
                    chunks.extend(sub_chunks)
                else:
                    chunks.append(paragraph)
            else:
             
                if current_length + paragraph_length <= chunk_size:
                    if current_chunk:
                        current_chunk += "\n\n" + paragraph
                    else:
                        current_chunk = paragraph
                    current_length += paragraph_length + 2  
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = paragraph
                    current_length = paragraph_length
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _split_long_paragraph(self, paragraph: str, chunk_size: int, overlap: int) -> List[str]:

        sentences = [s.strip() + '.' for s in paragraph.split('.') if s.strip()]
        
        if len(sentences) <= 1:
        
            return self._sliding_window_chunk(paragraph, chunk_size, overlap)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length <= chunk_size:
                current_chunk.append(sentence)
                current_length += sentence_length
            else:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _sliding_window_chunk(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += (chunk_size - overlap)
            
            if start >= text_length:
                break
        
        return chunks
    
    def _add_chunks_batch_thread_safe(self, chunks_data: List[Dict[str, Any]], batch_size: int = 100) -> int:
        if not chunks_data:
            return 0
        
        added_count = 0
        
        
        with self._lock:
            for i in range(0, len(chunks_data), batch_size):
                batch = chunks_data[i:i + batch_size]
                
                try:
                    self.collection.add(
                        documents=[item["document"] for item in batch],
                        metadatas=[item["metadata"] for item in batch],
                        ids=[item["id"] for item in batch]
                    )
                    added_count += len(batch)
                    
                except Exception as e:
                    print(f"批量添加块失败: {e}")
                    # 如果批量添加失败，尝试小批量添加
                    for j in range(0, len(batch), 20):
                        small_batch = batch[j:j+20]
                        try:
                            self.collection.add(
                                documents=[item["document"] for item in small_batch],
                                metadatas=[item["metadata"] for item in small_batch],
                                ids=[item["id"] for item in small_batch]
                            )
                            added_count += len(small_batch)
                        except Exception as small_e:
                            print(f"小批量添加失败: {small_e}")
                            continue
        
        return added_count
    
    def _cleanup_temp_files(self, temp_files: List[str]):    
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    print(f"file clean done: {os.path.basename(temp_file)}")
            except Exception as e:
                print(f"error {temp_file}: {e}")

    def query_knowledge(self, question: str, n_results: int = 3, domain_filter: str = None):    
        where_filter = None
        if domain_filter:
            where_filter = {"domain": domain_filter}
        
        try:
            results = self.collection.query(
                query_texts=[question],
                n_results=n_results,
                where=where_filter
            )
            return results
        except Exception as e:
            print(f"false: {e}")
            return {"documents": [[]], "metadatas": [[]]}


import time
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import statistics

if __name__ == "__main__":
    processor = UltraLargeFileProcessor()

  
    large_file_path = "./UltraDomain_txt1/art.txt"  # Replace with the actual file path

   # if os.path.exists(large_file_path):
    if  true:
        print("processing...")
        # processor.process_large_file(large_file_path, max_workers=multiprocessing.cpu_count())   #Build a vector database. Please download directly from Hugging Face here
        
        print("\n" + "="*60)
        print("testing")
        print("="*60)

     
        test_questions = [
            "What is the main content of this large file?",
            "What are the key topics discussed?",
            "Why did Leyla use a pseudonym?",
            "Summarize the main points",
            "What is the author's perspective?",
            "Key findings in the document",
            "Main arguments presented",
            "Important details mentioned"
        ]


      
        CONCURRENT_THREADS = 50  
        REQUESTS_PER_THREAD = 40 
        TOTAL_REQUESTS = CONCURRENT_THREADS * REQUESTS_PER_THREAD

      
        result_queue = queue.Queue()
        latency_list = []

       
        def query_worker(worker_id, questions):
            for i in range(REQUESTS_PER_THREAD):
                question = questions[(worker_id + i) % len(questions)]
                start_time = time.time()
                
                try:
                
                    results = processor.query_knowledge(question, n_results=2)
                    end_time = time.time()
                    latency = (end_time - start_time) * 1000  
                    
                    result_queue.put({
                        'worker_id': worker_id,
                        'request_id': i,
                        'latency': latency,
                        'success': True,
                        'question': question
                    })
                    latency_list.append(latency)
                    
                except Exception as e:
                    end_time = time.time()
                    latency = (end_time - start_time) * 1000
                    result_queue.put({
                        'worker_id': worker_id,
                        'request_id': i,
                        'latency': latency,
                        'success': False,
                        'error': str(e)
                    })


        print(f"Testing...")
        print(f"Concurrent threads: {CONCURRENT_THREADS}")
        print(f"Requests per thread: {REQUESTS_PER_THREAD}")
        print(f"Total requests: {TOTAL_REQUESTS}")
        print("-" * 40)

        start_test_time = time.time()

      
        with ThreadPoolExecutor(max_workers=CONCURRENT_THREADS) as executor:           
            futures = []
            for i in range(CONCURRENT_THREADS):
                future = executor.submit(query_worker, i, test_questions)
                futures.append(future)

        end_test_time = time.time()
        total_test_time = end_test_time - start_test_time

       
        results = []
        success_count = 0
        failed_count = 0

        while not result_queue.empty():
            result = result_queue.get()
            results.append(result)
            if result['success']:
                success_count += 1
            else:
                failed_count += 1

        
        qps = success_count / total_test_time  # 
        avg_latency = statistics.mean(latency_list) if latency_list else 0
        min_latency = min(latency_list) if latency_list else 0
        max_latency = max(latency_list) if latency_list else 0
        
      
        if latency_list:
            sorted_latencies = sorted(latency_list)
            p50 = sorted_latencies[int(len(sorted_latencies) * 0.5)]
            p90 = sorted_latencies[int(len(sorted_latencies) * 0.9)]
            p95 = sorted_latencies[int(len(sorted_latencies) * 0.95)]
            p99 = sorted_latencies[int(len(sorted_latencies) * 0.99)]
        else:
            p50 = p90 = p95 = p99 = 0

     
        print("\n" + "="*60)
        print("Stress Test Results")
        print("="*60)
        print(f"Total test time: {total_test_time:.2f} seconds")
        print(f"Total requests: {TOTAL_REQUESTS}")
        print(f"Successful requests: {success_count}")
        print(f"Failed requests: {failed_count}")
        print(f"Success rate: {(success_count/TOTAL_REQUESTS)*100:.2f}%")
        print(f"QPS (Queries Per Second): {qps:.2f}")
        print(f"Throughput: {qps:.2f} queries/sec")
        print("\nLatency statistics (milliseconds):")
        print(f"Average latency: {avg_latency:.2f}ms")
        print(f"Min latency: {min_latency:.2f}ms")
        print(f"Max latency: {max_latency:.2f}ms")
        print(f"P50 (Median): {p50:.2f}ms")
        print(f"P90: {p90:.2f}ms")
        print(f"P95: {p95:.2f}ms")
        print(f"P99: {p99:.2f}ms")

       
        print("\n" + "-"*40)
        print("First 5 query examples:")
        print("-"*40)
        for i, result in enumerate(results[:5]):
            if result['success']:
                print(f"{i+1}. question: {result['question'][:50]}...")
                print(f"   latency: {result['latency']:.2f}ms")
                print(f"   thread: {result['worker_id']}")
                print()

    else:
        print(f"no file: {large_file_path}")


   
