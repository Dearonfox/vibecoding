package com.restaurant.order.dto;

public record OrderItemRequest(
        Long menuId,
        int quantity
) {
}
