# 2048 game implemented using the Textual framework

import random
from textual.app import App, ComposeResult
from textual.containers import Vertical, Container, Horizontal
from textual.widgets import Static, Header, Footer, Label
from textual.reactive import reactive
from textual import events

class Tile(Static):
    value = reactive(0)

    def render(self):
        # Define the styles for each tile value
        tile_styles = {
            0: "on black",  # Background for empty tiles
            2: "black on white",
            4: "black on bright_white",
            8: "white on dark_red",
            16: "white on red",
            32: "white on dark_orange",
            64: "white on orange1",
            128: "white on yellow3",
            256: "white on khaki1",
            512: "white on light_goldenrod1",
            1024: "white on light_yellow",
            2048: "white on bright_yellow",
        }

        style = tile_styles.get(self.value, "white on magenta")
        text = str(self.value) if self.value > 0 else ""
        return f"[{style}]{text}[/{style}]"

class Game2048(App):
    CSS = """
    #main_container {
        align: center middle;
    }

    Tile {
        border: solid grey;
        text-align: center;
        height: 3;
        width: 7;
    }

    Horizontal {
        align: center middle;
    }

    #score_label {
        content-align: center middle;
        color: yellow;
        text-style: bold;
        padding: 1 0;
    }

    #game_over_label {
        content-align: center middle;
        color: red;
        text-style: bold;
        padding: 1 0;
    }

    #outer_container {
        align: center middle;
        height: 100%;
        width: 100%;
    }
    """

    board = [[0]*4 for _ in range(4)]
    tiles = []
    score = reactive(0)
    game_over = reactive(False)

    def compose(self) -> ComposeResult:
        yield Header()

        # Create the score label and game over label
        self.score_label = Label('', id='score_label')
        self.game_over_label = Label('', id='game_over_label')
        self.game_over_label.visible = False

        # Generate the tiles and create rows using Horizontal containers
        self.tiles = []  # Reset tiles list
        rows = []
        for i in range(4):
            row = []
            row_tiles = []
            for j in range(4):
                tile = Tile()
                row.append(tile)
                row_tiles.append(tile)
            self.tiles.append(row)
            rows.append(Horizontal(*row_tiles, id=f"row_{i}"))

        # Create the main content using Vertical container
        main_container = Vertical(
            self.score_label,
            *rows,
            self.game_over_label,
            id="main_container"
        )

        # Wrap the main container in another container to ensure proper sizing
        yield Container(
            main_container,
            id="outer_container"
        )

        yield Footer()

    def on_mount(self):
        self.init_game()

    def watch_score(self, old_value, new_value):
        self.score_label.update(f"Score: [bold yellow]{new_value}[/bold yellow]")

    def init_game(self):
        self.board = [[0]*4 for _ in range(4)]
        self.score = 0
        self.add_random_tile()
        self.add_random_tile()
        self.update_tiles()
        self.game_over_label.update('')
        self.game_over_label.visible = False
        self.game_over = False
        self.score_label.update(f"Score: [bold yellow]{self.score}[/bold yellow]")

    def add_random_tile(self):
        empty_cells = [
            (i, j) for i in range(4) for j in range(4) if self.board[i][j] == 0
        ]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = 4 if random.random() > 0.9 else 2

    def update_tiles(self):
        for i in range(4):
            for j in range(4):
                self.tiles[i][j].value = self.board[i][j]

    async def on_key(self, event: events.Key):
        key = event.key
        if self.game_over:
            if key == "r":
                self.init_game()
            elif key == "q":
                await self.action_quit()
            return
        changed = False
        if key == "left":
            changed = self.move_left()
        elif key == "right":
            changed = self.move_right()
        elif key == "up":
            changed = self.move_up()
        elif key == "down":
            changed = self.move_down()
        elif key == "r":
            self.init_game()
            return
        elif key == "q":
            await self.action_quit()
        else:
            return
        if changed:
            self.add_random_tile()
            self.update_tiles()
            if self.is_game_over():
                self.show_game_over()

    def show_game_over(self):
        self.game_over_label.update("[bold red]Game Over! Press 'r' to restart or 'q' to quit.[/bold red]")
        self.game_over_label.visible = True
        self.game_over = True

    def move_left(self):
        changed = False
        for i in range(4):
            original_row = self.board[i][:]
            new_row = [num for num in self.board[i] if num != 0]
            j = 0
            while j < len(new_row) - 1:
                if new_row[j] == new_row[j + 1]:
                    new_row[j] *= 2
                    self.score += new_row[j]
                    del new_row[j + 1]
                    changed = True
                j += 1
            new_row += [0] * (4 - len(new_row))
            if new_row != original_row:
                changed = True
            self.board[i] = new_row
        return changed

    def move_right(self):
        for i in range(4):
            self.board[i] = self.board[i][::-1]
        changed = self.move_left()
        for i in range(4):
            self.board[i] = self.board[i][::-1]
        return changed

    def move_up(self):
        self.board = [list(row) for row in zip(*self.board)]
        changed = self.move_left()
        self.board = [list(row) for row in zip(*self.board)]
        return changed

    def move_down(self):
        self.board = [list(row) for row in zip(*self.board)]
        for i in range(4):
            self.board[i] = self.board[i][::-1]
        changed = self.move_left()
        for i in range(4):
            self.board[i] = self.board[i][::-1]
        self.board = [list(row) for row in zip(*self.board)]
        return changed

    def is_game_over(self):
        for i in range(4):
            for j in range(4):
                if self.board[i][j] == 0:
                    return False
                if j < 3 and self.board[i][j] == self.board[i][j + 1]:
                    return False
                if i < 3 and self.board[i][j] == self.board[i + 1][j]:
                    return False
        return True

if __name__ == "__main__":
    Game2048().run()
