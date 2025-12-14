package com.example.userservice.Service;

import com.example.userservice.DTO.UserDTO;

import java.util.List;
import java.util.Optional;

public interface UserService {
    
    List<UserDTO> getAllUsers();
    
    Optional<UserDTO> getUserById(Long id);
    
    Optional<UserDTO> getUserByEmail(String email);
    
    Optional<UserDTO> getUserByExternalId(String externalId);
    
    List<UserDTO> getUsersByRoleId(Long roleId);
    
    UserDTO createUser(UserDTO userDTO);
    
    Optional<UserDTO> updateUser(Long id, UserDTO userDTO);
    
    boolean deleteUser(Long id);
    
    boolean existsByEmail(String email);
    
    boolean existsByExternalId(String externalId);
    
    // LTI-specific methods
    UserDTO createLTIUser(String name, String email, String role, String ltiUserId, String courseId);
    
    UserDTO updateUserFromLTI(UserDTO existingUser, String name, String role, String ltiUserId, String courseId);
}
