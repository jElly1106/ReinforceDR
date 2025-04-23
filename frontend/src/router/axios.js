import axios from 'axios';
// import {ElMessage } from 'element-plus';
// import { useRouter } from 'vue-router';
// const router = useRouter();

const API = axios.create({
  baseURL: 'http://127.0.0.1:8000', 
  withCredentials: true, // 允许跨域请求发送 Cookie
  timeout: 60000, 
  headers: {
    'Content-Type': 'application/json',
  },
});


// 请求拦截器：为每个请求添加 Authorization 头（根据需要排除特定接口）
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    const excludedPaths = [
      'account/login/',
      'account/check_email_registered/',
      'account/forgot_password_send_code/',
      'account/send_verification_code/',
      'account/register/',
      'account/reset_password/'
    ]; // 不需要附加 Authorization 头的路径

    // 检查当前请求路径是否在排除列表中
    const isExcluded = excludedPaths.some((path) => config.url.includes(path));

    if (!isExcluded && token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：处理 token 过期等情况
// API.interceptors.response.use(
//   (response) => {
//     return response;
//   },
//   (error) => {
//     // 如果响应失败，根据状态码处理
//     if (error.response && error.response.status === 401) {
//       ElMessage.error('未授权，请重新登录');
//       // 可以在这里触发用户登出逻辑
//       localStorage.removeItem('userID');
//       localStorage.removeItem('access_token');
//       router.push('/'); 
//     }
//     return Promise.reject(error);
//   }
// );

export default API;
