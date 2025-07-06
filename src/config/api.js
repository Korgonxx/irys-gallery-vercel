const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://irys-gallery-vercel.vercel.app/api'
  : 'http://localhost:3000/api';

export default API_BASE_URL;
