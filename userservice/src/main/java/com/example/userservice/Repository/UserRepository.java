package com.example.userservice.Repository;

import com.example.userservice.Entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    Optional<User> findByEmail(String email);
    
    Optional<User> findByExternalId(String externalId);
    
    @Query("SELECT u FROM User u WHERE u.deleteAt IS NULL")
    List<User> findAllActive();
    
    @Query("SELECT u FROM User u WHERE u.id = :id AND u.deleteAt IS NULL")
    Optional<User> findByIdAndNotDeleted(@Param("id") Long id);
    
    @Query("SELECT u FROM User u WHERE u.role.id = :roleId AND u.deleteAt IS NULL")
    List<User> findByRoleIdAndNotDeleted(@Param("roleId") Long roleId);
    
    boolean existsByEmail(String email);
    
    boolean existsByExternalId(String externalId);
}
