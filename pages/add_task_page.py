import re
from typing import List, Dict, Optional
from playwright.sync_api import Page, Locator, expect

class AddTaskPage:
    """Page Object for the Add Task page of the React Cool Todo App."""

    def __init__(self, page: Page):
        self.page = page

        # --- Core Locators ---
        self.back_button: Locator = page.locator('button[aria-label="Back"]')
        self.page_title: Locator = page.locator('h2:text("Add New Task")')
        
        # Form inputs
        self.task_name_input: Locator = page.locator('input[name="name"][placeholder="Enter task name"]')
        self.task_description_input: Locator = page.locator('textarea[name="name"][placeholder="Enter task description"]')
        self.task_deadline_input: Locator = page.locator('input[type="datetime-local"]')
        
        # Category selector
        self.category_select: Locator = page.locator('div[role="combobox"]')
        
        # Color selector
        self.color_accordion: Locator = page.locator('.MuiAccordion-root')
        self.color_accordion_summary: Locator = page.locator('.MuiAccordionSummary-root')
        self.color_grid: Locator = page.locator('.MuiGrid-container .MuiGrid-spacing-xs-1')
        self.color_buttons: Locator = page.locator('button[id^="color-element-"]')
        
        # Create Task button
        self.create_task_button: Locator = page.locator('button:text("Create Task")')

    def goto(self, base_url: str) -> None:
        """Navigates to the Add Task page."""
        self.page.goto(f"{base_url}/add")
        expect(self.page_title).to_be_visible(timeout=15000)
        expect(self.task_name_input).to_be_visible(timeout=10000)

    # --- Actions ---

    def fill_task_name(self, name: str) -> None:
        """Fills the task name input field."""
        self.task_name_input.fill(name)

    def fill_task_description(self, description: str) -> None:
        """Fills the task description input field."""
        self.task_description_input.fill(description)

    def set_task_deadline(self, deadline: str) -> None:
        """Sets the task deadline. Format should be YYYY-MM-DDThh:mm."""
        self.task_deadline_input.fill(deadline)

    def select_color(self, color_index: int = 0) -> None:
        """Selects a color for the task by index."""
        # Open color accordion if it's not already open
        if not self.color_grid.is_visible():
            self.color_accordion_summary.click()
            expect(self.color_grid).to_be_visible()
        
        # Select the color by index
        self.color_buttons.nth(color_index).click()

    def create_task(self) -> None:
        """Clicks the Create Task button to create a new task."""
        self.create_task_button.click()
        # Wait for navigation to complete
        self.page.wait_for_url("**/")
        # After navigation back to main page, allow caller to assert on specific task
        self.page.wait_for_timeout(500)  # small pause for UI update

    def add_complete_task(self, name: str, description: str = "", deadline: str = "", color_index: int = 0) -> None:
        """Adds a complete task with all details."""
        self.fill_task_name(name)
        
        if description:
            self.fill_task_description(description)
        
        if deadline:
            self.set_task_deadline(deadline)
        
        self.select_color(color_index)
        self.create_task()

    # --- Assertions ---

    def expect_on_add_task_page(self) -> None:
        """Asserts that we are on the Add Task page."""
        expect(self.page_title).to_be_visible()
        expect(self.create_task_button).to_be_visible()

    def expect_task_name_required_error(self) -> None:
        """Asserts that the task name field shows a required error."""
        # Create task without name
        self.create_task_button.click()
        # Check for error message or validation state
        expect(self.task_name_input).to_have_attribute("aria-invalid", "true")
