class IPWebcamAdapter:
    """
    Adapter for Android IP Webcam app.
    host and port are always dynamic — never hardcoded.
    Supports: RTSP/H264, HTTP MJPEG, HTTP snapshot.
    """

    def __init__(self, host: str, port: int = 8080):
        self.host = host
        self.port = port

    def get_base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def get_rtsp_h264_url(self) -> str:
        return f"rtsp://{self.host}:{self.port}/h264.sdp"

    def get_snapshot_url(self) -> str:
        return f"http://{self.host}:{self.port}/shot.jpg"

    def get_mjpeg_url(self) -> str:
        return f"http://{self.host}:{self.port}/video"
