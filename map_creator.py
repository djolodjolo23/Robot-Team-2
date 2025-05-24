import pygame
import sys

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CONTROLS_HEIGHT = 100 # Space for buttons and input fields
MAP_DISPLAY_HEIGHT = SCREEN_HEIGHT - CONTROLS_HEIGHT
TOOLBAR_WIDTH = 150 # Space for tools on the side
CANVAS_WIDTH = SCREEN_WIDTH - TOOLBAR_WIDTH

BG_COLOR = (200, 200, 200)
MAP_BG_COLOR = (255, 255, 255)
OBSTACLE_COLOR = (50, 50, 50)
SEAT_COLOR = (0, 150, 0)
GRID_COLOR = (220, 220, 220)
TEXT_COLOR = (0, 0, 0)
BUTTON_COLOR = (100, 100, 200)
BUTTON_TEXT_COLOR = (255, 255, 255)

# --- Helper Classes (assuming these are defined elsewhere as in your example) ---
class Seat:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Seat({self.id}, {self.x}, {self.y})"

class Obstacle:
    def __init__(self, id, x, y, width, height):
        self.id = id # Add an id for easier tracking if needed
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)

    def __repr__(self):
        return f"Obstacle({self.x}, {self.y}, {self.width}, {self.height})"

# --- Main Application Class ---
class MapCreator:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Map Creator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 24)

        self.map_width = 20 # Default map dimensions
        self.map_height = 15
        self.cell_size = 20 # For grid display, adjust dynamically

        self.obstacles = []
        self.seats = []
        self.obstacle_id_counter = 0
        self.seat_id_counter = 0

        self.drawing_obstacle = False
        self.obstacle_start_pos = None

        self.current_tool = "obstacle" # "obstacle", "seat"
        self.input_active_width = False
        self.input_active_height = False
        self.map_width_text = str(self.map_width)
        self.map_height_text = str(self.map_height)

        # --- UI Elements ---
        self.map_canvas_rect = pygame.Rect(0, 0, CANVAS_WIDTH, MAP_DISPLAY_HEIGHT) # Where the map is drawn
        self.toolbar_rect = pygame.Rect(CANVAS_WIDTH, 0, TOOLBAR_WIDTH, SCREEN_HEIGHT)
        self.controls_rect = pygame.Rect(0, MAP_DISPLAY_HEIGHT, SCREEN_WIDTH, CONTROLS_HEIGHT) # Below map

        # Buttons (rect, text, action)
        self.buttons = {
            "obstacle_tool": {"rect": pygame.Rect(CANVAS_WIDTH + 10, 50, 130, 40), "text": "Obstacle", "action": lambda: self.set_tool("obstacle")},
            "seat_tool": {"rect": pygame.Rect(CANVAS_WIDTH + 10, 100, 130, 40), "text": "Seat", "action": lambda: self.set_tool("seat")},
            "generate_code": {"rect": pygame.Rect(CANVAS_WIDTH + 10, SCREEN_HEIGHT - 60, 130, 40), "text": "Generate", "action": self.generate_code_popup},
            "clear_all": {"rect": pygame.Rect(CANVAS_WIDTH + 10, SCREEN_HEIGHT - 110, 130, 40), "text": "Clear All", "action": self.clear_all}
        }
        self.map_width_input_rect = pygame.Rect(CANVAS_WIDTH + 10, 180, 130, 30)
        self.map_height_input_rect = pygame.Rect(CANVAS_WIDTH + 10, 230, 130, 30)

    def set_tool(self, tool_name):
        self.current_tool = tool_name
        print(f"Tool set to: {self.current_tool}")

    def clear_all(self):
        self.obstacles = []
        self.seats = []
        self.obstacle_id_counter = 0
        self.seat_id_counter = 0
        print("Cleared all elements.")

    def calculate_cell_size(self):
        """Calculate cell size to fit map in canvas"""
        if self.map_width == 0 or self.map_height == 0:
            self.cell_size = 1
            return
        cell_w = self.map_canvas_rect.width // self.map_width
        cell_h = self.map_canvas_rect.height // self.map_height
        self.cell_size = min(cell_w, cell_h)
        if self.cell_size == 0: self.cell_size = 1 # Avoid division by zero if map is too large for canvas

    def to_map_coords(self, screen_x, screen_y):
        """Convert screen coordinates to map grid coordinates"""
        if self.cell_size == 0: return None, None
        map_x = screen_x // self.cell_size
        map_y = screen_y // self.cell_size
        if 0 <= map_x < self.map_width and 0 <= map_y < self.map_height:
            return map_x, map_y
        return None, None

    def to_screen_coords(self, map_x, map_y):
        """Convert map grid coordinates to screen coordinates"""
        return map_x * self.cell_size, map_y * self.cell_size

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # --- Text Input for Map Dimensions ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.map_width_input_rect.collidepoint(event.pos):
                    self.input_active_width = True
                    self.input_active_height = False
                elif self.map_height_input_rect.collidepoint(event.pos):
                    self.input_active_height = True
                    self.input_active_width = False
                else:
                    self.input_active_width = False
                    self.input_active_height = False

                # Update map dimensions if text changed
                if not self.input_active_width and self.map_width_text:
                    try:
                        new_width = int(self.map_width_text)
                        if new_width > 0: self.map_width = new_width
                        else: self.map_width_text = str(self.map_width) # Revert if invalid
                    except ValueError:
                        self.map_width_text = str(self.map_width) # Revert if not int
                if not self.input_active_height and self.map_height_text:
                    try:
                        new_height = int(self.map_height_text)
                        if new_height > 0: self.map_height = new_height
                        else: self.map_height_text = str(self.map_height)
                    except ValueError:
                        self.map_height_text = str(self.map_height)
                self.calculate_cell_size()


            if event.type == pygame.KEYDOWN:
                if self.input_active_width:
                    if event.key == pygame.K_RETURN:
                        self.input_active_width = False
                        try:
                            self.map_width = int(self.map_width_text)
                            if self.map_width <=0: self.map_width = 1 # Min size
                        except ValueError:
                            self.map_width_text = str(self.map_width) # Revert
                        self.calculate_cell_size()
                    elif event.key == pygame.K_BACKSPACE:
                        self.map_width_text = self.map_width_text[:-1]
                    else:
                        self.map_width_text += event.unicode
                elif self.input_active_height:
                    if event.key == pygame.K_RETURN:
                        self.input_active_height = False
                        try:
                            self.map_height = int(self.map_height_text)
                            if self.map_height <= 0: self.map_height = 1 # Min size
                        except ValueError:
                            self.map_height_text = str(self.map_height) # Revert
                        self.calculate_cell_size()
                    elif event.key == pygame.K_BACKSPACE:
                        self.map_height_text = self.map_height_text[:-1]
                    else:
                        self.map_height_text += event.unicode


            # --- Tool Interactions ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Button clicks
                for name, btn in self.buttons.items():
                    if btn["rect"].collidepoint(event.pos):
                        btn["action"]()
                        return # Prioritize button clicks

                # Map canvas clicks
                if self.map_canvas_rect.collidepoint(event.pos):
                    mx, my = self.to_map_coords(event.pos[0], event.pos[1])
                    if mx is not None and my is not None:
                        if self.current_tool == "obstacle":
                            if event.button == 1: # Left click
                                self.drawing_obstacle = True
                                self.obstacle_start_pos = (mx, my)
                        elif self.current_tool == "seat":
                            if event.button == 1: # Left click
                                # Check if seat already exists at this position
                                if not any(s.x == mx and s.y == my for s in self.seats):
                                    self.seats.append(Seat(self.seat_id_counter, mx, my))
                                    self.seat_id_counter += 1
                                    print(f"Added seat at: ({mx}, {my})")
                                else:
                                    print(f"Seat already exists at: ({mx}, {my})")

            if event.type == pygame.MOUSEBUTTONUP:
                if self.current_tool == "obstacle" and self.drawing_obstacle:
                    if event.button == 1: # Left click
                        self.drawing_obstacle = False
                        if self.obstacle_start_pos and self.map_canvas_rect.collidepoint(event.pos):
                            mx_end, my_end = self.to_map_coords(event.pos[0], event.pos[1])
                            if mx_end is not None and my_end is not None:
                                x0, y0 = self.obstacle_start_pos
                                x1, y1 = mx_end, my_end

                                obs_x = min(x0, x1)
                                obs_y = min(y0, y1)
                                obs_w = abs(x0 - x1) + 1
                                obs_h = abs(y0 - y1) + 1

                                if obs_w > 0 and obs_h > 0:
                                    new_obstacle = Obstacle(self.obstacle_id_counter, obs_x, obs_y, obs_w, obs_h)
                                    self.obstacles.append(new_obstacle)
                                    self.obstacle_id_counter += 1
                                    print(f"Added obstacle: x:{obs_x} y:{obs_y} w:{obs_w} h:{obs_h}")
                                self.obstacle_start_pos = None

    def draw_grid(self):
        if self.cell_size <= 1: return # Grid too dense
        for x in range(0, self.map_canvas_rect.width, self.cell_size):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, self.map_canvas_rect.height))
        for y in range(0, self.map_canvas_rect.height, self.cell_size):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (self.map_canvas_rect.width, y))

    def draw_map_elements(self):
        # Draw obstacles
        for obs in self.obstacles:
            screen_x, screen_y = self.to_screen_coords(obs.x, obs.y)
            obs_rect = pygame.Rect(screen_x, screen_y, obs.width * self.cell_size, obs.height * self.cell_size)
            pygame.draw.rect(self.screen, OBSTACLE_COLOR, obs_rect)

        # Draw seats (as small circles)
        seat_radius = max(2, self.cell_size // 4)
        for seat in self.seats:
            screen_x, screen_y = self.to_screen_coords(seat.x, seat.y)
            center_x = screen_x + self.cell_size // 2
            center_y = screen_y + self.cell_size // 2
            pygame.draw.circle(self.screen, SEAT_COLOR, (center_x, center_y), seat_radius)

        # Draw temporary obstacle being drawn
        if self.drawing_obstacle and self.obstacle_start_pos:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.map_canvas_rect.collidepoint(mouse_x, mouse_y):
                current_map_x, current_map_y = self.to_map_coords(mouse_x, mouse_y)
                if current_map_x is not None and current_map_y is not None:
                    start_screen_x, start_screen_y = self.to_screen_coords(self.obstacle_start_pos[0], self.obstacle_start_pos[1])

                    temp_x = min(self.obstacle_start_pos[0], current_map_x)
                    temp_y = min(self.obstacle_start_pos[1], current_map_y)
                    temp_w = abs(self.obstacle_start_pos[0] - current_map_x) + 1
                    temp_h = abs(self.obstacle_start_pos[1] - current_map_y) + 1

                    rect_x, rect_y = self.to_screen_coords(temp_x, temp_y)
                    rect_w = temp_w * self.cell_size
                    rect_h = temp_h * self.cell_size

                    temp_rect_surface = pygame.Surface((rect_w, rect_h), pygame.SRCALPHA)
                    temp_rect_surface.fill((100, 100, 100, 150)) # Semi-transparent gray
                    self.screen.blit(temp_rect_surface, (rect_x, rect_y))


    def draw_ui(self):
        # Toolbar background
        pygame.draw.rect(self.screen, (180, 180, 180), self.toolbar_rect)
        # Controls background
        pygame.draw.rect(self.screen, (150, 150, 150), self.controls_rect)


        # Draw buttons
        for name, btn in self.buttons.items():
            pygame.draw.rect(self.screen, BUTTON_COLOR, btn["rect"])
            text_surf = self.small_font.render(btn["text"], True, BUTTON_TEXT_COLOR)
            text_rect = text_surf.get_rect(center=btn["rect"].center)
            self.screen.blit(text_surf, text_rect)

            if self.current_tool == name.replace("_tool", ""): # Highlight active tool
                 pygame.draw.rect(self.screen, (255,0,0), btn["rect"], 2)


        # --- Draw Input Fields for Map Dimensions ---
        # Width
        pygame.draw.rect(self.screen, (220,220,220) if self.input_active_width else (255,255,255), self.map_width_input_rect)
        pygame.draw.rect(self.screen, TEXT_COLOR, self.map_width_input_rect, 1) # Border
        width_label_surf = self.small_font.render("Map Width:", True, TEXT_COLOR)
        self.screen.blit(width_label_surf, (self.map_width_input_rect.x, self.map_width_input_rect.y - 20))
        width_text_surf = self.small_font.render(self.map_width_text, True, TEXT_COLOR)
        self.screen.blit(width_text_surf, (self.map_width_input_rect.x + 5, self.map_width_input_rect.y + 5))

        # Height
        pygame.draw.rect(self.screen, (220,220,220) if self.input_active_height else (255,255,255), self.map_height_input_rect)
        pygame.draw.rect(self.screen, TEXT_COLOR, self.map_height_input_rect, 1) # Border
        height_label_surf = self.small_font.render("Map Height:", True, TEXT_COLOR)
        self.screen.blit(height_label_surf, (self.map_height_input_rect.x, self.map_height_input_rect.y - 20))
        height_text_surf = self.small_font.render(self.map_height_text, True, TEXT_COLOR)
        self.screen.blit(height_text_surf, (self.map_height_input_rect.x + 5, self.map_height_input_rect.y + 5))

        # Current tool display
        tool_text = self.font.render(f"Tool: {self.current_tool.capitalize()}", True, TEXT_COLOR)
        self.screen.blit(tool_text, (10, MAP_DISPLAY_HEIGHT + 10))

        # Map dimensions display
        dim_text = self.font.render(f"Map: {self.map_width}x{self.map_height}", True, TEXT_COLOR)
        self.screen.blit(dim_text, (10, MAP_DISPLAY_HEIGHT + 40))


    def generate_code_string(self):
        code_lines = []
        seat_vars = []
        for i, seat in enumerate(self.seats):
            var_name = f"seat{i}"
            code_lines.append(f"{var_name} = Seat({seat.id}, {seat.x}, {seat.y})")
            seat_vars.append(var_name)

        obstacle_vars = []
        for i, obs in enumerate(self.obstacles):
            var_name = f"o{i+1}" # As per example o1, o2 ...
            code_lines.append(f"{var_name} = Obstacle({obs.x}, {obs.y}, {obs.width}, {obs.height})")
            obstacle_vars.append(var_name)

        obstacles_list_str = "[" + ", ".join(obstacle_vars) + "]" if obstacle_vars else "[]"
        seats_list_str = "[" + ", ".join(seat_vars) + "]" if seat_vars else "[]"

        code_lines.append(f"\nmap = Map({self.map_width}, {self.map_height}, {obstacles_list_str}, {seats_list_str})")
        return "\n".join(code_lines)

    def generate_code_popup(self):
        generated_code = self.generate_code_string()
        print("\n--- Generated Code ---")
        print(generated_code)
        print("----------------------\n")

        # --- Simple Popup using Pygame (for demonstration) ---
        popup_width = 600
        popup_height = 400
        popup_x = (SCREEN_WIDTH - popup_width) // 2
        popup_y = (SCREEN_HEIGHT - popup_height) // 2
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        popup_surface = pygame.Surface((popup_width, popup_height))
        popup_surface.fill((230, 230, 250)) # Light lavender
        pygame.draw.rect(popup_surface, (50, 50, 50), (0,0, popup_width, popup_height), 3) # Border

        title_surf = self.font.render("Generated Map Code", True, TEXT_COLOR)
        popup_surface.blit(title_surf, (20, 20))

        code_lines = generated_code.split('\n')
        y_offset = 60
        for line in code_lines:
            code_surf = self.small_font.render(line, True, TEXT_COLOR)
            popup_surface.blit(code_surf, (20, y_offset))
            y_offset += 25
            if y_offset > popup_height - 40: # Avoid overflow
                # Could add scrolling here for longer code
                overflow_surf = self.small_font.render("...", True, TEXT_COLOR)
                popup_surface.blit(overflow_surf, (20, y_offset))
                break


        close_button_rect = pygame.Rect(popup_width - 120, popup_height - 50, 100, 30)
        pygame.draw.rect(popup_surface, BUTTON_COLOR, close_button_rect)
        close_text_surf = self.small_font.render("Close", True, BUTTON_TEXT_COLOR)
        close_text_rect = close_text_surf.get_rect(center=close_button_rect.center)
        popup_surface.blit(close_text_surf, close_text_rect)

        running_popup = True
        while running_popup:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Convert mouse pos to be relative to popup surface
                    mouse_x_rel = event.pos[0] - popup_x
                    mouse_y_rel = event.pos[1] - popup_y
                    if close_button_rect.collidepoint(mouse_x_rel, mouse_y_rel):
                        running_popup = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running_popup = False

            self.screen.blit(popup_surface, (popup_x, popup_y))
            pygame.display.flip()
            self.clock.tick(30)


    def run(self):
        self.calculate_cell_size() # Initial calculation
        while True:
            self.handle_input()

            self.screen.fill(BG_COLOR)

            # Map Canvas Area
            map_area_surface = self.screen.subsurface(self.map_canvas_rect)
            map_area_surface.fill(MAP_BG_COLOR)

            self.draw_grid()
            self.draw_map_elements()

            # UI Area
            self.draw_ui() # Draws on the main screen

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == '__main__':
    # Ensure helper classes are defined if they are not in this file
    # For example, you would have:
    # class Seat: ...
    # class Obstacle: ...
    # (as defined at the top for this example)

    creator = MapCreator()
    creator.run()