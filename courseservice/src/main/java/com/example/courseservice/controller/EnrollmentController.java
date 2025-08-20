package com.example.courseservice.controller;

import com.example.courseservice.dto.EnrollmentRequestDTO;
import com.example.courseservice.dto.EnrollmentResponseDTO;
import com.example.courseservice.dto.EnrollmentUpdateRequestDTO;
import com.example.courseservice.service.EnrollmentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.bson.types.ObjectId;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/enrollments")
@RequiredArgsConstructor
public class EnrollmentController {
    private final EnrollmentService service;

    // Create
    @PostMapping
    public ResponseEntity<EnrollmentResponseDTO> create(@Valid @RequestBody EnrollmentRequestDTO request) {
        return ResponseEntity.ok(service.create(request));
    }

    // Read by id
    @GetMapping("/{id}")
    public ResponseEntity<EnrollmentResponseDTO> getById(@PathVariable String id) {
        return ResponseEntity.ok(service.getById(new ObjectId(id)));
    }

    // List by course with pagination
    @GetMapping
    public ResponseEntity<Page<EnrollmentResponseDTO>> listByCourse(
            @RequestParam String courseId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size
    ) {
        Pageable pageable = PageRequest.of(page, size);
        return ResponseEntity.ok(service.listByCourse(new ObjectId(courseId), pageable));
    }

    // Update by id (partial update)
    @PutMapping("/{id}")
    public ResponseEntity<EnrollmentResponseDTO> update(@PathVariable String id,
                                                     @Valid @RequestBody EnrollmentUpdateRequestDTO request) {
        return ResponseEntity.ok(service.update(new ObjectId(id), request));
    }

    // Delete by id
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable String id) {
        service.delete(new ObjectId(id));
        return ResponseEntity.noContent().build();
    }

    // Convenience: get by course & user
    @GetMapping("/by-course-user")
    public ResponseEntity<EnrollmentResponseDTO> getByCourseAndUser(@RequestParam String courseId,
                                                                 @RequestParam String userId) {
        return ResponseEntity.ok(service.getByCourseAndUser(new ObjectId(courseId), userId));
    }

    // Convenience: delete by course & user
    @DeleteMapping("/by-course-user")
    public ResponseEntity<Void> deleteByCourseAndUser(@RequestParam String courseId,
                                                      @RequestParam String userId) {
        service.unenrollByCourseAndUser(new ObjectId(courseId), userId);
        return ResponseEntity.noContent().build();
    }
}
