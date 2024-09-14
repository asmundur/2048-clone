# 2048 game implemented using Textual framework
import random
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.widgets import Static, Header, Footer
from textual.reactive import reactive
from textual import events

class Tile(Static):
    value = reactive(0)

    def render(self):
        tile_colors = {
            0: "white on black",
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
        style = tile_colors.get(self.value, "white on magenta")
        return f"[{style}]{self.value if self.value > 0 else ''}[/{style}]"

class Game2048(App):
    CSS = """
    Grid#grid {
        grid-size: 4 4;
        grid-gutter: 1 1;
        content-align: center middle;
    }
    """

    board = [[0]*4 for _ in range(4)]
    tiles = []
    score = reactive(0)

    def compose(self) -> ComposeResult:
        yield Header()

        all_tiles = []

        # Generate the tiles and add them to the list
        for i in range(4):
            row = []
            for j in range(4):
                tile = Tile()
                row.append(tile)
                all_tiles.append(tile)
            self.tiles.append(row)

        # Create the Grid and pass the tiles as children
        grid = Grid(*all_tiles, id="grid")

        yield grid
        yield Footer()

    def on_mount(self):
        self.init_game()

    def init_game(self):
        self.board = [[0]*4 for _ in range(4)]
        self.add_random_tile()
        self.add_random_tile()
        self.update_tiles()

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
                await self.show_game_over()

    async def show_game_over(self):
        from textual.widgets import Label
        from textual.containers import Center

        await self.push_screen(
            Center(
                Label(
                    "Game Over! Press 'r' to restart or 'q' to quit.",
                    style="bold red",
                ),
            )
        )

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
