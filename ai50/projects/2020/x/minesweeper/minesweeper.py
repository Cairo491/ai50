import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        count = 0
        (row, col) = cell

        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):

                if (i, j) == cell:
                    continue

                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return set(self.cells)
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return set(self.cells)
        return set()

    def mark_mine(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():

    def __init__(self, height=8, width=8):

        self.height = height
        self.width = width

        self.moves_made = set()

        self.mines = set()
        self.safes = set()

        self.knowledge = []

    def mark_mine(self, cell):
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):

        # Mark move as made
        self.moves_made.add(cell)

        # Mark cell safe
        self.mark_safe(cell)

        # Determine neighbors
        neighbors = set()
        (row, col) = cell

        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):
                if (i, j) == cell:
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    if (i, j) not in self.safes:
                        neighbors.add((i, j))

        # Remove known mines
        for m in self.mines:
            if m in neighbors:
                neighbors.remove(m)
                count -= 1

        # Add new logical sentence
        new_sentence = Sentence(neighbors, count)
        self.knowledge.append(new_sentence)

        # Loop until no new inferences can be made
        changed = True
        while changed:
            changed = False

            safes = set()
            mines = set()

            for sentence in self.knowledge:
                safes |= sentence.known_safes()
                mines |= sentence.known_mines()

            for s in safes:
                if s not in self.safes:
                    self.mark_safe(s)
                    changed = True

            for m in mines:
                if m not in self.mines:
                    self.mark_mine(m)
                    changed = True

            # Infer new sentences
            new_sentences = []
            for s1 in self.knowledge:
                for s2 in self.knowledge:
                    if s1 == s2:
                        continue
                    if s1.cells and s1.cells < s2.cells:
                        diff_cells = s2.cells - s1.cells
                        diff_count = s2.count - s1.count
                        new_sentences.append(Sentence(diff_cells, diff_count))

            for s in new_sentences:
                if s not in self.knowledge and len(s.cells) > 0:
                    self.knowledge.append(s)
                    changed = True

    def make_safe_move(self):

        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):

        choices = []
        for i in range(self.height):
            for j in range(self.width):
                cell = (i, j)
                if cell not in self.moves_made and cell not in self.mines:
                    choices.append(cell)

        if len(choices) == 0:
            return None

        return random.choice(choices)

