from datetime import datetime
from exchange.models import Transaction


def perform_trade(buy_order, buy_order_wallet, sell_order, sell_order_wallet):
    """
    Performs a simple operation in which both the price and quantity of the two orders are equal.

    :argument
    - buy_order: Must be an 'Order' object.
    - buy_order_wallet: Must be a 'Wallet' object.
    - sell_order: Must be an 'Order' object.
    - sell_order_wallet: Must be a 'Wallet' object.
    """

    dollar_amount = buy_order.quantity * buy_order.price
    time_execution = datetime.now()
    transaction = Transaction.objects.create()

    # Execution of buy order
    buy_order.executed_at = time_execution
    buy_order.status = False
    buy_order.transaction = transaction
    buy_order.save()
    buy_order_wallet.frozen_dollar -= dollar_amount
    buy_order_wallet.available_bitcoin += buy_order.quantity
    buy_order_wallet.save()

    # Execution of sell order
    sell_order.price = buy_order.price
    sell_order.executed_at = time_execution
    sell_order.status = False
    sell_order.transaction = transaction
    sell_order.save()
    sell_order_wallet.frozen_bitcoin -= buy_order.quantity
    sell_order_wallet.available_dollar += dollar_amount
    sell_order_wallet.save()


