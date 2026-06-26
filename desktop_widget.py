import tkinter as tk
import json
import urllib.request
import threading
import time
import sys

class DesktopTelemetryWidget:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GPU Nexus Telemetry Widget")
        
        # Dimensions
        width = 260
        height = 160
        
        # Frameless window and always-on-top
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        # Position in bottom-right corner by default
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - width - 40
        y = screen_height - height - 80
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Theme colors
        self.bg_color = "#080A18"
        self.border_color = "#00E5FF"
        self.text_muted = "#94A3B8"
        self.cyan = "#00E5FF"
        self.purple = "#A855F7"
        self.green = "#10B981"
        self.red = "#EF4444"
        self.orange = "#F59E0B"
        
        # Outer Border
        self.root.config(bg=self.border_color)
        
        # Inner Frame
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Header / Title Bar (for dragging)
        self.header_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.header_frame.pack(fill=tk.X, padx=10, pady=(8, 4))
        
        # Live status dot + title
        self.status_dot = tk.Label(self.header_frame, text="●", fg=self.cyan, bg=self.bg_color, font=("Courier", 12, "bold"))
        self.status_dot.pack(side=tk.LEFT)
        
        self.title_label = tk.Label(self.header_frame, text="LIVE POWER STREAM", fg=self.cyan, bg=self.bg_color, font=("Helvetica", 9, "bold"))
        self.title_label.pack(side=tk.LEFT, padx=4)
        
        # Close Button
        self.close_btn = tk.Label(self.header_frame, text="✕", fg=self.text_muted, bg=self.bg_color, font=("Helvetica", 9, "bold"), cursor="hand2")
        self.close_btn.pack(side=tk.RIGHT)
        self.close_btn.bind("<Button-1>", lambda e: self.root.destroy())
        self.close_btn.bind("<Enter>", lambda e: self.close_btn.config(fg=self.red))
        self.close_btn.bind("<Leave>", lambda e: self.close_btn.config(fg=self.text_muted))
        
        # Divider
        divider = tk.Frame(self.main_frame, height=1, bg="rgba(255,255,255,0.08)", bd=0)
        divider.pack(fill=tk.X, padx=10, pady=(2, 8))
        
        # Content Rows
        self.metrics = {}
        self.add_metric_row("Cluster Total:", "1,820 W", self.cyan, "float-power")
        self.add_metric_row("Grid State:", "OFF-PEAK", self.green, "float-grid")
        self.add_metric_row("Savings:", "$6.00 USD", self.purple, "float-savings")
        self.add_metric_row("Efficiency:", "89.0%", self.orange, "float-efficiency")
        
        # Make window draggable
        for widget in [self.main_frame, self.header_frame, self.title_label, self.status_dot]:
            widget.bind("<Button-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.drag)
            
        # State for dragging
        self.drag_x = 0
        self.drag_y = 0
        
        # Active flag
        self.active = True
        
        # Start API polling thread
        self.thread = threading.Thread(target=self.poll_api, daemon=True)
        self.thread.start()
        
    def add_metric_row(self, label_text, value_text, value_color, key):
        row = tk.Frame(self.main_frame, bg=self.bg_color)
        row.pack(fill=tk.X, padx=12, pady=3)
        
        lbl = tk.Label(row, text=label_text, fg=self.text_muted, bg=self.bg_color, font=("Helvetica", 9, "medium"))
        lbl.pack(side=tk.LEFT)
        
        val = tk.Label(row, text=value_text, fg=value_color, bg=self.bg_color, font=("Helvetica", 10, "bold"))
        val.pack(side=tk.RIGHT)
        
        self.metrics[key] = val
        
        # Bind drag events to content rows too
        for w in [row, lbl, val]:
            w.bind("<Button-1>", self.start_drag)
            w.bind("<B1-Motion>", self.drag)
            
    def start_drag(self, event):
        self.drag_x = event.x
        self.drag_y = event.y
        
    def drag(self, event):
        x = self.root.winfo_x() + event.x - self.drag_x
        y = self.root.winfo_y() + event.y - self.drag_y
        self.root.geometry(f"+{x}+{y}")
        
    def poll_api(self):
        while self.active:
            try:
                # 1. Fetch Power Data
                req = urllib.request.Request("http://127.0.0.1:8000/api/power")
                with urllib.request.urlopen(req, timeout=1.5) as response:
                    power_data = json.loads(response.read().decode())
                    
                # 2. Fetch Batching Data
                req_batch = urllib.request.Request("http://127.0.0.1:8000/api/batching")
                with urllib.request.urlopen(req_batch, timeout=1.5) as response:
                    batch_data = json.loads(response.read().decode())
                
                # Update UI in main thread safely
                self.root.after(0, self.update_ui, power_data, batch_data)
                
            except Exception as e:
                # API Offline - set status indicator to red
                self.root.after(0, self.set_offline)
                
            time.sleep(2.0)
            
    def update_ui(self, power_data, batch_data):
        try:
            # Active status dot pulse color
            self.status_dot.config(fg=self.cyan)
            
            # Update values
            total_w = power_data.get("total_power_w", 1820)
            is_peak = power_data.get("price_info", {}).get("is_peak_hour", False)
            rate = power_data.get("price_info", {}).get("price_per_kwh", 0.12)
            saved_usd = power_data.get("savings_info", {}).get("saved_cost_usd", 6.00)
            efficiency = batch_data.get("gpu_efficiency_score", 89.0)
            
            self.metrics["float-power"].config(text=f"{total_w:,.0f} W")
            
            grid_text = f"PEAK (${rate:.2f})" if is_peak else f"OFF-PEAK (${rate:.2f})"
            grid_color = self.red if is_peak else self.green
            self.metrics["float-grid"].config(text=grid_text, fg=grid_color)
            
            self.metrics["float-savings"].config(text=f"${saved_usd:.2f} USD")
            self.metrics["float-efficiency"].config(text=f"{efficiency:.1f}%")
            
        except Exception:
            pass
            
    def set_offline(self):
        try:
            self.status_dot.config(fg=self.red)
            self.metrics["float-power"].config(text="OFFLINE")
            self.metrics["float-grid"].config(text="DISCONNECTED", fg=self.red)
        except Exception:
            pass

    def run(self):
        try:
            self.root.mainloop()
        finally:
            self.active = False

if __name__ == "__main__":
    app = DesktopTelemetryWidget()
    app.run()
