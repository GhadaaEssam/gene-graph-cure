import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'http://192.168.1.7:8000'; 

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000, // لو السيرفر مردش خلال 10 ثواني، يطلع Network Error
  headers: {
    'Content-Type': 'application/json',
  },
});

// اللمسة الاحترافية: إضافة التوكن تلقائياً في كل ريكوست بعد كدة
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const loginUser = async (email, password) => {
  try {
    const response = await api.post('/auth/login', { email, password });
    return response.data; // المفروض يرجع { status: "success", token: "...", user: {...} }
  } catch (error) {
    // التعامل مع الأخطاء بشكل مفصل
    if (error.response) {
      throw error.response.data;
    } else {
      throw new Error("Cannot connect to server. Check your Wi-Fi.");
    }
  }
};

export default api;