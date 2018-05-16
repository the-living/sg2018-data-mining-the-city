from helpers import CameraTrackExtractor


images_bin = "/path/to/sparse_aligned/images.bin"
output_path = "/path/to/align_ply"

tracker = CameraTrackExtractor(images_bin)

tracker.export(output_path)
