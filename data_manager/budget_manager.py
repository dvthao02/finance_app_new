import os
import logging
from utils.file_helper import load_json, save_json, generate_id
import datetime # Added for created_at/updated_at in add_or_update_budget

# Cấu hình logging
logger = logging.getLogger(__name__)

class BudgetManager:
    def __init__(self, file_path='budgets.json', notification_manager=None, category_manager=None, user_manager=None, transaction_manager=None): # Added transaction_manager
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        self.file_path = os.path.join(data_dir, file_path)
        if not os.path.exists(self.file_path):
            save_json(self.file_path, [])
        self.notification_manager = notification_manager
        self.category_manager = category_manager
        self.user_manager = user_manager # Store user_manager
        self.transaction_manager = transaction_manager # Store transaction_manager

    def get_all_budgets(self):
        return load_json(self.file_path)

    def get_budgets_by_user(self, user_id):
        return [b for b in self.get_all_budgets() if b.get('user_id') == user_id]
        
    def add_budget(self, budget): # Assuming this is a simple add, not add_or_update
        budgets = self.get_all_budgets()
        # Ensure ID generation and timestamps if this method is used directly
        if 'id' not in budget or not budget['id']:
            budget['id'] = generate_id('budget', budgets)
        now_iso = datetime.datetime.now().isoformat()
        budget.setdefault('created_at', now_iso)
        budget.setdefault('updated_at', now_iso)
        # For a new budget, current_amount (remaining) should be the limit
        budget.setdefault('current_amount', budget.get('limit', 0))
        budgets.append(budget)
        save_json(self.file_path, budgets)
        return budget
        
    def get_budgets_by_month(self, year, month, user_id=None):
        budgets = self.get_all_budgets()
        if user_id:
            budgets = [b for b in budgets if b.get('user_id') == user_id]
        return [b for b in budgets if b.get('year') == year and b.get('month') == month]

    def get_budget_by_id(self, budget_id):
        budgets = self.get_all_budgets()
        for budget in budgets:
            if budget.get('id') == budget_id:
                return budget
        return None

    def update_budget(self, budget_id, updated_data): # Generic update, used by Admin typically
        budgets = self.get_all_budgets()
        for i, budget in enumerate(budgets):
            if budget.get('id') == budget_id:
                # Preserve original id and user_id if they were not part of updated_data
                original_user_id = budget.get('user_id')
                original_id = budget.get('id')
                
                budgets[i].update(updated_data) # Apply all changes from updated_data first
                
                # Restore user_id and id if they were not in updated_data, to prevent accidental deletion/clearing
                if 'user_id' not in updated_data and original_user_id is not None:
                    budgets[i]['user_id'] = original_user_id
                if 'id' not in updated_data and original_id is not None: 
                    budgets[i]['id'] = original_id
                
                # If limit was part of updated_data, recalculate current_amount based on actual transactions
                if 'limit' in updated_data: # Check if 'limit' was a key in the input updated_data dict
                    new_limit = budgets[i].get('limit', 0) # Get the new limit value from the updated budget item
                    
                    b_user_id = budgets[i].get('user_id')
                    b_category_id = budgets[i].get('category_id')
                    b_year = budgets[i].get('year')
                    b_month = budgets[i].get('month')
                    
                    actual_spent = 0
                    if self.transaction_manager and b_user_id and b_category_id and b_year is not None and b_month is not None:
                        actual_spent = self.transaction_manager.get_total_expenses(b_user_id, b_category_id, b_year, b_month)
                        logger.debug(f"BudgetManager.update_budget (recalc): Budget ID: {budget_id}, New Limit: {new_limit}, Actual Spent: {actual_spent} for User: {b_user_id}, Cat: {b_category_id}, Period: {b_month}/{b_year}")
                    else:
                        logger.warning(f"BudgetManager.update_budget (recalc): Could not calculate actual_spent for budget ID {budget_id} due to missing info/transaction_manager. "
                                       f"User: {b_user_id}, Cat: {b_category_id}, Year: {b_year}, Month: {b_month}. "
                                       f"TransactionManager available: {bool(self.transaction_manager)}. Defaulting actual_spent to 0.")
                    
                    budgets[i]['current_amount'] = new_limit - actual_spent  # KHÔNG ép về min/max
                # If 'limit' was not in updated_data, current_amount is either from updated_data or remains as it was.
                
                budgets[i]['updated_at'] = datetime.datetime.now().isoformat()
                save_json(self.file_path, budgets)
                return True
        return False

    def delete_budget(self, budget_id):
        budgets = self.get_all_budgets()
        original_length = len(budgets)
        budgets = [b for b in budgets if b.get('id') != budget_id]
        if len(budgets) < original_length:
            save_json(self.file_path, budgets)
            return True
        return False

    def add_or_update_budget(self, budget_data):
        """Adds a new budget or updates an existing one for the same category, month, year, and user.
        'current_amount' will store the remaining balance, calculated from actual transactions.
        """
        budgets = self.get_all_budgets()
        user_id = budget_data.get('user_id')
        category_id = budget_data.get('category_id') 
        month = budget_data.get('month')
        year = budget_data.get('year')
        new_limit = budget_data.get('limit', 0)

        existing_budget_index = -1
        for i, b in enumerate(budgets):
            if (b.get('user_id') == user_id and
                b.get('category_id') == category_id and 
                b.get('month') == month and
                b.get('year') == year):
                existing_budget_index = i
                break
        
        now_iso = datetime.datetime.now().isoformat()

        # Calculate actual spent amount from transactions
        actual_spent = 0
        if self.transaction_manager and user_id and category_id and year and month:
            actual_spent = self.transaction_manager.get_total_expenses(user_id, category_id, year, month)
            logger.debug(f"BudgetManager.add_or_update_budget: Calculated actual spent for user={user_id}, cat={category_id}, Y/M={year}/{month}: {actual_spent}")
        
        # Calculate new remaining balance
        new_remaining = new_limit - actual_spent
        # Không ép new_remaining về tối đa limit, cho phép âm nếu chi vượt
        # new_remaining = min(new_remaining, new_limit)  # XÓA DÒNG NÀY

        if existing_budget_index != -1: 
            target_budget = budgets[existing_budget_index]
            target_budget.update(budget_data) 
            target_budget['current_amount'] = new_remaining  # Set remaining based on actual transactions
            target_budget['updated_at'] = now_iso
            
            save_json(self.file_path, budgets)
            logger.debug(f"BudgetManager: Updated existing budget. Limit: {new_limit}, Actual Spent: {actual_spent}, Remaining: {new_remaining}")
            return target_budget
        else: 
            budget_data['id'] = generate_id('budget', budgets)
            budget_data['current_amount'] = new_remaining  # Set remaining based on actual transactions
            budget_data.setdefault('created_at', now_iso)
            budget_data.setdefault('updated_at', now_iso)
            if 'user_id' not in budget_data and hasattr(self.user_manager, 'current_user_id'):
                 budget_data['user_id'] = self.user_manager.current_user_id
            budgets.append(budget_data)
            save_json(self.file_path, budgets)
            logger.debug(f"BudgetManager: Created new budget. Limit: {new_limit}, Actual Spent: {actual_spent}, Remaining: {new_remaining}")
            return budget_data

    def apply_expense_to_budget(self, user_id, category_id, year, month, expense_amount):
        """
        Applies an expense to a specific budget, decreasing the remaining balance.
        'current_amount' in the budget item stores the remaining balance.

        Args:
            user_id (str): The ID of the user.
            category_id (str): The ID of the category.
            year (int): The year of the budget.
            month (int): The month of the budget.
            expense_amount (float): The amount of the expense (should be positive).
        """
        budgets = self.get_all_budgets()
        updated = False
        logger.debug(f"BudgetManager: Applying expense for user='{user_id}', cat='{category_id}', Y/M={year}/{month}, expense={expense_amount}")
        
        for budget_item in budgets:
            b_user_id = budget_item.get('user_id')
            b_category_id = budget_item.get('category_id')
            b_year = budget_item.get('year')
            b_month = budget_item.get('month')

            if (b_user_id == user_id and
                b_category_id == category_id and
                b_year == year and 
                b_month == month):

                original_remaining = budget_item.get('current_amount', budget_item.get('limit', 0))
                limit = budget_item.get('limit', 0)

                new_remaining = original_remaining - expense_amount
                budget_item['current_amount'] = new_remaining
                budget_item['updated_at'] = datetime.datetime.now().isoformat()

                logger.debug(f"BudgetManager: Budget for cat='{category_id}' updated. Limit: {limit}, Original Remaining: {original_remaining}, Expense: {expense_amount}, New Remaining: {new_remaining}")

                if new_remaining < 0 and expense_amount > 0:
                    if self.notification_manager and self.category_manager and self.user_manager:
                        category_details = self.category_manager.get_category_by_id(category_id)
                        category_name = category_details.get('name', 'Không rõ') if category_details else 'Không rõ'
                        user_details = self.user_manager.get_user_by_id(user_id)
                        user_name = user_details.get('name', 'Người dùng') if user_details else 'Người dùng'
                        spent_total = limit - new_remaining 
                        overspent_by = -new_remaining
                        title = "Cảnh báo vượt ngân sách"
                        content = (f"Bạn đã chi tiêu {spent_total:,.0f}đ cho hạng mục '{category_name}', "
                                   f"vượt quá {overspent_by:,.0f}đ so với ngân sách {limit:,.0f}đ "
                                   f"cho tháng {month}/{year}.")
                        # Gọi đúng thứ tự positional arguments theo NotificationManager: title, content, notify_type, user_id
                        self.notification_manager.add_notification(
                            user_id=user_id,
                            title=title,
                            content=content,
                            notify_type="warning"
                        )
                        logger.info(f"BudgetManager: Over budget notification sent for user {user_id} ({user_name}), category {category_name}.")
                    else:
                        logger.warning("BudgetManager: Cannot send over budget notification due to missing manager (notification, category, or user manager).")
                
                updated = True
                break
        
        if updated:
            save_json(self.file_path, budgets)
            logger.debug(f"BudgetManager: budgets.json saved after applying expense for user='{user_id}', cat='{category_id}'.")
        else:
            logger.warning(f"BudgetManager: No matching budget found to apply expense for user='{user_id}', cat='{category_id}', Y/M={year}/{month}")
        return updated

    def revert_expense_from_budget(self, user_id, category_id, year, month, reverted_expense_amount):
        """
        Reverts an expense from a specific budget, increasing the remaining balance.
        Typically used when an expense transaction is deleted.
        'current_amount' in the budget item stores the remaining balance.

        Args:
            user_id (str): The ID of the user.
            category_id (str): The ID of the category.
            year (int): The year of the budget.
            month (int): The month of the budget.
            reverted_expense_amount (float): The amount of the expense to revert (should be positive).
        """
        budgets = self.get_all_budgets()
        updated = False
        logger.debug(f"BudgetManager: Reverting expense for user='{user_id}', cat='{category_id}', Y/M={year}/{month}, reverted_amount={reverted_expense_amount}")
        
        for budget_item in budgets:
            b_user_id = budget_item.get('user_id')
            b_category_id = budget_item.get('category_id')
            b_year = budget_item.get('year')
            b_month = budget_item.get('month')

            if (b_user_id == user_id and
                b_category_id == category_id and
                b_year == year and 
                b_month == month):
                original_remaining = budget_item.get('current_amount', budget_item.get('limit', 0))
                new_remaining = original_remaining + reverted_expense_amount # Increase remaining
                budget_item['current_amount'] = new_remaining # KHÔNG ép về limit
                budget_item['updated_at'] = datetime.datetime.now().isoformat()
                logger.debug(f"BudgetManager: Budget for cat='{category_id}' updated after reverting expense. Original Remaining: {original_remaining}, Reverted Amount: {reverted_expense_amount}, New Remaining: {new_remaining}")
                updated = True
                break
        
        if updated:
            save_json(self.file_path, budgets)
            logger.debug(f"BudgetManager: budgets.json saved after reverting expense for user='{user_id}', cat='{category_id}'.")
        else:
            logger.warning(f"BudgetManager: No matching budget found to revert expense for user='{user_id}', cat='{category_id}', Y/M={year}/{month}")
        return updated
