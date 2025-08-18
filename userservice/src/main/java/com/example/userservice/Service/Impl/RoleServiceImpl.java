package com.example.userservice.Service.Impl;

import com.example.userservice.DTO.RoleDTO;
import com.example.userservice.Entity.Role;
import com.example.userservice.Mapper.RoleMapper;
import com.example.userservice.Repository.RoleRepository;
import com.example.userservice.Service.RoleService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class RoleServiceImpl implements RoleService {
    
    private final RoleRepository roleRepository;
    private final RoleMapper roleMapper;
    
    @Override
    public List<RoleDTO> getAllRoles() {
        List<Role> roles = roleRepository.findAllActive();
        return roleMapper.toDTOList(roles);
    }
    
    @Override
    public Optional<RoleDTO> getRoleById(Long id) {
        return roleRepository.findByIdAndNotDeleted(id)
                .map(roleMapper::toDTO);
    }
    
    @Override
    public Optional<RoleDTO> getRoleByName(String roleName) {
        return roleRepository.findByRoleName(roleName)
                .filter(role -> role.getDeleteAt() == null)
                .map(roleMapper::toDTO);
    }
    
    @Override
    public RoleDTO createRole(RoleDTO roleDTO) {
        if (roleRepository.existsByRoleName(roleDTO.getRoleName())) {
            throw new RuntimeException("Role with name '" + roleDTO.getRoleName() + "' already exists");
        }
        
        Role role = roleMapper.toEntity(roleDTO);
        Role savedRole = roleRepository.save(role);
        return roleMapper.toDTO(savedRole);
    }
    
    @Override
    public Optional<RoleDTO> updateRole(Long id, RoleDTO roleDTO) {
        return roleRepository.findByIdAndNotDeleted(id)
                .map(existingRole -> {
                    // Check if role name is being changed and if it already exists
                    if (!existingRole.getRoleName().equals(roleDTO.getRoleName()) && 
                        roleRepository.existsByRoleName(roleDTO.getRoleName())) {
                        throw new RuntimeException("Role with name '" + roleDTO.getRoleName() + "' already exists");
                    }
                    
                    roleMapper.updateEntityFromDTO(roleDTO, existingRole);
                    Role updatedRole = roleRepository.save(existingRole);
                    return roleMapper.toDTO(updatedRole);
                });
    }
    
    @Override
    public boolean deleteRole(Long id) {
        return roleRepository.findByIdAndNotDeleted(id)
                .map(role -> {
                    role.setDeleteAt(LocalDateTime.now());
                    roleRepository.save(role);
                    return true;
                })
                .orElse(false);
    }
    
    @Override
    public boolean existsByRoleName(String roleName) {
        return roleRepository.existsByRoleName(roleName);
    }
}
