from api.models import Order

STATUS_SEQUENCE = [
    Order.OrderStatus.PENDING,
    Order.OrderStatus.CONFIRMED,
    Order.OrderStatus.PROCESSING,
    Order.OrderStatus.SHIPPED,
    Order.OrderStatus.DELIVERED,
    Order.OrderStatus.CANCELED,
]

STATUS_INDEX = {status: index for index, status in enumerate(STATUS_SEQUENCE)}


def is_valid_transaction(current_status, new_status):
    if new_status == current_status:
        return True

    if new_status not in STATUS_INDEX:
        return False

    if current_status in (Order.OrderStatus.DELIVERED, Order.OrderStatus.CANCELED):
        return False

    if new_status == Order.OrderStatus.CANCELED:
        return current_status != Order.OrderStatus.DELIVERED

    current_index = STATUS_INDEX.get(current_status)
    new_index = STATUS_INDEX.get(new_status)

    if current_index is None or new_index is None:
        return False

    return new_index > current_index