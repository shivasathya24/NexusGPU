import time
import random
import uuid
from typing import Dict, List, Any

class InferenceBatcher:
    def __init__(self):
        # Settings
        self.max_batch_size = 32
        self.max_queue_delay_ms = 10.0
        self.arrival_rate_rps = 240.0
        
        # State
        self.queue: List[Dict[str, Any]] = []
        self.completed_batches: List[Dict[str, Any]] = []
        self.last_batch_time = time.time()
        
        # Performance cache
        self.avg_latency_ms = 22.4
        self.ttft_ms = 8.5
        self.throughput_tokens_sec = 8240.0
        self.gpu_efficiency_score = 88.5
        
        # Pre-populate batch history
        for _ in range(15):
            self._create_mock_batch()

    def _create_mock_batch(self) -> Dict[str, Any]:
        batch_id = str(uuid.uuid4())[:8]
        actual_size = random.randint(int(self.max_batch_size * 0.5), self.max_batch_size)
        actual_size = max(actual_size, 4)
        
        # Dynamic metrics depending on batch size
        # Larger batch sizes increase throughput but increase latency
        ratio = actual_size / 32.0
        throughput = 4000.0 + (ratio * 6000.0) + random.uniform(-400, 400)
        avg_latency = 12.0 + (ratio * 15.0) + random.uniform(-1.5, 1.5)
        ttft = 5.0 + (ratio * 4.0) + random.uniform(-0.5, 0.5)
        
        # GPU efficiency: peaks around size 32 due to tensor core alignments
        if actual_size >= 32:
            efficiency = 95.0 - (actual_size - 32) * 0.2
        else:
            efficiency = 60.0 + (actual_size / 32.0) * 35.0
            
        efficiency = min(max(efficiency + random.uniform(-2.0, 2.0), 40.0), 99.0)
        
        tokens = actual_size * random.choice([256, 512, 1024])
        
        batch = {
            "id": f"batch_{batch_id}",
            "size": actual_size,
            "tokens": tokens,
            "throughput_tps": round(throughput, 1),
            "latency_ms": round(avg_latency, 1),
            "ttft_ms": round(ttft, 1),
            "efficiency": round(efficiency, 1),
            "timestamp": time.time() - random.uniform(1, 300)
        }
        self.completed_batches.append(batch)
        if len(self.completed_batches) > 30:
            self.completed_batches.pop(0)
            
        return batch

    def update_simulation(self) -> Dict[str, Any]:
        """
        Updates queues and forms new batches dynamically based on rates.
        """
        now = time.time()
        elapsed = now - self.last_batch_time
        self.last_batch_time = now
        
        # Simulate incoming request arrivals in queue
        num_incoming = int(self.arrival_rate_rps * elapsed)
        # Prevent explosion if elapsed is large
        num_incoming = min(num_incoming, 100)
        
        # Add new requests to queue
        for _ in range(num_incoming):
            req_id = f"req_{str(uuid.uuid4())[:6]}"
            self.queue.append({
                "id": req_id,
                "prompt_tokens": random.choice([128, 256, 512, 1024]),
                "arrival_time": now - random.uniform(0, elapsed)
            })
            
        # Form batches based on max_batch_size and max_queue_delay
        batches_formed = 0
        while len(self.queue) >= self.max_batch_size or (self.queue and (now - self.queue[0]["arrival_time"]) * 1000.0 > self.max_queue_delay_ms):
            # Form batch
            batch_size = min(len(self.queue), self.max_batch_size)
            if batch_size == 0:
                break
                
            # Pop requests from queue
            batch_requests = [self.queue.pop(0) for _ in range(batch_size)]
            
            # Compute real batch metrics
            ratio = batch_size / 32.0
            throughput = 4000.0 + (ratio * 6000.0) + random.uniform(-400, 400)
            avg_latency = 12.0 + (ratio * 15.0) + random.uniform(-1.5, 1.5)
            ttft = 5.0 + (ratio * 4.0) + random.uniform(-0.5, 0.5)
            
            if batch_size >= 32:
                efficiency = 95.0 - (batch_size - 32) * 0.2
            else:
                efficiency = 60.0 + (batch_size / 32.0) * 35.0
            efficiency = min(max(efficiency + random.uniform(-2.0, 2.0), 40.0), 99.0)
            
            tokens = sum([r["prompt_tokens"] for r in batch_requests])
            
            # Save batch
            new_batch = {
                "id": f"batch_{str(uuid.uuid4())[:8]}",
                "size": batch_size,
                "tokens": tokens,
                "throughput_tps": round(throughput, 1),
                "latency_ms": round(avg_latency, 1),
                "ttft_ms": round(ttft, 1),
                "efficiency": round(efficiency, 1),
                "timestamp": now
            }
            self.completed_batches.append(new_batch)
            batches_formed += 1
            
        if len(self.completed_batches) > 30:
            self.completed_batches = self.completed_batches[-30:]
            
        # Calculate moving averages
        if self.completed_batches:
            recent = self.completed_batches[-5:]
            self.throughput_tokens_sec = sum([b["throughput_tps"] for b in recent]) / len(recent)
            self.avg_latency_ms = sum([b["latency_ms"] for b in recent]) / len(recent)
            self.ttft_ms = sum([b["ttft_ms"] for b in recent]) / len(recent)
            self.gpu_efficiency_score = sum([b["efficiency"] for b in recent]) / len(recent)
            
        return {
            "queue_depth": len(self.queue),
            "active_queue": self.queue[:15], # limit returned list length
            "throughput_tokens_sec": round(self.throughput_tokens_sec, 1),
            "avg_latency_ms": round(self.avg_latency_ms, 1),
            "ttft_ms": round(self.ttft_ms, 1),
            "gpu_efficiency_score": round(self.gpu_efficiency_score, 1),
            "completed_batches": self.completed_batches[-10:] # last 10
        }
        
    def configure_batcher(self, max_batch_size: int, delay_ms: float, arrival_rate: float) -> Dict[str, Any]:
        self.max_batch_size = max(min(max_batch_size, 128), 4)
        self.max_queue_delay_ms = max(min(delay_ms, 500.0), 1.0)
        self.arrival_rate_rps = max(min(arrival_rate, 1000.0), 10.0)
        return {
            "status": "success",
            "max_batch_size": self.max_batch_size,
            "max_queue_delay_ms": self.max_queue_delay_ms,
            "arrival_rate_rps": self.arrival_rate_rps
        }

inference_batcher = InferenceBatcher()
