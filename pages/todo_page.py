import re
from typing import List, Dict, Optional
from playwright.sync_api import Page, Locator, expect
from pages.delete_task_dialog import DeleteTaskDialog

class CoolTodoPage:
    """Page Object for the React Cool Todo App."""

    def __init__(self, page: Page):
        self.page = page

        # --- Core Locators ---
        # Main page elements
        self.page_title: Locator = page.locator('div[data-testid="task-container"] h3')
        self.add_task_button: Locator = page.locator('button.MuiButtonBase-root[aria-label="Add Task"]')
        self.task_containers: Locator = page.locator('div[data-testid="task-container"]')
        self.search_input: Locator = page.locator('input[placeholder="Search for task..."]')
        self.task_count_text: Locator = page.locator('h4:has-text("You have")')
        
        # Sidebar elements
        self.sidebar_button: Locator = page.locator('button[aria-label="Sidebar"]')
        self.sidebar_menu: Locator = page.locator('div.MuiDrawer-paper')
        self.sidebar_purge_tasks_link: Locator = self.sidebar_menu.locator('li:has-text("Purge Tasks")')
        
        # Confirmation dialogs
        self.confirm_purge_dialog: Locator = page.locator('div[role="dialog"]:has-text("Delete All Tasks")')
        self.confirm_purge_button: Locator = page.locator('div[role="dialog"] button:has-text("Delete All")') 

        # --- Locators relative to a task container ---
        self.task_menu_button_selector = 'button[aria-label="Task Menu"]'
        self.task_title_selector = 'h3'
        self.task_description_selector = '.MuiTypography-root'
        self.task_completed_icon_selector = 'svg[data-testid="CheckCircleIcon"]'
        
        # --- Empty state text ---
        self.no_tasks_message = (
            page.locator('text="No tasks completed yet"')
            .or_(page.locator('text="Add your first task"'))
            .or_(page.locator('text="No tasks found"'))
        )

        # --- Locators for Menu Items (appear after clicking task menu button) ---
        self.menu_complete_item: Locator = page.locator('ul[role="menu"] li:has-text("Complete")')
        self.menu_pending_item: Locator = page.locator('ul[role="menu"] li:has-text("Pending")')
        self.menu_edit_item: Locator = page.locator('ul[role="menu"] li:has-text("Edit")')
        self.menu_delete_item: Locator = page.locator('ul[role="menu"] li:has-text("Delete")')

        # --- Delete Task Dialog is now handled by DeleteTaskDialog class ---

        # --- Empty state text (duplicate for reload) ---
        self.no_tasks_message = (
            page.locator('text="No tasks completed yet"')
            .or_(page.locator('text="Add your first task"'))
            .or_(page.locator('text="No tasks found"'))
        )

    def goto(self, base_url: str) -> None:
        """Navigates to the app's base URL."""
        self.page.goto(base_url)
        expect(self.add_task_button).to_be_visible(timeout=15000)

    # --- Actions ---

    def navigate_to_add_task_page(self) -> None:
        """Clicks the add button and navigates to the Add Task page."""
        # Use JS click to bypass scrollIntoView issues
        self.add_task_button.evaluate("button => button.click()")
        # Wait for navigation to the add task page
        self.page.wait_for_url("**/add", timeout=15000)
        expect(self.page.locator('h2:text("Add New Task")')).to_be_visible(timeout=10000)

    def add_task(self, title: str, description: str = '') -> None:
        """Adds a new task by navigating to the Add Task page.
        
        Note: This method uses the AddTaskPage object internally.
        """
        from pages.add_task_page import AddTaskPage
        
        # Navigate to add task page
        self.navigate_to_add_task_page()
        
        # Use the AddTaskPage to add the task
        add_task_page = AddTaskPage(self.page)
        add_task_page.add_complete_task(title, description)
        
        # We should now be back on the main page, verify specific task
        if title:
            expect(self.get_task_locator(title)).to_be_visible(timeout=10000)

    def add_tasks(self, tasks: List[Dict[str, str]]) -> None:
        """Adds multiple tasks."""
        for task in tasks:
            self.add_task(task.get('title', ''), task.get('description', ''))

    def get_task_locator(self, title: str) -> Locator:
        """Returns the locator for a specific task card by its title."""
        # Locate the task container whose text contains the title
        return self.page.locator('div[data-testid="task-container"]', has_text=title)

    def open_task_menu(self, task_title: str) -> None:
        """Opens the menu for a specific task."""
        container = self.get_task_locator(task_title)
        # Use force click in case it's not interactable until visible
        container.locator(self.task_menu_button_selector).click(force=True)
        expect(self.page.locator('ul[role="menu"]')).to_be_visible()
        self.page.wait_for_timeout(100) # Small delay for menu animation

    def complete_task(self, task_title: str) -> None:
        """Marks a task as completed via its menu."""
        self.open_task_menu(task_title)
        # Check if "Complete" or "Mark as Pending" is available based on current state
        if self.menu_complete_item.is_visible():
            self.menu_complete_item.click()
        else:
            # Assume it's already complete, or handle error
             print(f"Warning: 'Complete Task' not found for {task_title}, might be already completed.")
             # Close menu manually if needed
             self.page.keyboard.press('Escape') # Press Escape to close menu
             expect(self.page.locator('ul[role="menu"]')).to_be_hidden()
             return # Exit as action cannot be performed

        expect(self.page.locator('ul[role="menu"]')).to_be_hidden()
        expect(self.get_task_locator(task_title).locator(self.task_completed_icon_selector)).to_be_visible()

    def uncomplete_task(self, task_title: str) -> None:
        """Marks a task as pending (un-completes it)."""
        self.open_task_menu(task_title)
         # Check if "Pending" or "Complete Task" is available
        if self.menu_pending_item.is_visible():
             self.menu_pending_item.click()
        else:
            print(f"Warning: 'Mark as Pending' not found for {task_title}, might be already pending.")
            # Close menu manually if needed
            self.page.keyboard.press('Escape') # Press Escape to close menu
            expect(self.page.locator('ul[role="menu"]')).to_be_hidden()
            return # Exit

        expect(self.page.locator('ul[role="menu"]')).to_be_hidden()
        expect(self.get_task_locator(task_title).locator(self.task_completed_icon_selector)).to_be_hidden()

    def delete_task(self, task_title: str, confirm: bool = True) -> None:
        """Deletes a task via its menu and handles confirmation."""
        task_locator = self.get_task_locator(task_title)
        if not task_locator.is_visible():
             print(f"Task '{task_title}' not found for deletion.")
             return # Avoid error if task already gone

        # Add explicit wait before opening menu
        self.page.wait_for_timeout(500)  # 500ms pause for visibility
        self.open_task_menu(task_title)
        self.page.wait_for_timeout(500)  # 500ms pause for visibility
        self.menu_delete_item.click()

        # Use the DeleteTaskDialog page object to handle the confirmation
        delete_dialog = DeleteTaskDialog(self.page)
        
        if confirm:
            # Confirm deletion
            delete_dialog.confirm_delete()
            # Verify task was deleted
            expect(task_locator).to_be_hidden(timeout=10000)  # Wait for deletion
        else:
            # Cancel deletion
            delete_dialog.cancel()
            # Verify task still exists
            expect(task_locator).to_be_visible()

    def start_edit_task(self, task_title: str) -> None:
        """Opens the edit modal for a specific task."""
        self.open_task_menu(task_title)
        self.menu_edit_item.click()
        expect(self.task_modal).to_be_visible() # Re-uses modal
        expect(self.save_task_modal_button).to_be_visible() # Wait for edit mode

    def edit_task(self, original_title: str, new_title: str, new_description: Optional[str] = None) -> None:
        """Edits a task's title and/or description."""
        self.start_edit_task(original_title)
        self.task_title_input.fill(new_title)
        if new_description is not None: # Allows setting empty description
            self.task_description_input.fill(new_description)
        self.save_task_modal_button.click()

        expect(self.task_modal).to_be_hidden()
        expect(self.get_task_locator(new_title)).to_be_visible()
        expect(self.get_task_locator(original_title)).to_be_hidden()

    def search_tasks(self, search_term: str) -> None:
        """Enters text into the search bar."""
        self.search_input.fill(search_term)
        self.page.wait_for_timeout(500) # Wait for filtering debounce/render

    def clear_search(self) -> None:
        """Clears the search bar."""
        self.search_input.clear()
        self.page.wait_for_timeout(500)

    def purge_all_tasks(self) -> None:
        """Opens sidebar and clicks Purge Tasks, confirms deletion."""
        self.sidebar_button.click()
        expect(self.sidebar_menu).to_be_visible()
        self.sidebar_purge_tasks_link.click()

        # Confirmation modal for purge
        expect(self.confirm_purge_dialog).to_be_visible()
        self.confirm_purge_button.click()

        expect(self.confirm_purge_dialog).to_be_hidden()
        expect(self.task_containers).to_have_count(0, timeout=10000)

        # Close sidebar (optional, click away or find close button)
        self.page.keyboard.press('Escape') # Try Escape first
        expect(self.sidebar_menu).to_be_hidden(timeout=5000)

    # --- Assertions ---

    def expect_task_count(self, expected_count: int) -> None:
        """Asserts the active task count displayed in the header."""
        count_regex = r"(\d+)\s+tasks?" # Regex to extract number

        # Use expect with a lambda to handle potential timing issues and empty states
        expect(self.page.locator('body')).to_satisfy( # Check against body to allow header/empty message
            lambda _: self._get_current_task_count(count_regex) == expected_count,
            timeout=10000
        )

    def _get_current_task_count(self, regex: str) -> int:
        """Helper to safely get the displayed task count."""
        if self.task_count_text.is_visible():
            text = self.task_count_text.text_content() or ""
            match = re.search(regex, text)
            if match:
                return int(match.group(1))
        # Check for empty state messages if header isn't showing count
        if self.no_tasks_message.is_visible():
             return 0
        # If header visible but no count found, or neither visible, return -1 or raise error?
        # Let's return 0 if no tasks seem present, otherwise maybe -1 to indicate error state.
        if not self.task_containers.first.is_visible(timeout=1000): # Quick check if any tasks rendered
             return 0
        print("Warning: Could not determine task count from header or empty state message.")
        return -1 # Indicate error or unknown state

    def expect_total_task_cards(self, count: int) -> None:
        """Asserts the number of visible task card elements."""
        expect(self.task_containers).to_have_count(count)
        
    def get_visible_task_count(self) -> int:
        """Returns the number of visible task cards."""
        # Count only visible task containers
        return self.page.locator('div[data-testid="task-container"]:visible').count()

    def expect_task_visible(self, title: str, description: Optional[str] = None) -> None:
        """Asserts a task with the given title (and optionally description) is visible."""
        task_locator = self.get_task_locator(title)
        expect(task_locator).to_be_visible()
        expect(task_locator.locator(self.task_title_selector)).to_have_text(title)
        if description is not None:
            # Description matching might need to be contains_text depending on formatting
            expect(task_locator.locator(self.task_description_selector)).to_contain_text(description)

    def expect_task_hidden(self, title: str) -> None:
        """Asserts a task with the given title is hidden."""
        expect(self.get_task_locator(title)).to_be_hidden()

    def expect_task_completed(self, title: str, is_completed: bool = True) -> None:
        """Asserts the visual completed state of a task."""
        task_item = self.get_task_locator(title)
        completed_icon = task_item.locator(self.task_completed_icon_selector)
        if is_completed:
            expect(completed_icon).to_be_visible()
            # Optionally check for style changes like strikethrough if applied
            # expect(task_item.locator(self.task_title_selector)).to_have_css('text-decoration-line', 'line-through')
        else:
            expect(completed_icon).to_be_hidden()
            # expect(task_item.locator(self.task_title_selector)).not_to_have_css('text-decoration-line', 'line-through')

    def expect_task_list_to_contain(self, tasks: List[Dict[str, str]], check_completion: bool = False, expected_completion_status: Optional[List[bool]] = None) -> None:
        """Asserts the list contains the specified tasks and optionally checks their completion state."""
        expect(self.task_containers).to_have_count(len(tasks))
        if expected_completion_status is None:
            expected_completion_status = []

        for i, task in enumerate(tasks):
            title = task.get('title', '')
            desc = task.get('description') # Can be None
            self.expect_task_visible(title, desc)
            if check_completion:
                # Default to not completed if status list is too short
                is_completed = expected_completion_status[i] if i < len(expected_completion_status) else False
                self.expect_task_completed(title, is_completed)

    def expect_no_tasks(self) -> None:
        """Asserts that no task cards are visible and the empty state is shown."""
        expect(self.task_containers).to_have_count(0)
        # Show either an empty message or zero-count header
        zero_header = self.task_count_text.filter(has_text=re.compile(r"0 tasks?"))
        expect(self.no_tasks_message.or_(zero_header)).to_be_visible()

    def expect_search_placeholder(self, text: str) -> None:
        """Asserts the placeholder text of the search input."""
        expect(self.search_input).to_have_attribute('placeholder', text)

    # --- Cleanup ---

    def delete_all_tasks_via_ui(self) -> None:
        """Deletes all visible tasks one by one using the UI. Slower but reliable."""
        print("Attempting to delete all tasks via UI...")
        # It's safer to repeatedly get the count and delete the first one
        # as the locator list might become stale after deletions.
        while self.task_containers.count() > 0:
             count_before = self.task_containers.count()
             print(f"Tasks remaining: {count_before}")
             first_task = self.task_containers.first
             try:
                 # Get title dynamically before deleting
                 title_element = first_task.locator(self.task_title_selector)
                 expect(title_element).to_be_visible(timeout=5000) # Ensure title is loaded
                 task_title = title_element.text_content()
                 if task_title:
                     print(f"Deleting task: {task_title}")
                     self.delete_task(task_title, confirm=True)
                     # Add a small wait to allow UI to update before next iteration
                     self.page.wait_for_timeout(300)
                     count_after = self.task_containers.count()
                     print(f"Tasks remaining after delete: {count_after}")
                     if count_after >= count_before:
                          print("Warning: Task count did not decrease after deletion attempt. Breaking loop.")
                          break # Avoid infinite loop if deletion fails silently
                 else:
                     print("Warning: Could not retrieve title for the first task. Breaking loop.")
                     break
             except Exception as e:
                 print(f"Error during task deletion: {e}. Breaking loop.")
                 # Try refreshing page or taking screenshot might help debug here
                 break
        print("Finished deleting tasks via UI.")
        self.expect_no_tasks()

    def clear_storage_and_reload(self) -> None:
        """Clears localStorage and reloads the page."""
        print("Clearing localStorage and reloading...")
        self.page.evaluate("() => window.localStorage.clear()")
        self.page.reload()
        # Wait for app to re-initialize after reload
        expect(self.add_task_button).to_be_visible(timeout=20000) # Increased timeout after reload
        # Wait for either the count or the empty message
        expect(self.task_count_text.or_(self.no_tasks_message)).to_be_visible(timeout=15000)
        self.page.wait_for_timeout(500) # Extra small wait for stability
        print("Page reloaded after clearing storage.")

    def click_add_task_button(self) -> None:
        """Clicks the Add Task button."""
        self.add_task_button.click()

    def wait_for_add_task_page(self) -> None:
        """Waits for the Add Task page to load."""
        self.page.wait_for_url("**/add")
        expect(self.page.locator('h2:text("Add New Task")')).to_be_visible()

    def enter_task_title(self, title: str) -> None:
        """Enters the task title."""
        self.page.locator('input[name="name"][placeholder="Enter task name"]').fill(title)

    def click_create_task_button(self) -> None:
        """Clicks the Create Task button."""
        self.page.locator('button:text("Create Task")').click()

    def wait_for_main_page(self) -> None:
        """Waits for the main page to load after task creation."""
        self.page.wait_for_url("**/")
        expect(self.page_title).to_be_visible()
