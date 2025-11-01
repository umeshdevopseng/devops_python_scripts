#!/usr/bin/env python3
"""
Asynchronous Operations for DevOps - Script 15
Why: Async programming improves performance for I/O-heavy DevOps tasks
"""

import asyncio
import aiohttp
import aiofiles
import time
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

async def async_health_check(session: aiohttp.ClientSession, url: str) -> Dict:
    """
    Asynchronous health check for a single endpoint
    Why: Check multiple services concurrently instead of sequentially
    """
    start_time = time.time()
    
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
            response_time = time.time() - start_time
            
            return {
                'url': url,
                'status_code': response.status,
                'response_time': response_time,
                'healthy': response.status == 200
            }
    except Exception as e:
        return {
            'url': url,
            'error': str(e),
            'response_time': time.time() - start_time,
            'healthy': False
        }

async def batch_health_checks(urls: List[str]) -> List[Dict]:
    """
    Check multiple endpoints concurrently
    Why: Monitor many services simultaneously for faster feedback
    """
    async with aiohttp.ClientSession() as session:
        # Create tasks for all health checks
        tasks = [async_health_check(session, url) for url in urls]
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions that occurred
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    'error': str(result),
                    'healthy': False
                })
            else:
                processed_results.append(result)
        
        return processed_results

async def async_file_processor(file_path: str, process_func) -> Any:
    """
    Process file asynchronously
    Why: Handle large files without blocking the main thread
    """
    async with aiofiles.open(file_path, 'r') as file:
        content = await file.read()
        
        # Process content in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor, process_func, content)
        
        return result

async def async_log_aggregator(log_files: List[str]) -> Dict[str, int]:
    """
    Aggregate logs from multiple files concurrently
    Why: Process multiple log files simultaneously for faster analysis
    """
    async def count_errors_in_file(file_path: str) -> int:
        """Count error lines in a single file"""
        try:
            async with aiofiles.open(file_path, 'r') as file:
                error_count = 0
                async for line in file:
                    if 'ERROR' in line.upper():
                        error_count += 1
                return error_count
        except FileNotFoundError:
            return 0
    
    # Process all files concurrently
    tasks = [count_errors_in_file(file_path) for file_path in log_files]
    error_counts = await asyncio.gather(*tasks)
    
    # Combine results
    return {
        file_path: count 
        for file_path, count in zip(log_files, error_counts)
    }

class AsyncTaskQueue:
    """
    Asynchronous task queue for background processing
    Why: Handle background tasks without blocking main application
    """
    
    def __init__(self, max_workers: int = 5):
        self.queue = asyncio.Queue()
        self.max_workers = max_workers
        self.workers = []
        self.running = False
    
    async def add_task(self, coro):
        """Add coroutine to the task queue"""
        await self.queue.put(coro)
    
    async def worker(self, worker_id: int):
        """Worker coroutine to process tasks"""
        while self.running:
            try:
                # Get task from queue with timeout
                task = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                
                print(f"Worker {worker_id} processing task")
                await task  # Execute the task
                
                self.queue.task_done()
                
            except asyncio.TimeoutError:
                continue  # No tasks available, continue loop
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
    
    async def start(self):
        """Start the task queue workers"""
        self.running = True
        self.workers = [
            asyncio.create_task(self.worker(i)) 
            for i in range(self.max_workers)
        ]
    
    async def stop(self):
        """Stop the task queue workers"""
        self.running = False
        
        # Wait for all workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
    
    async def wait_for_completion(self):
        """Wait for all queued tasks to complete"""
        await self.queue.join()

