#include <librealsense2/rs.hpp> // Include RealSense Cross Platform API


int main(int argc, char * argv[]) try {
	rs2::pipeline p;
	p.start();
	while (true) {
		rs2::frameset frames = p.wait_for_frames();
		rs2::depth_frame depth = frames.get_depth_frame();
		float width = depth.get_width();
        float height = depth.get_height();
		
		float dist_to_center = depth.get_distance(width / 2, height / 2)
		std::cout << "the camera is facing an object " << dist_to_center << " meters away \r"
}