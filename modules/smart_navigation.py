"""
Smart Navigation module for AI Blind Assistant.
Provides intelligent path planning and obstacle avoidance.
"""

import numpy as np
import cv2
import logging
from typing import List, Tuple, Optional
import time

logger = logging.getLogger(__name__)

class SmartNavigation:
    def __init__(self, camera_handler, gps_handler):
        self.camera = camera_handler
        self.gps = gps_handler
        self.map_data = {}  # Store explored areas
        self.current_path = []
        self.obstacle_map = np.zeros((100, 100), dtype=np.uint8)  # Simple grid map

    def detect_obstacles(self, frame) -> List[Tuple[int, int, int, int]]:
        """Detect obstacles using depth estimation and computer vision."""
        try:
            # Convert to grayscale for edge detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # Edge detection using Canny
            edges = cv2.Canny(blurred, 50, 150)

            # Find contours (potential obstacles)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            obstacles = []
            height, width = frame.shape[:2]

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 500:  # Filter small contours
                    x, y, w, h = cv2.boundingRect(contour)
                    # Calculate distance based on bounding box size (simple approximation)
                    distance = self._estimate_distance(w, h, height, width)
                    obstacles.append((x, y, w, h, distance))

            return obstacles
        except Exception as e:
            logger.error(f"Obstacle detection failed: {e}")
            return []

    def _estimate_distance(self, w: int, h: int, frame_height: int, frame_width: int) -> float:
        """Estimate distance based on object size in frame."""
        # Simple distance estimation based on object size
        # This is a rough approximation - real implementation would use stereo vision
        size_ratio = (w * h) / (frame_width * frame_height)
        if size_ratio > 0.5:
            return 1.0  # Very close
        elif size_ratio > 0.2:
            return 2.0  # Close
        elif size_ratio > 0.05:
            return 5.0  # Medium distance
        else:
            return 10.0  # Far

    def plan_path(self, start: Tuple[float, float], goal: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Plan a safe path from start to goal avoiding obstacles."""
        # Simple A* path planning implementation
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        def get_neighbors(pos):
            neighbors = []
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nx, ny = pos[0] + dx, pos[1] + dy
                if 0 <= nx < 100 and 0 <= ny < 100 and self.obstacle_map[nx, ny] == 0:
                    neighbors.append((nx, ny))
            return neighbors

        # Convert GPS coordinates to grid coordinates (simplified)
        start_grid = (int(start[0] * 10) % 100, int(start[1] * 10) % 100)
        goal_grid = (int(goal[0] * 10) % 100, int(goal[1] * 10) % 100)

        frontier = [(0, start_grid)]
        came_from = {start_grid: None}
        cost_so_far = {start_grid: 0}

        while frontier:
            current_cost, current = frontier.pop(0)

            if current == goal_grid:
                break

            for neighbor in get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + heuristic(goal_grid, neighbor)
                    frontier.append((priority, neighbor))
                    frontier.sort()
                    came_from[neighbor] = current

        # Reconstruct path
        if goal_grid not in came_from:
            return []  # No path found

        path = []
        current = goal_grid
        while current != start_grid:
            path.append(current)
            current = came_from[current]
        path.append(start_grid)
        path.reverse()

        # Convert back to GPS-like coordinates
        gps_path = [(x / 10.0, y / 10.0) for x, y in path]
        return gps_path

    def get_navigation_instruction(self, current_pos: Tuple[float, float],
                                 next_pos: Tuple[float, float]) -> str:
        """Generate turn-by-turn navigation instructions."""
        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]

        angle = np.arctan2(dy, dx) * 180 / np.pi

        if -45 <= angle < 45:
            direction = "straight ahead"
        elif 45 <= angle < 135:
            direction = "to the right"
        elif -135 <= angle < -45:
            direction = "to the left"
        else:
            direction = "turn around"

        distance = np.sqrt(dx**2 + dy**2)
        if distance < 0.1:
            return "You have arrived at your destination"
        elif distance < 0.5:
            return f"Continue {direction} for {distance:.1f} meters"
        else:
            return f"Go {direction}"

    def update_obstacle_map(self, obstacles: List[Tuple[int, int, int, int, float]]):
        """Update the obstacle map with detected obstacles."""
        # Convert camera coordinates to map coordinates (simplified)
        for x, y, w, h, distance in obstacles:
            if distance < 3.0:  # Only mark close obstacles
                map_x = int(x / 10) % 100
                map_y = int(y / 10) % 100
                self.obstacle_map[map_x, map_y] = 255

    def find_safe_spot(self, current_pos: Tuple[float, float]) -> Optional[Tuple[float, float]]:
        """Find the nearest safe spot away from obstacles."""
        current_grid = (int(current_pos[0] * 10) % 100, int(current_pos[1] * 10) % 100)

        # Search in expanding circles for safe spots
        for radius in range(1, 10):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) + abs(dy) == radius:
                        nx, ny = current_grid[0] + dx, current_grid[1] + dy
                        if (0 <= nx < 100 and 0 <= ny < 100 and
                            self.obstacle_map[nx, ny] == 0):
                            return (nx / 10.0, ny / 10.0)
        return None

    def get_environment_context(self) -> str:
        """Provide context about the current environment."""
        try:
            frame = self.camera.capture_frame()
            if frame is not None:
                obstacles = self.detect_obstacles(frame)
                self.update_obstacle_map(obstacles)

                if not obstacles:
                    return "The path ahead appears clear."
                elif len(obstacles) == 1:
                    _, _, _, _, distance = obstacles[0]
                    return f"There is an obstacle approximately {distance:.1f} meters ahead."
                else:
                    close_obstacles = [obs for obs in obstacles if obs[4] < 3.0]
                    return f"There are {len(close_obstacles)} obstacles within 3 meters."
            else:
                return "Unable to assess the environment."
        except Exception as e:
            logger.error(f"Environment context failed: {e}")
            return "Unable to assess the environment."
