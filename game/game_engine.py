import pygame
import random
from .target import Target

# Game Engine

WHITE = (255, 255, 255)
RED = (220, 60, 60)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.margin = 60
        self.hud_height = 60

        self.difficulty = "medium"

        self.difficulty_settings = {
            "easy": {
                "base_radius": 44,
                "min_radius": 13.2,
                "lifespan_frames": 112
            },
            "medium": {
                "base_radius": 40,
                "min_radius": 12,
                "lifespan_frames": 90
            },
            "hard": {
                "base_radius": 30,
                "min_radius": 9,
                "lifespan_frames": 45
            }
        }

        self.target = self._spawn_target()

        self.round_seconds = 30
        self.time_left_frames = self.round_seconds * 60

        self.hits = 0
        self.misses = 0
        self.score = 0

        self.font = pygame.font.SysFont("Arial", 26)
        self.game_over = False

        # Sound effects
        self.hit_sound = pygame.mixer.Sound("assets/sounds/hit.wav")
        self.miss_sound = pygame.mixer.Sound("assets/sounds/miss.wav")
        self.round_end_sound = pygame.mixer.Sound("assets/sounds/round_end.wav")

        # Prevent round-end sound from playing every rendered frame
        self.round_end_sound_played = False

        button_width = 130
        button_height = 45
        gap = 15

        total_width = (button_width * 3) + (gap * 2)
        start_x = (self.width - total_width) // 2
        button_y = self.height // 2 + 105

        self.easy_button = pygame.Rect(
            start_x,
            button_y,
            button_width,
            button_height
        )

        self.medium_button = pygame.Rect(
            start_x + button_width + gap,
            button_y,
            button_width,
            button_height
        )

        self.hard_button = pygame.Rect(
            start_x + (button_width + gap) * 2,
            button_y,
            button_width,
            button_height
        )

        self.quit_button = pygame.Rect(
            self.width // 2 - button_width // 2,
            button_y + 65,
            button_width,
            button_height
        )

    def _spawn_target(self):
        x = random.randint(
            self.margin,
            self.width - self.margin
        )

        y = random.randint(
            self.margin + self.hud_height,
            self.height - self.margin
        )

        settings = self.difficulty_settings[self.difficulty]

        return Target(
            x,
            y,
            base_radius=settings["base_radius"],
            min_radius=settings["min_radius"],
            lifespan_frames=settings["lifespan_frames"]
        )

    def _restart_game(self, difficulty):
        self.difficulty = difficulty

        self.time_left_frames = self.round_seconds * 60

        self.hits = 0
        self.misses = 0
        self.score = 0

        self.game_over = False
        self.round_end_sound_played = False

        self.target = self._spawn_target()
    
    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                if self.easy_button.collidepoint(x, y):
                    self._restart_game("easy")

                elif self.medium_button.collidepoint(x, y):
                    self._restart_game("medium")

                elif self.hard_button.collidepoint(x, y):
                    self._restart_game("hard")

                elif self.quit_button.collidepoint(x, y):
                    pygame.event.post(
                        pygame.event.Event(pygame.QUIT)
                    )

            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_click(event.pos)

    def _handle_click(self, pos):
        x, y = pos

        if self.target.contains_point(x, y):
            self.hit_sound.play()

            self.hits += 1
            self.score += 1
            self.target = self._spawn_target()

        else:
            self.miss_sound.play()
            self.misses += 1

    def handle_input(self):
        # Reserved for continuously-held-key input; this game is
        # entirely mouse-driven, so there's nothing to poll here.
        pass

    def update(self):
        if self.game_over:
            return

        self.time_left_frames -= 1

        if self.time_left_frames <= 0:
            self.game_over = True

            if not self.round_end_sound_played:
                self.round_end_sound.play()
                self.round_end_sound_played = True

            return

        self.target.update()

        if self.target.expired():
            self.miss_sound.play()

            self.misses += 1
            self.target = self._spawn_target()

    def accuracy(self):
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return round(100 * self.hits / total, 1)

    def render(self, screen):
        if self.game_over:
            screen.fill((35, 35, 40))

            title_font = pygame.font.SysFont("Arial", 42)
            result_font = pygame.font.SysFont("Arial", 28)
            message_font = pygame.font.SysFont("Arial", 23)
            button_font = pygame.font.SysFont("Arial", 22)

            # Final result
            title = title_font.render(
                "Time's Up!",
                True,
                WHITE
            )

            score_text = result_font.render(
                f"Final Score: {self.score}",
                True,
                WHITE
            )

            accuracy_value = self.accuracy()

            accuracy_text = result_font.render(
                f"Accuracy: {accuracy_value}%",
                True,
                WHITE
            )

            # Performance message
            if accuracy_value > 90:
                message = "Excellent! Congratulations!"

            elif accuracy_value > 40:
                message = "Good effort! Keep improving!"

            elif accuracy_value < 30:
                message = "Are you a bot?"

            else:
                message = "Keep practicing!"

            message_text = message_font.render(
                message,
                True,
                WHITE
            )

            # Position result text
            screen.blit(
                title,
                title.get_rect(
                    center=(self.width // 2, 90)
                )
            )

            screen.blit(
                score_text,
                score_text.get_rect(
                    center=(self.width // 2, 145)
                )
            )

            screen.blit(
                accuracy_text,
                accuracy_text.get_rect(
                    center=(self.width // 2, 185)
                )
            )

            screen.blit(
                message_text,
                message_text.get_rect(
                    center=(self.width // 2, 225)
                )
            )

            # Button colors
            GREEN = (70, 180, 90)
            YELLOW = (220, 190, 50)
            RED_BUTTON = (210, 65, 65)

            # Easy button
            pygame.draw.rect(
                screen,
                GREEN,
                self.easy_button,
                border_radius=8
            )

            # Medium button
            pygame.draw.rect(
                screen,
                YELLOW,
                self.medium_button,
                border_radius=8
            )

            # Hard button
            pygame.draw.rect(
                screen,
                RED_BUTTON,
                self.hard_button,
                border_radius=8
            )

            # Quit button:
            # no fill -> transparent/colorless
            pygame.draw.rect(
                screen,
                WHITE,
                self.quit_button,
                width=2,
                border_radius=8
            )

            # Button text
            easy_text = button_font.render(
                "Easy",
                True,
                WHITE
            )

            medium_text = button_font.render(
                "Medium",
                True,
                WHITE
            )

            hard_text = button_font.render(
                "Hard",
                True,
                WHITE
            )

            quit_text = button_font.render(
                "Quit",
                True,
                WHITE
            )

            screen.blit(
                easy_text,
                easy_text.get_rect(
                    center=self.easy_button.center
                )
            )

            screen.blit(
                medium_text,
                medium_text.get_rect(
                    center=self.medium_button.center
                )
            )

            screen.blit(
                hard_text,
                hard_text.get_rect(
                    center=self.hard_button.center
                )
            )

            screen.blit(
                quit_text,
                quit_text.get_rect(
                    center=self.quit_button.center
                )
            )

            return

        # -------------------------
        # Normal gameplay rendering
        # -------------------------

        r = int(self.target.visual_radius())

        pygame.draw.circle(
            screen,
            RED,
            (self.target.x, self.target.y),
            r
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (self.target.x, self.target.y),
            r,
            2
        )

        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            WHITE
        )

        screen.blit(
            score_text,
            (10, 10)
        )

        seconds_left = max(
            0,
            self.time_left_frames // 60
        )

        timer_text = self.font.render(
            f"Time: {seconds_left}s",
            True,
            WHITE
        )

        screen.blit(
            timer_text,
            (self.width - 140, 10)
        )

        acc_text = self.font.render(
            f"Accuracy: {self.accuracy()}%",
            True,
            WHITE
        )

        screen.blit(
            acc_text,
            (self.width // 2 - 90, 10)
        )