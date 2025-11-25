#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test module loading"""

from core.rl.state_builder import StateBuilderV2

# Initialize
builder = StateBuilderV2(
    cluster_profiles_path='data/cluster_profiles.json',
    course_structure_path='data/course_structure.json'
)

print('\n' + '='*70)
print('MODULES LOADED (Only subsections - Bài học cấp 1):')
print('='*70)
for idx, module in enumerate(builder.modules):
    print(f'{idx}. ID={module["id"]:3d} | {module["name"]}')
    print(f'   Section: {module["section"]}')
    print()

print('='*70)
print(f'Total modules: {builder.n_modules}')
print('='*70)
