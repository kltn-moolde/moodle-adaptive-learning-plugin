package com.example.plugin_moodle_LTI_13.repository;

import com.example.plugin_moodle_LTI_13.model.LtiLaunch;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface LtiLaunchRepository extends JpaRepository<LtiLaunch, Long> {
    Optional<LtiLaunch> findByUserId(String userId);
    Optional<LtiLaunch> findByUserIdAndContextId(String userId, String contextId);
}