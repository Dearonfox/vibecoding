package com.restaurant.review.controller;

import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/reviews")
public class ReviewController {

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("service", "review-service", "status", "ok");
    }

    @GetMapping
    public List<Map<String, Object>> getReviews() {
        return List.of(
                Map.of("id", 1, "rating", 5, "content", "맛있고 빨리 나왔어요.")
        );
    }

    @PostMapping("/ai-generated")
    public Map<String, Object> saveGeneratedReview(@RequestBody Map<String, Object> payload) {
        return Map.of("message", "AI review saved", "payload", payload);
    }
}
