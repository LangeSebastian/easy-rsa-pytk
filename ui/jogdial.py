"""Jog-dial navigation system for menu and list navigation."""

from typing import Callable, List, Optional, Any


class JogDialNavigator:
    """Navigation manager for jog-dial interface (up/down/confirm)."""

    def __init__(self):
        """Initialize jog-dial navigator."""
        self.items: List[Any] = []
        self.current_index: int = 0
        self.on_selection_changed: Optional[Callable[[int, Any], None]] = None
        self.on_confirm: Optional[Callable[[int, Any], None]] = None
        self.screen_stack: List[Any] = []

    def set_items(self, items: List[Any]):
        """Set the list of items to navigate.

        Args:
            items: List of items to navigate through
        """
        self.items = items
        self.current_index = 0 if items else -1
        if self.on_selection_changed and items:
            self.on_selection_changed(self.current_index, items[self.current_index])

    def move_up(self):
        """Move selection up (previous item)."""
        if not self.items:
            return

        self.current_index = (self.current_index - 1) % len(self.items)
        if self.on_selection_changed:
            self.on_selection_changed(self.current_index, self.items[self.current_index])

    def move_down(self):
        """Move selection down (next item)."""
        if not self.items:
            return

        self.current_index = (self.current_index + 1) % len(self.items)
        if self.on_selection_changed:
            self.on_selection_changed(self.current_index, self.items[self.current_index])

    def confirm(self):
        """Confirm current selection."""
        if not self.items or self.current_index < 0:
            return

        if self.on_confirm:
            self.on_confirm(self.current_index, self.items[self.current_index])

    def get_current_item(self) -> Optional[Any]:
        """Get currently selected item.

        Returns:
            Currently selected item or None
        """
        if not self.items or self.current_index < 0:
            return None
        return self.items[self.current_index]

    def get_current_index(self) -> int:
        """Get current selection index.

        Returns:
            Current index or -1 if no items
        """
        return self.current_index

    def push_screen(self, screen: Any):
        """Push screen onto navigation stack.

        Args:
            screen: Screen object to push
        """
        self.screen_stack.append(screen)

    def pop_screen(self) -> Optional[Any]:
        """Pop screen from navigation stack.

        Returns:
            Popped screen or None if stack empty
        """
        if self.screen_stack:
            return self.screen_stack.pop()
        return None

    def get_current_screen(self) -> Optional[Any]:
        """Get current screen from stack.

        Returns:
            Current screen or None if stack empty
        """
        if self.screen_stack:
            return self.screen_stack[-1]
        return None

    def clear_stack(self):
        """Clear the navigation stack."""
        self.screen_stack.clear()


class ScrollableNavigator(JogDialNavigator):
    """Extended navigator with scrolling support for long lists."""

    def __init__(self, visible_items: int = 5):
        """Initialize scrollable navigator.

        Args:
            visible_items: Number of items visible at once
        """
        super().__init__()
        self.visible_items = visible_items
        self.scroll_offset = 0

    def set_items(self, items: List[Any]):
        """Set items and reset scroll.

        Args:
            items: List of items to navigate
        """
        super().set_items(items)
        self.scroll_offset = 0

    def move_up(self):
        """Move up with scrolling."""
        if not self.items:
            return

        old_index = self.current_index
        super().move_up()

        # Adjust scroll if needed
        if self.current_index < self.scroll_offset:
            self.scroll_offset = self.current_index
        elif old_index == 0 and self.current_index == len(self.items) - 1:
            # Wrapped to end
            self.scroll_offset = max(0, len(self.items) - self.visible_items)

    def move_down(self):
        """Move down with scrolling."""
        if not self.items:
            return

        old_index = self.current_index
        super().move_down()

        # Adjust scroll if needed
        if self.current_index >= self.scroll_offset + self.visible_items:
            self.scroll_offset = self.current_index - self.visible_items + 1
        elif old_index == len(self.items) - 1 and self.current_index == 0:
            # Wrapped to start
            self.scroll_offset = 0

    def get_visible_items(self) -> List[Any]:
        """Get currently visible items.

        Returns:
            List of visible items
        """
        if not self.items:
            return []

        start = self.scroll_offset
        end = min(start + self.visible_items, len(self.items))
        return self.items[start:end]

    def get_visible_range(self) -> tuple:
        """Get visible item index range.

        Returns:
            Tuple of (start_index, end_index)
        """
        if not self.items:
            return (0, 0)

        start = self.scroll_offset
        end = min(start + self.visible_items, len(self.items))
        return (start, end)

    def is_scrollable(self) -> bool:
        """Check if list needs scrolling.

        Returns:
            True if more items than visible
        """
        return len(self.items) > self.visible_items