async def async_deployment_monitor(services: List[str], check_interval: int = 30):
    """
    Monitor deployment status asynchronously
    Why: Continuously monitor multiple services without blocking
    """
    async def monitor_service(service_name: str):
        """Monitor a single service"""
        while True:
            try:
                # Simulate service health check
                await asyncio.sleep(1)  # Simulate API call
                
                # In real implementation, this would be an actual health check
                health_status = "healthy"  # or "unhealthy"
                
                print(f"{service_name}: {health_status} at {time.strftime('%H:%M:%S')}")
                
                await asyncio.sleep(check_interval)
                
            except asyncio.CancelledError:
                print(f"Monitoring stopped for {service_name}")
                break
            except Exception as e:
                print(f"Error monitoring {service_name}: {e}")
                await asyncio.sleep(check_interval)
    
    # Start monitoring all services concurrently
    tasks = [asyncio.create_task(monitor_service(service)) for service in services]
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("Stopping deployment monitoring...")
        for task in tasks:
            task.cancel()
        
        # Wait for tasks to complete cancellation
        await asyncio.gather(*tasks, return_exceptions=True)

async def async_backup_multiple_databases(db_configs: List[Dict]) -> List[Dict]:
    """
    Backup multiple databases concurrently
    Why: Reduce total backup time by running backups in parallel
    """
    async def backup_database(config: Dict) -> Dict:
        """Backup a single database"""
        start_time = time.time()
        
        try:
            # Simulate database backup (in real implementation, use subprocess)
            await asyncio.sleep(2)  # Simulate backup time
            
            backup_time = time.time() - start_time
            
            return {
                'database': config['name'],
                'status': 'success',
                'backup_time': backup_time,
                'backup_file': f"/backups/{config['name']}_{int(time.time())}.sql"
            }
            
        except Exception as e:
            return {
                'database': config['name'],
                'status': 'failed',
                'error': str(e),
                'backup_time': time.time() - start_time
            }
    
    # Backup all databases concurrently
    tasks = [backup_database(config) for config in db_configs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return [r for r in results if not isinstance(r, Exception)]

async def rate_limited_api_calls(urls: List[str], rate_limit: int = 5):
    """
    Make API calls with rate limiting
    Why: Respect API rate limits while maximizing throughput
    """
    semaphore = asyncio.Semaphore(rate_limit)  # Limit concurrent requests
    
    async def limited_request(session: aiohttp.ClientSession, url: str):
        """Make rate-limited request"""
        async with semaphore:  # Acquire semaphore before making request
            try:
                async with session.get(url) as response:
                    return {
                        'url': url,
                        'status': response.status,
                        'success': True
                    }
            except Exception as e:
                return {
                    'url': url,
                    'error': str(e),
                    'success': False
                }
    
    async with aiohttp.ClientSession() as session:
        tasks = [limited_request(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        return results

if __name__ == "__main__":
    # Example 1: Batch health checks
    async def test_health_checks():
        urls = [
            'http://httpbin.org/status/200',
            'http://httpbin.org/status/404',
            'http://httpbin.org/delay/2'
        ]
        
        start_time = time.time()
        results = await batch_health_checks(urls)
        total_time = time.time() - start_time
        
        print(f"Health checks completed in {total_time:.2f} seconds")
        for result in results:
            print(f"  {result['url']}: {'✓' if result['healthy'] else '✗'}")
    
    # Example 2: Task queue
    async def test_task_queue():
        queue = AsyncTaskQueue(max_workers=3)
        await queue.start()
        
        # Add some tasks
        for i in range(5):
            await queue.add_task(asyncio.sleep(1))  # Simple sleep tasks
        
        await queue.wait_for_completion()
        await queue.stop()
        print("Task queue processing completed")
    
    # Example 3: Database backups
    async def test_database_backups():
        db_configs = [
            {'name': 'users_db', 'host': 'db1.example.com'},
            {'name': 'orders_db', 'host': 'db2.example.com'},
            {'name': 'analytics_db', 'host': 'db3.example.com'}
        ]
        
        results = await async_backup_multiple_databases(db_configs)
        print(f"Completed {len(results)} database backups")
        for result in results:
            print(f"  {result['database']}: {result['status']}")
    
    # Run examples
    print("Running async operations examples...")
    
    asyncio.run(test_health_checks())
    asyncio.run(test_task_queue())
    asyncio.run(test_database_backups())
    
    print("Async operations script ready!")