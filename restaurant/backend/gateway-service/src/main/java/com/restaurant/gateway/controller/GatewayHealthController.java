package com.restaurant.gateway.controller;

import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class GatewayHealthController {

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of(
                "service", "gateway-service",
                "status", "ok"
        );
    }
}
