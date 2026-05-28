import threading
import time
from datetime import datetime
from queue import Queue, Empty
import uuid
import traceback

class AnalysisQueueManager:
    def __init__(self, max_workers=10):
        self.max_workers = max_workers
        self.task_queue = Queue()
        self.results = {}
        self.completed_count = 0
        self.total_tasks = 0
        self.lock = threading.Lock()
        self.workers = []
        self.running = False
        print(f"🚀 Queue manager initialized with {max_workers} workers")
        
    def start(self):
        """Start worker threads"""
        self.running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, args=(i,))
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
        print(f"✅ Started {len(self.workers)} worker threads")
        
    def stop(self):
        """Stop all workers"""
        self.running = False
        print("🛑 Stopping queue manager...")
        
    def add_batch(self, batch_id, files, analyzer_func):
        """
        Add a batch of files for analysis
        files: list of dict with 'path' and 'name'
        """
        with self.lock:
            self.total_tasks += len(files)
            self.results[batch_id] = {
                'status': 'processing',
                'total': len(files),
                'completed': 0,
                'failed': 0,
                'files': {},
                'start_time': datetime.now().isoformat()
            }
            print(f"📦 Added batch {batch_id[:8]} with {len(files)} files")
            
        # Add each file to queue
        for file_info in files:
            self.task_queue.put({
                'batch_id': batch_id,
                'file_path': file_info['path'],
                'file_name': file_info['name'],
                'analyzer_func': analyzer_func,
                'file_index': file_info.get('index', 0)
            })
            
        return batch_id
    
    def _worker_loop(self, worker_id):
        """Worker thread function"""
        print(f"👷 Worker {worker_id} started")
        
        while self.running:
            try:
                # Get task from queue with timeout
                task = self.task_queue.get(timeout=1)
                
                # Process the file
                try:
                    # Generate unique analysis ID for this file
                    file_analysis_id = str(uuid.uuid4())
                    
                    # Update status
                    with self.lock:
                        if task['batch_id'] in self.results:
                            self.results[task['batch_id']]['files'][task['file_name']] = {
                                'status': 'analyzing',
                                'analysis_id': file_analysis_id,
                                'start_time': datetime.now().isoformat()
                            }
                    
                    print(f"🔍 Worker {worker_id} analyzing: {task['file_name']}")
                    
                    # Run analysis
                    result = task['analyzer_func'](task['file_path'], file_analysis_id)
                    
                    # Store result
                    with self.lock:
                        if task['batch_id'] in self.results:
                            self.results[task['batch_id']]['files'][task['file_name']].update({
                                'status': 'completed',
                                'result': result,
                                'completed_at': datetime.now().isoformat()
                            })
                            self.results[task['batch_id']]['completed'] += 1
                            self.completed_count += 1
                            
                    print(f"✅ Worker {worker_id} completed: {task['file_name']}")
                            
                except Exception as e:
                    print(f"❌ Worker {worker_id} failed for {task['file_name']}: {e}")
                    traceback.print_exc()
                    
                    with self.lock:
                        if task['batch_id'] in self.results:
                            self.results[task['batch_id']]['files'][task['file_name']] = {
                                'status': 'failed',
                                'error': str(e),
                                'error_time': datetime.now().isoformat()
                            }
                            self.results[task['batch_id']]['failed'] += 1
                
                finally:
                    self.task_queue.task_done()
                    
            except Empty:
                # No tasks, just continue
                pass
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
                time.sleep(1)
        
        print(f"👋 Worker {worker_id} stopped")
    
    def get_batch_status(self, batch_id):
        """Get status of a batch"""
        with self.lock:
            if batch_id in self.results:
                status = self.results[batch_id].copy()
                # Calculate progress percentage
                if status['total'] > 0:
                    completed = status.get('completed', 0)
                    failed = status.get('failed', 0)
                    status['progress'] = int((completed + failed) * 100 / status['total'])
                    status['remaining'] = status['total'] - completed - failed
                    
                    if completed + failed >= status['total']:
                        status['status'] = 'completed'
                return status
        return None
    
    def get_batch_results(self, batch_id):
        """Get complete results for a batch"""
        with self.lock:
            if batch_id in self.results:
                return self.results[batch_id].copy()
        return None
    
    def cleanup_batch(self, batch_id):
        """Remove batch from memory"""
        with self.lock:
            if batch_id in self.results:
                del self.results[batch_id]
                print(f"🧹 Cleaned up batch {batch_id[:8]}")
    
    def get_queue_stats(self):
        """Get queue statistics"""
        with self.lock:
            return {
                'queue_size': self.task_queue.qsize(),
                'total_tasks': self.total_tasks,
                'completed': self.completed_count,
                'active_batches': len(self.results)
            }