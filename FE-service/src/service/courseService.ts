// src/services/courseService.ts
import api from './api';
import type { Course } from '../types';

export const courseService = {
  async getCourses(): Promise<Course[]> {
    const res = await api.get('/courses');
    return res.data;
  },

  async getCourseById(id: string): Promise<Course> {
    const res = await api.get(`/courses/${id}`);
    return res.data;
  },
};