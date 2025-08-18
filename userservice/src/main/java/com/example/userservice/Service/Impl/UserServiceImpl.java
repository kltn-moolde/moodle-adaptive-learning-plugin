package com.example.userservice.Service.Impl;

import com.example.userservice.DTO.UserDTO;
import com.example.userservice.Entity.Role;
import com.example.userservice.Entity.User;
import com.example.userservice.Mapper.UserMapper;
import com.example.userservice.Repository.RoleRepository;
import com.example.userservice.Repository.UserRepository;
import com.example.userservice.Service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {
    
    private final UserRepository userRepository;
    private final RoleRepository roleRepository;
    private final UserMapper userMapper;
    
    @Override
    public List<UserDTO> getAllUsers() {
        List<User> users = userRepository.findAllActive();
        return userMapper.toDTOList(users);
    }
    
    @Override
    public Optional<UserDTO> getUserById(Long id) {
        return userRepository.findByIdAndNotDeleted(id)
                .map(userMapper::toDTO);
    }
    
    @Override
    public Optional<UserDTO> getUserByEmail(String email) {
        return userRepository.findByEmail(email)
                .filter(user -> user.getDeleteAt() == null)
                .map(userMapper::toDTO);
    }
    
    @Override
    public Optional<UserDTO> getUserByExternalId(String externalId) {
        return userRepository.findByExternalId(externalId)
                .filter(user -> user.getDeleteAt() == null)
                .map(userMapper::toDTO);
    }
    
    @Override
    public List<UserDTO> getUsersByRoleId(Long roleId) {
        List<User> users = userRepository.findByRoleIdAndNotDeleted(roleId);
        return userMapper.toDTOList(users);
    }
    
    @Override
    public UserDTO createUser(UserDTO userDTO) {
        // Check if email already exists
        if (userRepository.existsByEmail(userDTO.getEmail())) {
            throw new RuntimeException("User with email '" + userDTO.getEmail() + "' already exists");
        }
        
        // Check if external ID already exists (if provided)
        if (userDTO.getExternalId() != null && userRepository.existsByExternalId(userDTO.getExternalId())) {
            throw new RuntimeException("User with external ID '" + userDTO.getExternalId() + "' already exists");
        }
        
        // Check if role exists
        Role role = roleRepository.findByIdAndNotDeleted(userDTO.getRoleId())
                .orElseThrow(() -> new RuntimeException("Role with ID " + userDTO.getRoleId() + " not found"));
        
        User user = userMapper.toEntity(userDTO);
        user.setRole(role);
        
        User savedUser = userRepository.save(user);
        return userMapper.toDTO(savedUser);
    }
    
    @Override
    public Optional<UserDTO> updateUser(Long id, UserDTO userDTO) {
        return userRepository.findByIdAndNotDeleted(id)
                .map(existingUser -> {
                    // Check if email is being changed and if it already exists
                    if (!existingUser.getEmail().equals(userDTO.getEmail()) && 
                        userRepository.existsByEmail(userDTO.getEmail())) {
                        throw new RuntimeException("User with email '" + userDTO.getEmail() + "' already exists");
                    }
                    
                    // Check if external ID is being changed and if it already exists
                    if (userDTO.getExternalId() != null && 
                        !userDTO.getExternalId().equals(existingUser.getExternalId()) &&
                        userRepository.existsByExternalId(userDTO.getExternalId())) {
                        throw new RuntimeException("User with external ID '" + userDTO.getExternalId() + "' already exists");
                    }
                    
                    // Update role if provided
                    if (userDTO.getRoleId() != null) {
                        Role role = roleRepository.findByIdAndNotDeleted(userDTO.getRoleId())
                                .orElseThrow(() -> new RuntimeException("Role with ID " + userDTO.getRoleId() + " not found"));
                        existingUser.setRole(role);
                    }
                    
                    userMapper.updateEntityFromDTO(userDTO, existingUser);
                    User updatedUser = userRepository.save(existingUser);
                    return userMapper.toDTO(updatedUser);
                });
    }
    
    @Override
    public boolean deleteUser(Long id) {
        return userRepository.findByIdAndNotDeleted(id)
                .map(user -> {
                    user.setDeleteAt(LocalDateTime.now());
                    userRepository.save(user);
                    return true;
                })
                .orElse(false);
    }
    
    @Override
    public boolean existsByEmail(String email) {
        return userRepository.existsByEmail(email);
    }
    
    @Override
    public boolean existsByExternalId(String externalId) {
        return userRepository.existsByExternalId(externalId);
    }
}
