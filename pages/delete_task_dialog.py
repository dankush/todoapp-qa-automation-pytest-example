from playwright.sync_api import Page, Locator, expect

class DeleteTaskDialog:
    """Page object for the delete task confirmation dialog."""
    
    def __init__(self, page: Page):
        self.page = page
        
        # Dialog locators - using multiple strategies for reliability
        self._dialog_locators = [
            page.locator('div[role="dialog"]'),
            page.locator('.MuiDialog-root'),  # Material UI dialog class
            page.locator('div:has-text("Delete Task") >> visible=true'),  # Dialog with title
        ]
        
        # Button locators - using the exact button classes from the HTML
        self.confirm_delete_button = page.get_by_role('button', name='Confirm Delete')
        self.cancel_button = page.get_by_role('button', name='Cancel')
    
    def is_visible(self) -> bool:
        """Check if any of the dialog locators is visible."""
        for locator in self._dialog_locators:
            if locator.is_visible():
                return True
        return False
    
    def wait_for_visible(self, timeout: int = 5000) -> None:
        """Wait for the dialog to be visible."""
        # Try each locator strategy
        for locator in self._dialog_locators:
            try:
                expect(locator).to_be_visible(timeout=timeout/len(self._dialog_locators))
                return  # If any locator is found, return
            except:
                continue
        
        # If we get here, none of the locators worked
        raise AssertionError("Delete confirmation dialog not found")
    
    def confirm_delete(self) -> None:
        """Click the confirm delete button."""
        self.wait_for_visible()
        self.page.wait_for_timeout(500)  # Small delay for visibility
        self.confirm_delete_button.click()
        
        # Wait for dialog to disappear
        for locator in self._dialog_locators:
            try:
                expect(locator).to_be_hidden(timeout=5000)
                break
            except:
                continue
    
    def cancel(self) -> None:
        """Click the cancel button."""
        self.wait_for_visible()
        self.page.wait_for_timeout(500)  # Small delay for visibility
        self.cancel_button.click()
        
        # Wait for dialog to disappear
        for locator in self._dialog_locators:
            try:
                expect(locator).to_be_hidden(timeout=5000)
                break
            except:
                continue
