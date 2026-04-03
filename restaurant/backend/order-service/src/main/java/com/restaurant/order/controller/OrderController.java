package com.restaurant.order.controller;

import com.restaurant.order.dto.OrderItemRequest;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/orders")
public class OrderController {

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("service", "order-service", "status", "ok");
    }

    @PostMapping
    public Map<String, Object> createOrder(@RequestBody List<OrderItemRequest> items) {
        return Map.of(
                "message", "Order created",
                "itemCount", items.size(),
                "status", "CREATED"
        );
    }
}
