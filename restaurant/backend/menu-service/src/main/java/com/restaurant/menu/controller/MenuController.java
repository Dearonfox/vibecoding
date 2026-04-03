package com.restaurant.menu.controller;

import com.restaurant.menu.dto.MenuItemResponse;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/menus")
public class MenuController {

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("service", "menu-service", "status", "ok");
    }

    @GetMapping
    public List<MenuItemResponse> getMenus() {
        return List.of(
                new MenuItemResponse(1L, "김치볶음밥", "한식", 9000),
                new MenuItemResponse(2L, "제육덮밥", "한식", 10000)
        );
    }
}
