package com.example.userservice.Repository;

import com.example.userservice.Entity.Role;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface RoleRepository extends JpaRepository<Role, Long> {
    
    Optional<Role> findByRoleName(String roleName);
    
    @Query("SELECT r FROM Role r WHERE r.deleteAt IS NULL")
    List<Role> findAllActive();
    
    @Query("SELECT r FROM Role r WHERE r.id = :id AND r.deleteAt IS NULL")
    Optional<Role> findByIdAndNotDeleted(Long id);
    
    boolean existsByRoleName(String roleName);
}
