package com.example.userservice.Mapper;

import com.example.userservice.DTO.RoleDTO;
import com.example.userservice.Entity.Role;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Component
public class RoleMapper {
    
    public RoleDTO toDTO(Role role) {
        if (role == null) {
            return null;
        }
        
        RoleDTO dto = new RoleDTO();
        dto.setId(role.getId());
        dto.setRoleName(role.getRoleName());
        dto.setDescription(role.getDescription());
        dto.setCreateAt(role.getCreateAt());
        dto.setUpdateAt(role.getUpdateAt());
        
        return dto;
    }
    
    public Role toEntity(RoleDTO dto) {
        if (dto == null) {
            return null;
        }
        
        Role role = new Role();
        role.setId(dto.getId());
        role.setRoleName(dto.getRoleName());
        role.setDescription(dto.getDescription());
        
        return role;
    }
    
    public List<RoleDTO> toDTOList(List<Role> roles) {
        return roles.stream()
                .map(this::toDTO)
                .collect(Collectors.toList());
    }
    
    public void updateEntityFromDTO(RoleDTO dto, Role role) {
        if (dto.getRoleName() != null) {
            role.setRoleName(dto.getRoleName());
        }
        if (dto.getDescription() != null) {
            role.setDescription(dto.getDescription());
        }
        role.setUpdateAt(LocalDateTime.now());
    }
}
