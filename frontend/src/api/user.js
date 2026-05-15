import request from './index';

export const register = (data) => request.post('api/users/register', data);
export const login = (data) => request.post('api/users/login', data);
export const getUserInfo = () => request.get('api/users/me');
export const updateUser = (data) => request.put('api/users/me', data);
export const deleteUser = () => request.delete('api/users/me');