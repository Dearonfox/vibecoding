package com.restaurant.menu.dto;

public record MenuItemResponse(
        Long id,
        String name,
        String category,
        int price
) {
}
