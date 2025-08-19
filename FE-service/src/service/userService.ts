// import api from './api';
// import type { User } from '../types';


// export const userService = {
//   async getUsers(): Promise<User[]> {
//     const res = await api.get('/users');
//     return res.data;
//   },

//   async getUserById(id: string): Promise<User> {
//     const res = await api.get(`/users/${id}`);
//     return res.data;
//   },

//   async createUser(user: Partial<User>): Promise<User> {
//     const res = await api.post('/users', user);
//     return res.data;
//   },

//   async updateUser(id: string, user: Partial<User>): Promise<User> {
//     const res = await api.put(`/users/${id}`, user);
//     return res.data;
//   },

//   async deleteUser(id: string): Promise<void> {
//     await api.delete(`/users/${id}`);
//   },
// };