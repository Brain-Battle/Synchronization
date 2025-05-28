from camera_display import display_video_blocking

from rich.console import Console
console = Console()

display_video_blocking("udp://0.0.0.0:8554", console.print)
# for hero 7
# display_video_blocking("udp://10.5.5.9:8554", console.print)