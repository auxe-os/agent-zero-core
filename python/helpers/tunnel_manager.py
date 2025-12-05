from flaredantic import FlareConfig, ServeoConfig, ServeoTunnel
from python.helpers.cloudflare_tunnel import CloudflareTunnel
import threading


# Singleton to manage the tunnel instance
class TunnelManager:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def __init__(self):
        self.tunnel = None
        self.tunnel_url = None
        self.is_running = False
        self.provider = None

    def start_tunnel(self, port=80, provider="serveo"):
        """Start a new tunnel or return the existing one's URL"""
        if self.is_running and self.tunnel_url:
            return self.tunnel_url

        self.provider = provider

        try:
            # Start tunnel in a separate thread to avoid blocking
            def run_tunnel():
                try:
                    if self.provider == "cloudflared":
                        # Use internal CloudflareTunnel helper instead of flaredantic's cloudflared support
                        self.tunnel = CloudflareTunnel(port)
                    else:  # Default to serveo
                        config = ServeoConfig(port=port) # type: ignore
                        self.tunnel = ServeoTunnel(config)

                    self.tunnel.start()
                    self.tunnel_url = self.tunnel.tunnel_url
                    self.is_running = True
                except Exception as e:
                    print(f"Error in tunnel thread: {str(e)}")

            tunnel_thread = threading.Thread(target=run_tunnel)
            tunnel_thread.daemon = True
            tunnel_thread.start()

            # Wait for tunnel to start (max 15 seconds instead of 5)
            for _ in range(150):  # Increased from 50 to 150 iterations
                # If TunnelManager already has a URL, we're done
                if self.tunnel_url:
                    break

                # For providers like CloudflareTunnel, the URL is populated
                # asynchronously on the tunnel instance itself; pick it up
                # and mirror it into TunnelManager when available.
                if self.tunnel is not None:
                    tunnel_url = getattr(self.tunnel, "tunnel_url", None)
                    if tunnel_url:
                        self.tunnel_url = tunnel_url
                        self.is_running = True
                        break

                import time

                time.sleep(0.1)

            return self.tunnel_url
        except Exception as e:
            print(f"Error starting tunnel: {str(e)}")
            return None

    def stop_tunnel(self):
        """Stop the running tunnel"""
        if self.tunnel and self.is_running:
            try:
                self.tunnel.stop()
                self.is_running = False
                self.tunnel_url = None
                self.provider = None
                return True
            except Exception:
                return False
        return False

    def get_tunnel_url(self):
        """Get the current tunnel URL if available"""
        return self.tunnel_url if self.is_running else None
