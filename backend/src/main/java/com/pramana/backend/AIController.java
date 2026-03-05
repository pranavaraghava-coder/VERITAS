package com.pramana.backend;

import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*")
public class AIController {

    private final String PYTHON_API_URL = "http://127.0.0.1:8000/ask";
    private final RestTemplate restTemplate = new RestTemplate();

    @PostMapping("/chat")
    public ResponseEntity<Map<String, Object>> chat(@RequestBody Map<String, String> payload) {
        String userQuestion = payload.get("question");
        System.out.println("📩 Java received question: " + userQuestion);

        Map<String, String> pythonRequest = new HashMap<>();
        pythonRequest.put("text", userQuestion);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, String>> request = new HttpEntity<>(pythonRequest, headers);

        try {
            // We use specific types here to satisfy the compiler
            @SuppressWarnings("unchecked")
            Map<String, Object> responseBody = restTemplate.postForEntity(PYTHON_API_URL, request, Map.class).getBody();
            return ResponseEntity.ok(responseBody);
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Python Brain is dead or unreachable.");
            return ResponseEntity.internalServerError().body(error);
        }
    }
}