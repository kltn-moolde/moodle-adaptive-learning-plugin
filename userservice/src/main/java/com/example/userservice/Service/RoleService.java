package com.example.userservice.Service;

import com.example.userservice.DTO.RoleDTO;

import java.util.List;
import java.util.Optional;

public interface RoleService {
    
    List<RoleDTO> getAllRoles();
    
    Optional<RoleDTO> getRoleById(Long id);
    
    Optional<RoleDTO> getRoleByName(String roleName);
    
    RoleDTO createRole(RoleDTO roleDTO);
    
    Optional<RoleDTO> updateRole(Long id, RoleDTO roleDTO);
    
    boolean deleteRole(Long id);
    
    boolean existsByRoleName(String roleName);
}
