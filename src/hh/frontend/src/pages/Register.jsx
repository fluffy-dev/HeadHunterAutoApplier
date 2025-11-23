import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { register } from '../api/endpoints';

export default function Register() {
  const [formData, setFormData] = useState({ name: '', login: '', email: '', password: '' });
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await register(formData);
      navigate('/login');
    } catch (err) {
      alert('Registration failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <h2 className="text-center text-3xl font-extrabold text-gray-900">Register</h2>
        <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
            {['name', 'login', 'email', 'password'].map((field) => (
                <input
                    key={field}
                    type={field === 'password' ? 'password' : 'text'}
                    placeholder={field.charAt(0).toUpperCase() + field.slice(1)}
                    required
                    className="appearance-none rounded block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    value={formData[field]}
                    onChange={(e) => setFormData({ ...formData, [field]: e.target.value })}
                />
            ))}
          <button type="submit" className="w-full py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700">
            Register
          </button>
        </form>
        <div className="text-center">
             <Link to="/login" className="text-indigo-600 hover:text-indigo-500">Back to Login</Link>
        </div>
      </div>
    </div>
  );
}