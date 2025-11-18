class HistoryManager:
    """
    Manages game state history for undo/redo operations.

    Uses the Memento pattern to save and restore complete game states
    """

    def __init__(self, max_history_size: int = 100, state=None):
        self.undo_stack = []
        self.redo_stack = []
        self.max_history_size = max_history_size
        self.current_state = state

    def save_state(self, state):
        if self.current_state is not None:
            self.undo_stack.append(self.current_state.copy())

            if len(self.undo_stack) > self.max_history_size:
                self.undo_stack.pop(0)

        self.current_state = state

        self.redo_stack.clear()

    def undo(self):
        if not self.can_undo():
            return None

        if self.current_state is not None:
            self.redo_stack.append(self.current_state.copy())

        previous_state = self.undo_stack.pop()
        self.current_state = previous_state

        return previous_state.copy()

    def redo(self):
        if not self.can_redo():
            return None

        if self.current_state is not None:
            self.undo_stack.append(self.current_state.copy())

        next_state = self.redo_stack.pop()
        self.current_state = next_state

        return next_state.copy()

    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0

    def clear(self):
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.current_state = None

    def get_undo_count(self) -> int:
        return len(self.undo_stack)

    def get_redo_count(self) -> int:
        return len(self.redo_stack)
